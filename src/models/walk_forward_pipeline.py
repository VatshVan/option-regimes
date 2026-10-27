"""
walk_forward_pipeline.py
========================
Execution engine for Stage 7 walk-forward model fitting, hyperparameter tuning,
and statistical evaluation.
Governing specifications:
- stage5_modeling_specification.md Sections 4, 5, 6, 7.
- gate_b_audit_report.md Section 9 (User-Authorized Decisions).

Key Principles:
1. Operational estimand y_t = ln(S_{t+2} / S_{t+1}) (Proposal A).
2. Label availability: Supervised models at refit origin tau_m use t <= tau_m - 2.
3. Contemporaneous HMM emissions use t <= tau_m; feature scalers are fit on the
   supervised training rows (t <= tau_m - 2).
4. Complete-case filtering: origins with valid_Q_all5 == True.
5. Partition boundary purity: targets crossing partitions are nulled.
6. Hyperparameter tuning on validation: lambda in {1e-4, 1e-3, 1e-2}, K in {2, 3}.
7. Fallback MDN check on validation.
8. Sensitivity benchmark starting 2012-07-02.
9. Statistical evaluation: NLL, CRPS, PIT, coverage, pinball, paired DM test, stationary bootstrap.
"""

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath("."))

import math
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional

from src.models.density_models import (
    RobustFeatureScaler,
    ModelB0_UnconditionalGaussian,
    ModelB1_RVLocationScaleStudentT,
    StudentTRegression,
    MixtureDensityNetwork2
)
from src.models.hmm_filter import CausalGaussianHMM
from src.models.evaluation_metrics import (
    compute_nll,
    student_t_crps,
    compute_crps_student_t_vectorized,
    gaussian_crps,
    compute_pit_values_student_t,
    compute_pit_values_gaussian,
    compute_interval_coverage,
    compute_pinball_loss,
    diebold_mariano_test,
    stationary_block_bootstrap
)
from scipy import stats

Q_COLS = ['SVIX_30d', 'QSkew_30d', 'QKurt_30d', 'ATM_IV_30d', 'TermSlope_60_30']
X_COLS = ['r_1d', 'r_5d', 'rv_5d', 'rv_20d', 'dsemi_20d', 'dd_20d']
ALL_FEAT_COLS = Q_COLS + X_COLS

def load_datasets():
    dev_path = "output/stage7_datasets/spx_stage7_operational_development_2010_2019.csv"
    val_path = "output/stage7_datasets/spx_stage7_operational_validation_2020_2021.csv"
    df_dev = pd.read_csv(dev_path)
    df_val = pd.read_csv(val_path)
    return df_dev, df_val

