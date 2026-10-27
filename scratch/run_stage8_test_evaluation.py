"""
run_stage8_test_evaluation.py
=============================
Executes Stage 8: Gate D final held-out test evaluation on the SPX 2022-2023 partition.

Strictly follows frozen Stage 7 specifications:
- Proposal A target: y_t = ln(S_{t+2} / S_{t+1})
- Primary comparator: R1 (d=13) versus B4 (d=11)
- K = 2 latent regimes (Causal Gaussian HMM)
- lambda = 0.01 L2 regularization penalty
- Location-scale Student-t density regression
- 21-session expanding walk-forward refit schedule
- Supervised training at refit origin tau restricted to t <= tau - 2
- Contemporaneous HMM emissions and scalers use t <= tau
- Exact closed-form analytical Student-t CRPS (Jordan, Krüger, Lerch 2019)
- Both 500-session unbreached set (excluding 2022-01-03) and 501-session full set evaluated
"""

import os
import sys
import json
import math
import time
import numpy as np
import pandas as pd
from scipy import stats, integrate

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

from src.models.density_models import (
    RobustFeatureScaler,
    ModelB0_UnconditionalGaussian,
    ModelB1_RVLocationScaleStudentT,
    StudentTRegression
)
from src.models.walk_forward_pipeline import Q_COLS, X_COLS
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

def load_all_three_partitions():
    """Loads Development, Validation, and Test datasets using frozen Stage 7 operational definitions."""
    dev_path = "output/stage7_datasets/spx_stage7_operational_development_2010_2019.csv"
    val_path = "output/stage7_datasets/spx_stage7_operational_validation_2020_2021.csv"
    test_path = "output/stage8_test/spx_features_test_2022_2023.csv"
    
    df_dev = pd.read_csv(dev_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)
    
    print(f"Development: {len(df_dev)} sessions, {df_dev['valid_supervised_pair_all5'].sum()} usable pairs")
    print(f"Validation:  {len(df_val)} sessions, {df_val['valid_supervised_pair_all5'].sum()} usable pairs")
    print(f"Test:        {len(df_test)} sessions, {df_test['valid_supervised_pair_all5'].sum()} usable pairs")
    
    return df_dev, df_val, df_test