def build_refit_inputs(
    df_all: pd.DataFrame,
    tau_m: int,
    score_end: int,
    K_regimes: int = 2,
    start_train_idx: int = 0,
    q_cols: Optional[List[str]] = None,
    r1_pi_states: Optional[List[int]] = None,
    clip_quantiles: Optional[Tuple[float, float]] = None,
    pi_ablation: Optional[str] = None
) -> Dict[str, Any]:
    """
    Builds everything fitted at refit origin tau_m: the HMM (emissions t in [start, tau_m],
    forward-filtered through score_end - 1), the supervised training rows
    (t <= tau_m - 2, valid_supervised_pair_all5), robust scalers fitted on those rows,
    and the scaled design matrices for B2 (Q), B3 (X), B4 (QX) and R1 (QX + pi).

    Options (Step 6/7 controls; defaults reproduce the primary design):
    q_cols: option-implied columns used by B2/B4/R1 (default Q_COLS).
    r1_pi_states: filtered-probability columns appended for R1 (default: all K).
    clip_quantiles: if given, per-feature [lo, hi] quantiles of the scaled training
        features, returned as clip bounds for build_scoring_inputs (training rows are not clipped).
    pi_ablation: R1's regime inputs (research_protocol.md section 7.2), returned as 'pi_r1';
        'pi_eval' always holds the true filtered probabilities.
        None: filtered HMM probabilities.
        'shuffle': training-row pi permuted across dates; scoring-block pi
            (rows tau_m + 1 ... score_end - 1) permuted within the block; rng seeded with tau_m.
        'rv_median': pi_1 = 1(rv_20d > median rv_20d of the supervised training rows),
            pi_0 = 1 - pi_1 (K = 2 only).
    """
    q_cols = list(Q_COLS if q_cols is None else q_cols)
    r1_pi_states = list(range(K_regimes) if r1_pi_states is None else r1_pi_states)
    # 1. HMM Estimation Window: t in [start_train_idx, tau_m]
    hmm_indices = np.arange(start_train_idx, tau_m + 1)

    # Standardize HMM emissions
    r_hist = df_all['r_1d'].iloc[hmm_indices].values
    rv_hist = df_all['rv_20d'].iloc[hmm_indices].values
    r_mean, r_std = float(np.mean(r_hist)), float(np.std(r_hist, ddof=1))
    rv_mean, rv_std = float(np.mean(rv_hist)), float(np.std(rv_hist, ddof=1))

    # Emission vector across all data up to score_end
    eval_indices = np.arange(start_train_idx, score_end)
    r_all_eval = df_all['r_1d'].iloc[eval_indices].values
    rv_all_eval = df_all['rv_20d'].iloc[eval_indices].values
    Y_eval = np.column_stack([(r_all_eval - r_mean) / r_std, (rv_all_eval - rv_mean) / rv_std])
    Y_train = Y_eval[:len(hmm_indices)]

    # Fit HMM
    hmm = CausalGaussianHMM(n_states=K_regimes, max_iter=60, random_state=42)
    hmm.fit(Y_train)

    # Forward filter across eval_indices causally
    pi_eval = hmm.forward_filter(Y_eval)

    # 2. Supervised Training Set: t in [start_train_idx, tau_m - 2] with valid_supervised_pair_all5 == True
    sup_tau = tau_m - 2
    sup_cand_indices = np.arange(start_train_idx, sup_tau + 1)
    sup_valid_mask = df_all['valid_supervised_pair_all5'].iloc[sup_cand_indices].values
    train_sup_indices = sup_cand_indices[sup_valid_mask]

    # Extract features and targets for training
    y_train = df_all['target_y_next2'].iloc[train_sup_indices].values
    rv_train = df_all['rv_20d'].iloc[train_sup_indices].values
    Q_train_raw = df_all[q_cols].iloc[train_sup_indices].values
    X_train_raw = df_all[X_COLS].iloc[train_sup_indices].values

    # Scalers fit strictly on the supervised training rows (t <= tau_m - 2)
    scaler_Q = RobustFeatureScaler().fit(Q_train_raw)
    scaler_X = RobustFeatureScaler().fit(X_train_raw)

    Q_train_scaled = scaler_Q.transform(Q_train_raw)
    X_train_scaled = scaler_X.transform(X_train_raw)
    QX_train_scaled = np.column_stack([Q_train_scaled, X_train_scaled])

    # pi_t for training: align causal pi (or its ablation) with the supervised rows
    train_pi_offsets = train_sup_indices - start_train_idx
    if pi_ablation is None:
        pi_r1 = pi_eval
    elif pi_ablation == 'shuffle':
        rng = np.random.default_rng(tau_m)
        pi_r1 = pi_eval.copy()
        pi_r1[train_pi_offsets] = pi_eval[rng.permutation(train_pi_offsets)]
        score_offsets = np.arange(tau_m + 1, score_end) - start_train_idx
        if len(score_offsets):
            pi_r1[score_offsets] = pi_eval[rng.permutation(score_offsets)]
    elif pi_ablation == 'rv_median':
        assert K_regimes == 2, "rv_median ablation is defined for K = 2"
        high = (rv_all_eval > np.median(rv_train)).astype(np.float64)
        pi_r1 = np.column_stack([1.0 - high, high])
    else:
        raise ValueError(f"unknown pi_ablation {pi_ablation!r}")
    pi_train = pi_r1[train_pi_offsets][:, r1_pi_states]
    QXpi_train = np.column_stack([QX_train_scaled, pi_train])

    clip_bounds = None
    if clip_quantiles is not None:
        lo, hi = clip_quantiles
        clip_bounds = {
            'Q': (np.quantile(Q_train_scaled, lo, axis=0), np.quantile(Q_train_scaled, hi, axis=0)),
            'X': (np.quantile(X_train_scaled, lo, axis=0), np.quantile(X_train_scaled, hi, axis=0)),
        }

    return {
        'q_cols': q_cols,
        'r1_pi_states': r1_pi_states,
        'clip_bounds': clip_bounds,
        'start_train_idx': start_train_idx,
        'hmm': hmm,
        'pi_eval': pi_eval,
        'pi_ablation': pi_ablation,
        'pi_r1': pi_r1,
        'hmm_indices': hmm_indices,
        'sup_tau': sup_tau,
        'train_sup_indices': train_sup_indices,
        'y_train': y_train,
        'rv_train': rv_train,
        'scaler_Q': scaler_Q,
        'scaler_X': scaler_X,
        'Q_train_scaled': Q_train_scaled,
        'X_train_scaled': X_train_scaled,
        'QX_train_scaled': QX_train_scaled,
        'QXpi_train': QXpi_train
    }

def build_scoring_inputs(df_all: pd.DataFrame, refit: Dict[str, Any], score_indices: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Scaled scoring-time design matrices for B2/B3/B4/R1 using the frozen refit scalers,
    the refit's Q columns and pi states, and (if set) its training-quantile clip bounds.
    """
    Q = refit['scaler_Q'].transform(df_all[refit['q_cols']].iloc[score_indices].values)
    X = refit['scaler_X'].transform(df_all[X_COLS].iloc[score_indices].values)
    n_clipped = 0
    if refit['clip_bounds'] is not None:
        (q_lo, q_hi), (x_lo, x_hi) = refit['clip_bounds']['Q'], refit['clip_bounds']['X']
        n_clipped = int(np.sum((Q < q_lo) | (Q > q_hi)) + np.sum((X < x_lo) | (X > x_hi)))
        Q, X = np.clip(Q, q_lo, q_hi), np.clip(X, x_lo, x_hi)
    QX = np.column_stack([Q, X])
    pi = refit['pi_r1'][np.asarray(score_indices) - refit['start_train_idx']][:, refit['r1_pi_states']]
    return {'Q': Q, 'X': X, 'QX': QX, 'QXpi': np.column_stack([QX, pi]), 'n_clipped': n_clipped}

def run_walk_forward(
    df_all: pd.DataFrame,
    val_start_idx: int,
    K_regimes: int = 2,
    lambda_reg: float = 1e-3,
    start_train_idx: int = 0,
    block_size: int = 21,
    include_mdn: bool = False,
    q_cols: Optional[List[str]] = None,
    r1_pi_states: Optional[List[int]] = None,
    clip_quantiles: Optional[Tuple[float, float]] = None,
    pi_ablation: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes expanding-window walk-forward refits across the validation partition.
    df_all: combined DataFrame (Dev + Val)
    val_start_idx: row index where Validation begins (2516)
    start_train_idx: row index where training begins (0 for full, 629 for mid-2012 sensitivity)
    q_cols, r1_pi_states, clip_quantiles, pi_ablation: Step 6/7 controls, see build_refit_inputs.
    """
    N_total = len(df_all)
    val_end_idx = N_total
    
    # Validation scoring mask
    val_mask = np.zeros(N_total, dtype=bool)
    val_mask[val_start_idx:val_end_idx] = df_all['valid_supervised_pair_all5'].iloc[val_start_idx:val_end_idx].values
    val_indices = np.where(val_mask)[0]
    
    # Storage for out-of-sample predictions
    # Models: B0, B1, B2, B3, B4, R1 (and optionally MDN)
    model_names = ['B0', 'B1', 'B2', 'B3', 'B4', 'R1']
    if include_mdn:
        model_names.append('B4_MDN')
        
    preds = {m: {'mu': np.full(N_total, np.nan), 'sigma': np.full(N_total, np.nan), 'nu': np.full(N_total, np.nan), 'log_p': np.full(N_total, np.nan)} for m in model_names}
    if include_mdn:
        preds['B4_MDN'] = {'log_p': np.full(N_total, np.nan)}
        
    filtered_pi_all = np.full((N_total, K_regimes), np.nan)
    
    # Walk-forward refit origins
    refit_origins = list(range(val_start_idx - 1, val_end_idx - 1, block_size))
    # Ensure initial refit is at val_start_idx - 1 (end of 2019)
    if refit_origins[0] != val_start_idx - 1:
        refit_origins.insert(0, val_start_idx - 1)
        
    print(f"\n--- Walk-Forward Run: K={K_regimes}, lambda={lambda_reg}, start_idx={start_train_idx} ---")
    print(f"Total refit blocks: {len(refit_origins)}")
    
    refit_diagnostics = []
    
    for block_num, tau_m in enumerate(refit_origins):
        # Determine scoring window for this block
        score_start = max(val_start_idx, tau_m + 1)
        score_end = min(val_end_idx, tau_m + 1 + block_size)
        if score_start >= score_end:
            continue
            
        refit = build_refit_inputs(df_all, tau_m, score_end, K_regimes, start_train_idx,
                                   q_cols=q_cols, r1_pi_states=r1_pi_states, clip_quantiles=clip_quantiles,
                                   pi_ablation=pi_ablation)
        hmm, pi_eval, hmm_indices = refit['hmm'], refit['pi_eval'], refit['hmm_indices']
        sup_tau, train_sup_indices = refit['sup_tau'], refit['train_sup_indices']
        y_train, rv_train = refit['y_train'], refit['rv_train']
        Q_train_scaled, X_train_scaled = refit['Q_train_scaled'], refit['X_train_scaled']
        QX_train_scaled, QXpi_train = refit['QX_train_scaled'], refit['QXpi_train']

        # Store filtered pi for the scoring window
        window_offset_start = score_start - start_train_idx
        window_offset_end = score_end - start_train_idx
        filtered_pi_all[score_start:score_end] = pi_eval[window_offset_start:window_offset_end]

        # 3. Fit Models
        # Model B0: Unconditional Gaussian
        m_b0 = ModelB0_UnconditionalGaussian().fit(y_train)
        
        # Model B1: Trailing RV Location-Scale Student-t
        m_b1 = ModelB1_RVLocationScaleStudentT().fit(rv_train, y_train)
        
        # Model B2: Q-Only Student-t Regression (d=5 in the primary design)
        m_b2 = StudentTRegression(in_features=Q_train_scaled.shape[1], l2_reg=lambda_reg).fit(Q_train_scaled, y_train)

        # Model B3: X-Only Student-t Regression (d=6)
        m_b3 = StudentTRegression(in_features=X_train_scaled.shape[1], l2_reg=lambda_reg).fit(X_train_scaled, y_train)

        # Model B4: Combined Non-Regime Primary Baseline (d=11 in the primary design)
        m_b4 = StudentTRegression(in_features=QX_train_scaled.shape[1], l2_reg=lambda_reg).fit(QX_train_scaled, y_train)

        # Model R1: Matched Latent Regime Challenger (d=11+K in the primary design)
        m_r1 = StudentTRegression(in_features=QXpi_train.shape[1], l2_reg=lambda_reg).fit(QXpi_train, y_train)

        # Optional MDN check
        m_mdn = None
        if include_mdn:
            m_mdn = MixtureDensityNetwork2(in_features=QX_train_scaled.shape[1], l2_reg=lambda_reg).fit(QX_train_scaled, y_train)

        # 4. Out-of-Sample Prediction for Block [score_start, score_end)
        score_indices = np.arange(score_start, score_end)
        rv_score = df_all['rv_20d'].iloc[score_indices].values
        y_score = df_all['target_y_next2'].iloc[score_indices].values

        # Transform features using frozen scalers (and optional clip bounds) from tau_m
        score_inputs = build_scoring_inputs(df_all, refit, score_indices)
        Q_score_scaled, X_score_scaled = score_inputs['Q'], score_inputs['X']
        QX_score_scaled, QXpi_score = score_inputs['QX'], score_inputs['QXpi']
        
        # Generate predictions
        # B0
        mu_b0, sig_b0 = m_b0.predict(len(score_indices))
        preds['B0']['mu'][score_indices] = mu_b0
        preds['B0']['sigma'][score_indices] = sig_b0
        preds['B0']['log_p'][score_indices] = m_b0.log_density(y_score)
        
        # B1
        mu_b1, sig_b1, nu_b1 = m_b1.predict(rv_score)
        preds['B1']['mu'][score_indices] = mu_b1
        preds['B1']['sigma'][score_indices] = sig_b1
        preds['B1']['nu'][score_indices] = nu_b1
        preds['B1']['log_p'][score_indices] = m_b1.log_density(rv_score, y_score)
        
        # B2
        mu_b2, sig_b2, nu_b2 = m_b2.predict(Q_score_scaled)
        preds['B2']['mu'][score_indices] = mu_b2
        preds['B2']['sigma'][score_indices] = sig_b2
        preds['B2']['nu'][score_indices] = nu_b2
        preds['B2']['log_p'][score_indices] = m_b2.log_density(Q_score_scaled, y_score)
        
        # B3
        mu_b3, sig_b3, nu_b3 = m_b3.predict(X_score_scaled)
        preds['B3']['mu'][score_indices] = mu_b3
        preds['B3']['sigma'][score_indices] = sig_b3
        preds['B3']['nu'][score_indices] = nu_b3
        preds['B3']['log_p'][score_indices] = m_b3.log_density(X_score_scaled, y_score)
        
        # B4
        mu_b4, sig_b4, nu_b4 = m_b4.predict(QX_score_scaled)
        preds['B4']['mu'][score_indices] = mu_b4
        preds['B4']['sigma'][score_indices] = sig_b4
        preds['B4']['nu'][score_indices] = nu_b4
        preds['B4']['log_p'][score_indices] = m_b4.log_density(QX_score_scaled, y_score)
        
        # R1
        mu_r1, sig_r1, nu_r1 = m_r1.predict(QXpi_score)
        preds['R1']['mu'][score_indices] = mu_r1
        preds['R1']['sigma'][score_indices] = sig_r1
        preds['R1']['nu'][score_indices] = nu_r1
        preds['R1']['log_p'][score_indices] = m_r1.log_density(QXpi_score, y_score)
        
        # MDN
        if include_mdn and m_mdn is not None:
            preds['B4_MDN']['log_p'][score_indices] = m_mdn.log_density(QX_score_scaled, y_score)
            
        # HMM Diagnostics for this refit block
        dwells = hmm.compute_dwell_times()
        trans = hmm.trans_mat
        diags = np.diag(trans)
        pi_train = pi_eval[:len(hmm_indices)]
        occ_argmax = hmm.compute_occupancies(pi_train)
        occ_mean = np.mean(pi_train, axis=0)
        
        dwell_pass = bool(np.all(dwells >= 5.0))
        occ_pass = bool(np.all(occ_argmax >= 0.05))
        
        refit_diagnostics.append({
            'block': block_num,
            'refit_origin_tau': int(tau_m),
            'refit_date': str(df_all['date'].iloc[tau_m]),
            'train_window': {
                'start_idx': int(start_train_idx),
                'start_date': str(df_all['date'].iloc[start_train_idx]),
                'end_idx': int(tau_m),
                'end_date': str(df_all['date'].iloc[tau_m]),
                'n_sessions_hmm': int(len(hmm_indices)),
                'sup_cutoff_tau': int(sup_tau),
                'sup_cutoff_date': str(df_all['date'].iloc[sup_tau]),
                'n_train_sup': int(len(train_sup_indices))
            },
            'scoring_window': {
                'score_start_idx': int(score_start),
                'score_end_idx': int(score_end),
                'score_dates': f"{df_all['date'].iloc[score_start]} to {df_all['date'].iloc[score_end - 1]}",
                'n_scored': int(score_end - score_start)
            },
            'n_scoring_feature_values_clipped': int(score_inputs['n_clipped']),
            'hmm_n_iter': int(hmm.n_iter_),
            'hmm_converged': bool(hmm.converged_),
            'hmm_final_log_lik': float(hmm.log_lik_history_[-1]),
            'hmm_transition_matrix': trans.tolist(),
            'hmm_diagonal_probabilities': [float(d) for d in diags],
            'hmm_expected_dwell_times': [float(d) for d in dwells],
            'hmm_state_occupancies_train_argmax': [float(o) for o in occ_argmax],
            'hmm_state_occupancies_train_mean': [float(o) for o in occ_mean],
            'dwell_time_constraint_pass': dwell_pass,
            'occupancy_constraint_pass': occ_pass,
            'all_constraints_pass': bool(dwell_pass and occ_pass),
            'fit_reports': {
                'B1': m_b1.fit_report_,
                'B2': m_b2.fit_report_,
                'B3': m_b3.fit_report_,
                'B4': m_b4.fit_report_,
                'R1': m_r1.fit_report_
            }
        })
        
    # Evaluate performance on the 494 complete-case validation scoring rows
    val_y = df_all['target_y_next2'].iloc[val_indices].values
    val_dates = df_all['date'].iloc[val_indices].values
    
    val_metrics = {}
    for m in model_names:
        log_p = preds[m]['log_p'][val_indices]
        nll = compute_nll(log_p)
        
        metrics = {'nll': nll}
        
        # CRPS, PIT, Interval coverage, Pinball
        if m == 'B0':
            mu = preds[m]['mu'][val_indices]
            sigma = preds[m]['sigma'][val_indices]
            crps_vals = [gaussian_crps(val_y[i], mu[i], sigma[i]) for i in range(len(val_y))]
            pit_vals = compute_pit_values_gaussian(val_y, mu, sigma)
            ks_res = stats.kstest(pit_vals, 'uniform')
            
            # Coverage
            cov_res = {}
            for cov in [0.50, 0.80, 0.95]:
                alpha = 1.0 - cov
                low = stats.norm.ppf(alpha / 2.0, loc=mu, scale=sigma)
                high = stats.norm.ppf(1.0 - alpha / 2.0, loc=mu, scale=sigma)
                cov_res[f"coverage_{int(cov*100)}"] = float(np.mean((val_y >= low) & (val_y <= high)))
                
            # Pinball
            pinball_res = {}
            for alpha in [0.01, 0.05, 0.10, 0.90, 0.95, 0.99]:
                q = stats.norm.ppf(alpha, loc=mu, scale=sigma)
                pinball_res[f"pinball_{int(alpha*100):02d}"] = float(np.mean((val_y - q) * (alpha - (val_y < q).astype(float))))
                
            metrics.update({
                'crps': float(np.mean(crps_vals)),
                'pit_ks_stat': float(ks_res.statistic),
                'pit_ks_pvalue': float(ks_res.pvalue),
                'coverages': cov_res,
                'pinball': pinball_res
            })
            
        elif m in ['B1', 'B2', 'B3', 'B4', 'R1']:
            mu = preds[m]['mu'][val_indices]
            sigma = preds[m]['sigma'][val_indices]
            nu = preds[m]['nu'][val_indices]
            
            crps_vals = compute_crps_student_t_vectorized(val_y, mu, sigma, nu)
            pit_vals = compute_pit_values_student_t(val_y, mu, sigma, nu)
            ks_res = stats.kstest(pit_vals, 'uniform')
            cov_res = compute_interval_coverage(val_y, mu, sigma, nu)
            pinball_res = compute_pinball_loss(val_y, mu, sigma, nu)
            
            metrics.update({
                'crps': float(np.mean(crps_vals)),
                'pit_ks_stat': float(ks_res.statistic),
                'pit_ks_pvalue': float(ks_res.pvalue),
                'coverages': cov_res,
                'pinball': pinball_res,
                'mean_scale': float(np.mean(sigma)),
                'mean_nu': float(np.mean(nu))
            })
            
        val_metrics[m] = metrics
        print(f"Model {m:6s} -> Val NLL: {nll:.4f} nats, CRPS: {metrics.get('crps', np.nan):.6f}")
        
    # Paired DM test and bootstrap CI between B4 and R1
    logp_b4 = preds['B4']['log_p'][val_indices]
    logp_r1 = preds['R1']['log_p'][val_indices]
    d_loss = logp_r1 - logp_b4  # Positive d means R1 has higher log-likelihood (lower loss)
    
    dm_test = diebold_mariano_test(d_loss)
    boot_res = stationary_block_bootstrap(d_loss, n_boot=2000, expected_block_len=5, seed=42)
    
    print(f"\nPaired Test (R1 vs B4):")
    print(f"Mean Log-Score Differential: {dm_test['mean_differential']:+.6f} nats/session")
    print(f"Diebold-Mariano Stat: {dm_test['dm_stat']:.4f} (p-value one-sided: {dm_test['p_value_one_sided']:.4f})")
    print(f"Stationary Block Bootstrap 95% CI: [{boot_res['ci_95_lower']:+.6f}, {boot_res['ci_95_upper']:+.6f}] (Excludes Zero: {boot_res['excludes_zero']})")
    
    # HMM occupancies and dwell times on validation
    val_pi = filtered_pi_all[val_indices]
    val_argmax = np.argmax(val_pi, axis=1)
    occupancies = [float(np.mean(val_argmax == k)) for k in range(K_regimes)]
    
    return {
        'val_metrics': val_metrics,
        'dm_test': dm_test,
        'bootstrap': boot_res,
        'occupancies': occupancies,
        'refit_diagnostics': refit_diagnostics,
        'preds': preds,
        'val_indices': val_indices,
        'filtered_pi_all': filtered_pi_all
    }

def fit_insample_development(df_dev: pd.DataFrame, lambda_reg: float = 1e-3, K_regimes: int = 2) -> Dict[str, Any]:
    """
    Fits models on Development data and evaluates in-sample metrics on the 2,231 usable pairs.
    """
    sup_mask = df_dev['valid_supervised_pair_all5'].values
    train_indices = np.where(sup_mask)[0]
    
    y = df_dev['target_y_next2'].iloc[train_indices].values
    rv = df_dev['rv_20d'].iloc[train_indices].values
    Q_raw = df_dev[Q_COLS].iloc[train_indices].values
    X_raw = df_dev[X_COLS].iloc[train_indices].values
    
    scaler_Q = RobustFeatureScaler().fit(Q_raw)
    scaler_X = RobustFeatureScaler().fit(X_raw)
    Q_scaled = scaler_Q.transform(Q_raw)
    X_scaled = scaler_X.transform(X_raw)
    QX_scaled = np.column_stack([Q_scaled, X_scaled])
    
    # HMM on all development emissions
    r_hist = df_dev['r_1d'].values
    rv_hist = df_dev['rv_20d'].values
    r_mean, r_std = float(np.mean(r_hist)), float(np.std(r_hist, ddof=1))
    rv_mean, rv_std = float(np.mean(rv_hist)), float(np.std(rv_hist, ddof=1))
    Y_dev = np.column_stack([(r_hist - r_mean) / r_std, (rv_hist - rv_mean) / rv_std])
    
    hmm = CausalGaussianHMM(n_states=K_regimes, max_iter=60, random_state=42)
    hmm.fit(Y_dev)
    pi_filtered = hmm.forward_filter(Y_dev)[train_indices]
    QXpi_scaled = np.column_stack([QX_scaled, pi_filtered])
    
    # Fit models
    m_b0 = ModelB0_UnconditionalGaussian().fit(y)
    m_b1 = ModelB1_RVLocationScaleStudentT().fit(rv, y)
    m_b2 = StudentTRegression(in_features=5, l2_reg=lambda_reg).fit(Q_scaled, y)
    m_b3 = StudentTRegression(in_features=6, l2_reg=lambda_reg).fit(X_scaled, y)
    m_b4 = StudentTRegression(in_features=11, l2_reg=lambda_reg).fit(QX_scaled, y)
    m_r1 = StudentTRegression(in_features=11 + K_regimes, l2_reg=lambda_reg).fit(QXpi_scaled, y)
    
    # In-sample log-likelihoods
    insample_metrics = {}
    preds = {}
    
    # B0
    logp_b0 = m_b0.log_density(y)
    insample_metrics['B0'] = {'nll': compute_nll(logp_b0)}
    preds['B0'] = logp_b0
    
    # B1
    logp_b1 = m_b1.log_density(rv, y)
    insample_metrics['B1'] = {'nll': compute_nll(logp_b1)}
    preds['B1'] = logp_b1
    
    # B2
    logp_b2 = m_b2.log_density(Q_scaled, y)
    insample_metrics['B2'] = {'nll': compute_nll(logp_b2)}
    preds['B2'] = logp_b2
    
    # B3
    logp_b3 = m_b3.log_density(X_scaled, y)
    insample_metrics['B3'] = {'nll': compute_nll(logp_b3)}
    preds['B3'] = logp_b3
    
    # B4
    logp_b4 = m_b4.log_density(QX_scaled, y)
    insample_metrics['B4'] = {'nll': compute_nll(logp_b4)}
    preds['B4'] = logp_b4
    
    # R1
    logp_r1 = m_r1.log_density(QXpi_scaled, y)
    insample_metrics['R1'] = {'nll': compute_nll(logp_r1)}
    preds['R1'] = logp_r1
    
    d_loss = logp_r1 - logp_b4
    dm_res = diebold_mariano_test(d_loss)
    
    print("\n--- In-Sample Development Performance (2010–2019, N=2,231 pairs) ---")
    for m, met in insample_metrics.items():
        print(f"Model {m:6s} -> In-Sample NLL: {met['nll']:.4f} nats")
    print(f"In-Sample R1 vs B4 differential: {dm_res['mean_differential']:+.6f} nats, DM Stat: {dm_res['dm_stat']:.4f}")
    
    return {
        'insample_metrics': insample_metrics,
        'dm_test': dm_res,
        'train_indices': train_indices,
        'fit_reports': {
            'B1': m_b1.fit_report_,
            'B2': m_b2.fit_report_,
            'B3': m_b3.fit_report_,
            'B4': m_b4.fit_report_,
            'R1': m_r1.fit_report_
        }
    }