def run_test_walk_forward(df_all, test_start_idx, K_regimes=2, lambda_reg=0.01, block_size=21, exclude_origin_from_training=None):
    """
    Executes expanding-window walk-forward evaluation across the held-out Test partition.
    
    Parameters:
    -----------
    df_all : pd.DataFrame
        Concatenated Development, Validation, and Test datasets.
    test_start_idx : int
        Index in df_all where the Test partition begins (session 2022-01-03).
    K_regimes : int
        Number of latent regimes for HMM (default K=2).
    lambda_reg : float
        Ridge regularization penalty for Student-t regression (default lambda=0.01).
    block_size : int
        Refit cadence in sessions (default 21 sessions).
    exclude_origin_from_training : str, optional
        Date string (e.g. '2022-01-03') to exclude from supervised training pairs at all refits.
    """
    N_total = len(df_all)
    test_end_idx = N_total
    
    model_names = ['B0', 'B1', 'B2', 'B3', 'B4', 'R1']
    preds = {m: {'mu': np.full(N_total, np.nan), 'sigma': np.full(N_total, np.nan), 'nu': np.full(N_total, np.nan), 'log_p': np.full(N_total, np.nan)} for m in model_names}
    filtered_pi_all = np.full((N_total, K_regimes), np.nan)
    
    refit_origins = list(range(test_start_idx - 1, test_end_idx - 1, block_size))
    if refit_origins[0] != test_start_idx - 1:
        refit_origins.insert(0, test_start_idx - 1)
        
    print(f"\n================================================================================")
    print(f"WALK-FORWARD TEST ENGINE: K={K_regimes}, lambda={lambda_reg}, Refits={len(refit_origins)}")
    print(f"Training exclusion: {exclude_origin_from_training if exclude_origin_from_training else 'None (Standard Prequential)'}")
    print(f"Test scoring sessions: indices {test_start_idx} to {test_end_idx - 1} ({test_end_idx - test_start_idx} sessions)")
    print(f"================================================================================")
    
    refit_diagnostics = []
    t0_wf = time.time()
    
    for block_num, tau_m in enumerate(refit_origins):
        score_start = max(test_start_idx, tau_m + 1)
        score_end = min(test_end_idx, tau_m + 1 + block_size)
        if score_start >= score_end:
            continue
            
        # 1. HMM Estimation & Feature Scaler Window: t in [0, tau_m]
        hmm_indices = np.arange(0, tau_m + 1)
        r_hist = df_all['r_1d'].iloc[hmm_indices].values
        rv_hist = df_all['rv_20d'].iloc[hmm_indices].values
        r_mean, r_std = float(np.mean(r_hist)), float(np.std(r_hist, ddof=1))
        rv_mean, rv_std = float(np.mean(rv_hist)), float(np.std(rv_hist, ddof=1))
        
        eval_indices = np.arange(0, score_end)
        r_all_eval = df_all['r_1d'].iloc[eval_indices].values
        rv_all_eval = df_all['rv_20d'].iloc[eval_indices].values
        Y_eval = np.column_stack([(r_all_eval - r_mean) / r_std, (rv_all_eval - rv_mean) / rv_std])
        Y_train = Y_eval[:len(hmm_indices)]
        
        hmm = CausalGaussianHMM(n_states=K_regimes, max_iter=60, random_state=42)
        hmm.fit(Y_train)
        
        pi_eval = hmm.forward_filter(Y_eval)
        filtered_pi_all[score_start:score_end] = pi_eval[score_start:score_end]
        
        # 2. Supervised Training Set: t in [0, tau_m - 2] with valid_supervised_pair_all5 == True
        sup_tau = tau_m - 2
        sup_cand_indices = np.arange(0, sup_tau + 1)
        sup_valid_mask = df_all['valid_supervised_pair_all5'].iloc[sup_cand_indices].values
        if exclude_origin_from_training is not None:
            sup_valid_mask = sup_valid_mask & (df_all['date'].iloc[sup_cand_indices].values != exclude_origin_from_training)
        train_sup_indices = sup_cand_indices[sup_valid_mask]
        
        y_train = df_all['target_y_next2'].iloc[train_sup_indices].values
        rv_train = df_all['rv_20d'].iloc[train_sup_indices].values
        Q_train_raw = df_all[Q_COLS].iloc[train_sup_indices].values
        X_train_raw = df_all[X_COLS].iloc[train_sup_indices].values
        
        scaler_Q = RobustFeatureScaler().fit(Q_train_raw)
        scaler_X = RobustFeatureScaler().fit(X_train_raw)
        
        Q_train_scaled = scaler_Q.transform(Q_train_raw)
        X_train_scaled = scaler_X.transform(X_train_raw)
        QX_train_scaled = np.column_stack([Q_train_scaled, X_train_scaled])
        
        pi_train = pi_eval[train_sup_indices]
        QXpi_train = np.column_stack([QX_train_scaled, pi_train])
        
        # 3. Fit Models
        m_b0 = ModelB0_UnconditionalGaussian().fit(y_train)
        m_b1 = ModelB1_RVLocationScaleStudentT().fit(rv_train, y_train)
        m_b2 = StudentTRegression(in_features=5, l2_reg=lambda_reg).fit(Q_train_scaled, y_train)
        m_b3 = StudentTRegression(in_features=6, l2_reg=lambda_reg).fit(X_train_scaled, y_train)
        m_b4 = StudentTRegression(in_features=11, l2_reg=lambda_reg).fit(QX_train_scaled, y_train)
        m_r1 = StudentTRegression(in_features=11 + K_regimes, l2_reg=lambda_reg).fit(QXpi_train, y_train)
        
        # 4. Out-of-Sample Prediction for Block [score_start, score_end)
        score_indices = np.arange(score_start, score_end)
        rv_score = df_all['rv_20d'].iloc[score_indices].values
        y_score = df_all['target_y_next2'].iloc[score_indices].values
        
        Q_score_raw = df_all[Q_COLS].iloc[score_indices].values
        X_score_raw = df_all[X_COLS].iloc[score_indices].values
        Q_score_scaled = scaler_Q.transform(Q_score_raw)
        X_score_scaled = scaler_X.transform(X_score_raw)
        QX_score_scaled = np.column_stack([Q_score_scaled, X_score_scaled])
        
        pi_score = filtered_pi_all[score_indices]
        QXpi_score = np.column_stack([QX_score_scaled, pi_score])
        
        # Predictions
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
        
        # HMM Diagnostics
        dwells = hmm.compute_dwell_times()
        trans = hmm.trans_mat
        diags = np.diag(trans)
        pi_train_hmm = pi_eval[:len(hmm_indices)]
        occ_argmax = hmm.compute_occupancies(pi_train_hmm)
        occ_mean = np.mean(pi_train_hmm, axis=0)
        
        dwell_pass = bool(np.all(dwells >= 5.0))
        occ_pass = bool(np.all(occ_argmax >= 0.05))
        
        refit_diagnostics.append({
            'block': block_num,
            'refit_origin_tau': int(tau_m),
            'refit_date': str(df_all['date'].iloc[tau_m]),
            'train_window': {
                'start_idx': 0,
                'start_date': str(df_all['date'].iloc[0]),
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
            'hmm_transition_matrix': trans.tolist(),
            'hmm_diagonal_probabilities': [float(d) for d in diags],
            'hmm_expected_dwell_times': [float(d) for d in dwells],
            'hmm_state_occupancies_train_argmax': [float(o) for o in occ_argmax],
            'hmm_state_occupancies_train_mean': [float(o) for o in occ_mean],
            'dwell_time_constraint_pass': dwell_pass,
            'occupancy_constraint_pass': occ_pass,
            'all_constraints_pass': bool(dwell_pass and occ_pass)
        })
        
        if block_num in [0, 5, 10, 15, 20, 23]:
            print(f"Block {block_num:2d} ({df_all['date'].iloc[tau_m]}): n_sup={len(train_sup_indices)}, Dwells={[round(d, 1) for d in dwells]}, Occ={[round(o, 3) for o in occ_argmax]}")
            
    print(f"\nWalk-forward engine finished in {time.time() - t0_wf:.1f}s")
    
    return {
        'preds': preds,
        'filtered_pi_all': filtered_pi_all,
        'refit_diagnostics': refit_diagnostics
    }

def evaluate_subset(df_all, preds, filtered_pi_all, eval_indices, label="Test"):
    """Evaluates comprehensive metrics on a subset of indices."""
    model_names = ['B0', 'B1', 'B2', 'B3', 'B4', 'R1']
    y_eval = df_all['target_y_next2'].iloc[eval_indices].values
    
    metrics_summary = {}
    for m in model_names:
        log_p = preds[m]['log_p'][eval_indices]
        nll = compute_nll(log_p)
        mu = preds[m]['mu'][eval_indices]
        sigma = preds[m]['sigma'][eval_indices]
        
        m_dict = {'nll': nll}
        if m == 'B0':
            crps_vals = [gaussian_crps(y_eval[i], mu[i], sigma[i]) for i in range(len(y_eval))]
            pit_vals = compute_pit_values_gaussian(y_eval, mu, sigma)
            ks_res = stats.kstest(pit_vals, 'uniform')
            cov_res = {}
            for cov in [0.50, 0.80, 0.95]:
                alpha = 1.0 - cov
                low = stats.norm.ppf(alpha / 2.0, loc=mu, scale=sigma)
                high = stats.norm.ppf(1.0 - alpha / 2.0, loc=mu, scale=sigma)
                cov_res[f"coverage_{int(cov*100)}"] = float(np.mean((y_eval >= low) & (y_eval <= high)))
            pinball_res = {}
            for alpha in [0.01, 0.05, 0.10, 0.90, 0.95, 0.99]:
                q = stats.norm.ppf(alpha, loc=mu, scale=sigma)
                pinball_res[f"pinball_{int(alpha*100):02d}"] = float(np.mean((y_eval - q) * (alpha - (y_eval < q).astype(float))))
            m_dict.update({
                'crps': float(np.mean(crps_vals)),
                'pit_ks_stat': float(ks_res.statistic),
                'pit_ks_pvalue': float(ks_res.pvalue),
                'coverages': cov_res,
                'pinball': pinball_res
            })
        else:
            nu = preds[m]['nu'][eval_indices]
            crps_vals = compute_crps_student_t_vectorized(y_eval, mu, sigma, nu)
            pit_vals = compute_pit_values_student_t(y_eval, mu, sigma, nu)
            ks_res = stats.kstest(pit_vals, 'uniform')
            cov_res = compute_interval_coverage(y_eval, mu, sigma, nu)
            pinball_res = compute_pinball_loss(y_eval, mu, sigma, nu)
            m_dict.update({
                'crps': float(np.mean(crps_vals)),
                'pit_ks_stat': float(ks_res.statistic),
                'pit_ks_pvalue': float(ks_res.pvalue),
                'coverages': cov_res,
                'pinball': pinball_res,
                'mean_scale': float(np.mean(sigma)),
                'mean_nu': float(np.mean(nu))
            })
        metrics_summary[m] = m_dict
        print(f"[{label}] Model {m:4s} -> NLL: {nll:.4f} nats, CRPS: {m_dict['crps']:.6f}, PIT KS p: {m_dict['pit_ks_pvalue']:.4f}")
        
    # Paired Test R1 vs B4
    logp_b4 = preds['B4']['log_p'][eval_indices]
    logp_r1 = preds['R1']['log_p'][eval_indices]
    d_diff = logp_r1 - logp_b4
    dm_res = diebold_mariano_test(d_diff)
    boot_res = stationary_block_bootstrap(d_diff, n_boot=2000, expected_block_len=5, seed=42)
    
    print(f"\n[{label}] Paired Hypothesis Test (R1 vs B4, N={len(eval_indices)}):")
    print(f"  Mean Log-Score Differential: {dm_res['mean_differential']:+.6f} nats/session")
    print(f"  Diebold-Mariano Stat:        {dm_res['dm_stat']:.4f} (p one-sided: {dm_res['p_value_one_sided']:.4f}, two-sided: {dm_res['p_value_two_sided']:.4f})")
    print(f"  Bootstrap 95% CI:            [{boot_res['ci_95_lower']:+.6f}, {boot_res['ci_95_upper']:+.6f}] (Excludes Zero: {boot_res['excludes_zero']})")
    
    # HMM occupancies on this eval set
    eval_pi = filtered_pi_all[eval_indices]
    eval_argmax = np.argmax(eval_pi, axis=1)
    occupancies = [float(np.mean(eval_argmax == k)) for k in range(eval_pi.shape[1])]
    
    return {
        'n_sessions': len(eval_indices),
        'metrics': metrics_summary,
        'dm_test': dm_res,
        'bootstrap': boot_res,
        'occupancies': occupancies
    }

def main():
    print("================================================================================")
    print("STAGE 8: GATE D FINAL HELD-OUT TEST EVALUATION (2022-2023)")
    print("================================================================================")
    
    out_dir = "output/stage8_test"
    os.makedirs(out_dir, exist_ok=True)
    
    df_dev, df_val, df_test = load_all_three_partitions()
    df_all = pd.concat([df_dev, df_val, df_test], ignore_index=True)
    
    test_start_idx = len(df_dev) + len(df_val)  # 2516 + 505 = 3021
    print(f"Combined total sessions: {len(df_all)}, Test start index: {test_start_idx}")
    
    # Run Walk-Forward on Test
    wf_res = run_test_walk_forward(
        df_all,
        test_start_idx=test_start_idx,
        K_regimes=2,
        lambda_reg=0.01,
        block_size=21
    )
    
    preds = wf_res['preds']
    filtered_pi_all = wf_res['filtered_pi_all']
    refit_diagnostics = wf_res['refit_diagnostics']
    
    # Build complete test prediction table
    test_indices = np.arange(test_start_idx, len(df_all))
    df_test_preds = pd.DataFrame({
        'date': df_all['date'].iloc[test_indices].values,
        'S_t': df_all['S_t'].iloc[test_indices].values,
        'target_y': df_all['target_y_next2'].iloc[test_indices].values,
        'rv_20d': df_all['rv_20d'].iloc[test_indices].values,
        'breach_exclusion_flag': df_all['breach_exclusion_flag'].iloc[test_indices].values if 'breach_exclusion_flag' in df_all.columns else False,
        'breach_note': df_all['breach_note'].iloc[test_indices].values if 'breach_note' in df_all.columns else "UNBREACHED",
        'q_is_fallback': df_all['q_is_fallback'].iloc[test_indices].values if 'q_is_fallback' in df_all.columns else False,
        'q_source': df_all['q_source'].iloc[test_indices].values if 'q_source' in df_all.columns else "CBOE_OPTIONSDX_ACTUAL"
    })
    
    for m in ['B0', 'B1', 'B2', 'B3', 'B4', 'R1']:
        df_test_preds[f'{m}_mu'] = preds[m]['mu'][test_indices]
        df_test_preds[f'{m}_sigma'] = preds[m]['sigma'][test_indices]
        df_test_preds[f'{m}_nu'] = preds[m]['nu'][test_indices]
        df_test_preds[f'{m}_log_p'] = preds[m]['log_p'][test_indices]
        
    for k in range(2):
        df_test_preds[f'pi_state_{k}'] = filtered_pi_all[test_indices, k]
        
    preds_csv_path = f"{out_dir}/test_predictions.csv"
    df_test_preds.to_csv(preds_csv_path, index=False)
    print(f"\nSaved test predictions ({len(df_test_preds)} rows) to {preds_csv_path}")
    
    # Save Per-Refit HMM Diagnostics
    test_hmm_diag = {
        'run_name': 'test_walk_forward_2022_2023',
        'n_regimes_K': 2,
        'lambda_reg': 0.01,
        'total_refit_blocks': len(refit_diagnostics),
        'constraints': {
            'min_dwell_time_required': 5.0,
            'min_occupancy_required': 0.05
        },
        'all_blocks_dwell_pass': all(b['dwell_time_constraint_pass'] for b in refit_diagnostics),
        'all_blocks_occupancy_pass': all(b['occupancy_constraint_pass'] for b in refit_diagnostics),
        'all_blocks_pass': all(b['all_constraints_pass'] for b in refit_diagnostics),
        'min_dwell_time_observed': float(min(min(b['hmm_expected_dwell_times']) for b in refit_diagnostics)),
        'max_dwell_time_observed': float(max(max(b['hmm_expected_dwell_times']) for b in refit_diagnostics)),
        'min_occupancy_argmax_observed': float(min(min(b['hmm_state_occupancies_train_argmax']) for b in refit_diagnostics)),
        'max_occupancy_argmax_observed': float(max(max(b['hmm_state_occupancies_train_argmax']) for b in refit_diagnostics)),
        'blocks': refit_diagnostics
    }
    with open(f"{out_dir}/hmm_refit_diagnostics_test.json", "w") as f:
        json.dump(test_hmm_diag, f, indent=2)
    print(f"Saved test HMM refit diagnostics to {out_dir}/hmm_refit_diagnostics_test.json")
    print(f"  Test HMM: all_dwell_pass={test_hmm_diag['all_blocks_dwell_pass']}, all_occ_pass={test_hmm_diag['all_blocks_occupancy_pass']}")
    print(f"  Observed Dwell Range: [{test_hmm_diag['min_dwell_time_observed']:.2f}, {test_hmm_diag['max_dwell_time_observed']:.2f}] sessions")
    print(f"  Observed Occupancy Range: [{test_hmm_diag['min_occupancy_argmax_observed']:.4f}, {test_hmm_diag['max_occupancy_argmax_observed']:.4f}]")
    
    # 6. Comprehensive Evaluation on All Defined Subsets
    # Subset 1: Primary Jan 3-Origin-Score-Excluded Prequential Evaluation (N=500 sessions, excluding 2022-01-03 from scoring)
    idx_unbreached = [i for i in test_indices if df_all['date'].iloc[i] != '2022-01-03']
    print(f"\n================================================================================")
    print(f"PRIMARY PREQUENTIAL TEST EVALUATION: JAN 3 ORIGIN SCORE-EXCLUDED (N={len(idx_unbreached)} sessions)")
    print(f"================================================================================")
    eval_jan3_score_excluded = evaluate_subset(df_all, preds, filtered_pi_all, idx_unbreached, label="Jan 3-Score-Excluded Prequential (N=500)")
    
    # Subset 2: Full Test Set Evaluation (N=501 sessions, including 2022-01-03)
    print(f"\n================================================================================")
    print(f"FULL TEST SET EVALUATION (N={len(test_indices)} sessions, Including 2022-01-03 Origin - Secondary)")
    print(f"================================================================================")
    eval_full = evaluate_subset(df_all, preds, filtered_pi_all, test_indices, label="Full Test Set (N=501)")
    
    # Subset 3: Actual-Quote Scoring Subset (N=495 sessions, excluding 5 forward-filled gap dates & 2022-01-03)
    gap_dates = ['2022-05-11', '2022-06-17', '2022-06-24', '2022-12-16', '2023-01-03']
    idx_actual_quotes = [i for i in idx_unbreached if df_all['date'].iloc[i] not in gap_dates]
    print(f"\n================================================================================")
    print(f"ACTUAL-QUOTE SCORING SUBSET (N={len(idx_actual_quotes)} sessions, Live Option Quotes Only)")
    print(f"================================================================================")
    eval_actual_quotes = evaluate_subset(df_all, preds, filtered_pi_all, idx_actual_quotes, label="Actual-Quote Scoring Subset (N=495)")
    
    # Subset 4: Jan 3 Strictly Isolated Trajectory (N=500 sessions, excluding 2022-01-03 from scoring AND supervised training)
    print(f"\n================================================================================")
    print(f"STRICT ISOLATION SENSITIVITY: EXCLUDING 2022-01-03 FROM SCORING & SUPERVISED REFITS")
    print(f"================================================================================")
    wf_strict = run_test_walk_forward(
        df_all, test_start_idx, K_regimes=2, lambda_reg=0.01, block_size=21, exclude_origin_from_training='2022-01-03'
    )
    preds_strict = wf_strict['preds']
    pi_strict = wf_strict['filtered_pi_all']
    diag_strict = wf_strict['refit_diagnostics']
    eval_strict_isolation = evaluate_subset(df_all, preds_strict, pi_strict, idx_unbreached, label="Jan 3 Strictly Isolated Trajectory (N=500)")
    
    # Save Strict Isolation Predictions Table
    df_strict_preds = pd.DataFrame({
        'date': df_all['date'].iloc[test_indices].values,
        'S_t': df_all['S_t'].iloc[test_indices].values,
        'target_y': df_all['target_y_next2'].iloc[test_indices].values,
        'rv_20d': df_all['rv_20d'].iloc[test_indices].values,
        'breach_exclusion_flag': df_all['breach_exclusion_flag'].iloc[test_indices].values if 'breach_exclusion_flag' in df_all.columns else False,
        'breach_note': df_all['breach_note'].iloc[test_indices].values if 'breach_note' in df_all.columns else "UNBREACHED",
        'q_is_fallback': df_all['q_is_fallback'].iloc[test_indices].values if 'q_is_fallback' in df_all.columns else False,
        'q_source': df_all['q_source'].iloc[test_indices].values if 'q_source' in df_all.columns else "CBOE_OPTIONSDX_ACTUAL"
    })
    for m in ['B0', 'B1', 'B2', 'B3', 'B4', 'R1']:
        df_strict_preds[f'{m}_mu'] = preds_strict[m]['mu'][test_indices]
        df_strict_preds[f'{m}_sigma'] = preds_strict[m]['sigma'][test_indices]
        df_strict_preds[f'{m}_nu'] = preds_strict[m]['nu'][test_indices]
        df_strict_preds[f'{m}_log_p'] = preds_strict[m]['log_p'][test_indices]
    for k in range(2):
        df_strict_preds[f'pi_state_{k}'] = pi_strict[test_indices, k]
    strict_preds_csv_path = f"{out_dir}/test_predictions_strict_isolation.csv"
    df_strict_preds.to_csv(strict_preds_csv_path, index=False)
    print(f"Saved strict isolation test predictions ({len(df_strict_preds)} rows) to {strict_preds_csv_path}")

    # 7. Mathematical Density Integrity Verification
    print(f"\n================================================================================")
    print("MATHEMATICAL DENSITY INTEGRITY VERIFICATION ON TEST PREDICTIONS")
    print("================================================================================")
    test_sample_dates = [0, 100, 200, 300, 400, 500]
    integration_checks = []
    for s_idx in test_sample_dates:
        row = df_test_preds.iloc[s_idx]
        mu = row['R1_mu']
        sig = row['R1_sigma']
        nu = row['R1_nu']
        dist = stats.t(df=nu, loc=mu, scale=sig)
        integral, _ = integrate.quad(lambda z: dist.pdf(z), mu - 20 * sig, mu + 20 * sig)
        integration_checks.append({
            'date': str(row['date']),
            'mu': float(mu),
            'sigma': float(sig),
            'nu': float(nu),
            'integral': float(integral),
            'error': float(abs(integral - 1.0))
        })
        print(f"Date {row['date']}: mu={mu:+.6f}, sigma={sig:.6f}, nu={nu:.2f} -> Integral={integral:.8f} (Error: {abs(integral - 1.0):.2e})")
        
    with open(f"{out_dir}/density_integration_checks.json", "w") as f:
        json.dump(integration_checks, f, indent=2)
        
    # Save Final Test Summary JSON
    test_summary = {
        'evaluation_date': '2026-10-24',
        'governing_protocol': 'research_protocol.md (Stage 8 / Gate D)',
        'frozen_stage7_commit': '66924f36d55a1c829f8a4c8657935735ee177b81',
        'frozen_parameters': {
            'K_regimes': 2,
            'lambda_reg': 0.01,
            'refit_frequency_sessions': 21,
            'label_maturity_rule': 't <= tau - 2',
            'hmm_emissions_rule': 't <= tau',
            'crps_method': 'Exact Analytical (Jordan, Kruger, Lerch 2019)'
        },
        'primary_evaluation_jan3_score_excluded_N500': {
            'description': 'Jan 3-origin-score-excluded prequential evaluation',
            'note': (
                'Primary prequential evaluation under frozen protocol design. Origin 2022-01-03 is excluded from '
                'out-of-sample scoring as a conservative safeguard against historical cash-close access in commit cee01a1. '
                'Under prequential walk-forward rules, matured labels (t <= tau_m - 2) from this origin are incorporated '
                'into supervised model refits at expanding windows tau_1 through tau_23.'
            ),
            'metrics': eval_jan3_score_excluded
        },
        'sensitivity_jan3_strictly_isolated_N500': {
            'description': 'Jan 3-origin strictly isolated trajectory',
            'note': (
                'Strictly isolated sensitivity trajectory where origin 2022-01-03 is excluded from out-of-sample scoring '
                'AND excluded from supervised training sets at all 24 refit blocks.'
            ),
            'metrics': eval_strict_isolation
        },
        'secondary_full_test_evaluation_N501': {
            'description': 'Full test set evaluation including 2022-01-03 origin',
            'note': (
                'Secondary evaluation including origin 2022-01-03. Origin 2022-01-03 has cash close 2022-01-03 accessed '
                'in Git commit cee01a1, but its Proposal A target ln(S_{2022-01-05}/S_{2022-01-04}) was uncompromised. '
                'Reported transparently alongside the primary run.'
            ),
            'metrics': eval_full
        },
        'actual_quote_scoring_subset_N495': {
            'description': 'Actual-quote scoring subset',
            'note': (
                'Evaluates out-of-sample predictive scoring strictly on the 495 sessions with live option quotes (excluding '
                'the 5 forward-filled gap dates and 2022-01-03). Models at later refit blocks incorporate previously matured '
                'labels from permitted forward-filled dates; this subset isolates scoring but does not isolate training-time forward-fill effects.'
            ),
            'metrics': eval_actual_quotes
        },
        'test_breach_disclosure': {
            'breach_origin': '2022-01-03',
            'breach_interval_cash_closes': {
                '2022-01-03': 4796.56,
                '2022-01-04': 4793.54
            },
            'breach_return_log': -0.000630,
            'status': 'Jan 3-origin-score-excluded in primary prequential run (N=500); strictly excluded from training in sensitivity run (N=500); reported side-by-side in Full Set (N=501)'
        },
        'missing_option_gaps_disclosure': {
            'n_gaps': 5,
            'gap_dates': gap_dates,
            'gap_rule_applied': 'Causal prior-session forward-fill Q_t <- Q_{t-1} per protocol',
            'all_gaps_isolated': True
        },
        'data_access_scope_disclosure': {
            'cash_closes_end_date': '2024-01-03',
            'label_maturity_origins': ['2023-12-28', '2023-12-29'],
            'note': 'Cash closes for 2024-01-04 to 2024-01-09 were initially fetched during data exploration and have been truncated. spx_daily_closes_2009_2024.csv ends strictly at 2024-01-03.'
        }
    }
    
    with open(f"{out_dir}/test_metrics_summary.json", "w") as f:
        json.dump(test_summary, f, indent=2)
    print(f"\nSaved test metrics summary to {out_dir}/test_metrics_summary.json")
    
    print("\n================================================================================")
    print("STAGE 8 GATE D FINAL HELD-OUT TEST EVALUATION COMPLETE!")
    print("================================================================================")

if __name__ == "__main__":
    main()
