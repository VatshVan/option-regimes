"""
run_stage7_experiments.py
=========================
Main execution script for Stage 7 modeling experiments.
Executes:
1. Hyperparameter grid search: lambda in {1e-4, 1e-3, 1e-2}, K in {2, 3}.
2. Fallback check for Mixture Density Network (MDN).
3. Primary walk-forward evaluation on Validation (2020–2021).
4. Mid-2012 sensitivity benchmark (2012-07-02 start).
5. In-sample Development evaluation (2010–2019).
6. Density integration & mathematical integrity checks.
7. Saving of CSV forecasts and JSON metric summaries in output/stage7_models/.
"""

import os
import sys

# Ensure repository root is on sys.path and stdout flushes immediately
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

import json
import numpy as np
import pandas as pd
from scipy import stats, integrate

from src.models.walk_forward_pipeline import load_datasets, run_walk_forward, fit_insample_development

def main():
    print("================================================================================")
    print("STAGE 7: REGIME-CONDITIONED PHYSICAL RETURN DENSITY MODELING & VALIDATION")
    print("================================================================================")
    
    # 1. Load operational datasets
    df_dev, df_val = load_datasets()
    print(f"Loaded Development dataset: {len(df_dev)} sessions (2010-01-04 to 2019-12-31)")
    print(f"Loaded Validation dataset:  {len(df_val)} sessions (2020-01-02 to 2021-12-31)")
    
    df_all = pd.concat([df_dev, df_val], ignore_index=True)
    val_start_idx = len(df_dev)  # 2516
    print(f"Combined total sessions: {len(df_all)}, Validation start index: {val_start_idx}")
    
    out_dir = "output/stage7_models"
    os.makedirs(out_dir, exist_ok=True)
    
    # 2. Hyperparameter Grid Search: lambda in {1e-4, 1e-3, 1e-2}, K in {2, 3}
    grid_results = []
    
    for K in [2, 3]:
        for lam in [1e-4, 1e-3, 1e-2]:
            print(f"\n>>> Running Grid Search: K={K}, lambda={lam} <<<")
            res = run_walk_forward(
                df_all,
                val_start_idx=val_start_idx,
                K_regimes=K,
                lambda_reg=lam,
                start_train_idx=0,
                block_size=21,
                include_mdn=False
            )
            val_m = res['val_metrics']
            grid_results.append({
                'K': K,
                'lambda': lam,
                'B4_nll': val_m['B4']['nll'],
                'R1_nll': val_m['R1']['nll'],
                'B4_crps': val_m['B4']['crps'],
                'R1_crps': val_m['R1']['crps'],
                'dm_stat': res['dm_test']['dm_stat'],
                'dm_mean_diff': res['dm_test']['mean_differential'],
                'occupancies': res['occupancies']
            })
            
    # Save Grid Search Results
    with open(f"{out_dir}/hyperparameter_tuning_results.json", "w") as f:
        json.dump(grid_results, f, indent=2)
    print("\nSaved hyperparameter tuning results to output/stage7_models/hyperparameter_tuning_results.json")
    
    # Find best hyperparameter configuration
    # Protocol rule: Default to K=2 unless K=3 passes >5% occupancy and lowers NLL by >= 0.020 nats.
    # Lambda selected by minimizing B4 validation NLL.
    b4_lambdas = [(r['lambda'], r['B4_nll']) for r in grid_results if r['K'] == 2]
    best_lambda = min(b4_lambdas, key=lambda x: x[1])[0]
    print(f"\nOptimal lambda for B4: {best_lambda}")
    
    # Check K=3 rule
    k2_r1_nll = [r['R1_nll'] for r in grid_results if r['K'] == 2 and r['lambda'] == best_lambda][0]
    k3_res = [r for r in grid_results if r['K'] == 3 and r['lambda'] == best_lambda][0]
    k3_r1_nll = k3_res['R1_nll']
    k3_occ_valid = all(occ >= 0.05 for occ in k3_res['occupancies'])
    nll_diff_k = k2_r1_nll - k3_r1_nll
    
    print(f"K=2 R1 NLL: {k2_r1_nll:.4f}, K=3 R1 NLL: {k3_r1_nll:.4f}, Delta NLL: {nll_diff_k:+.4f}")
    print(f"K=3 Occupancies: {k3_res['occupancies']}, All >= 5%: {k3_occ_valid}")
    if k3_occ_valid and nll_diff_k >= 0.020:
        selected_K = 3
        print("Decision: Adopt K=3 (passed occupancy and Delta NLL >= 0.020 threshold)")
    else:
        selected_K = 2
        print("Decision: Adopt K=2 (Parsimony default; K=3 did not meet improvement threshold)")
        
    # 3. MDN Fallback Check
    print("\n>>> Running MDN Fallback Check on Validation <<<")
    mdn_res = run_walk_forward(
        df_all,
        val_start_idx=val_start_idx,
        K_regimes=2,
        lambda_reg=best_lambda,
        start_train_idx=0,
        block_size=21,
        include_mdn=True
    )
    mdn_nll = mdn_res['val_metrics']['B4_MDN']['nll']
    b4_nll = mdn_res['val_metrics']['B4']['nll']
    print(f"Validation NLL -> Single-Component Student-t (B4): {b4_nll:.4f} nats")
    print(f"Validation NLL -> 2-Component Mixture MDN (B4_MDN): {mdn_nll:.4f} nats")
    mdn_delta = b4_nll - mdn_nll
    print(f"MDN Improvement (b4_nll - mdn_nll): {mdn_delta:+.4f} nats")
    
    # 4. Primary Walk-Forward Run with Selected Parameters
    print(f"\n================================================================================")
    print(f"PRIMARY WALK-FORWARD VALIDATION RUN: K={selected_K}, lambda={best_lambda}")
    print(f"================================================================================")
    primary_run = run_walk_forward(
        df_all,
        val_start_idx=val_start_idx,
        K_regimes=selected_K,
        lambda_reg=best_lambda,
        start_train_idx=0,
        block_size=21,
        include_mdn=False
    )
    
    # Extract prediction table for Validation
    val_indices = primary_run['val_indices']
    df_val_preds = pd.DataFrame({
        'date': df_all['date'].iloc[val_indices].values,
        'target_y': df_all['target_y_next2'].iloc[val_indices].values,
        'rv_20d': df_all['rv_20d'].iloc[val_indices].values
    })
    
    for m in ['B0', 'B1', 'B2', 'B3', 'B4', 'R1']:
        df_val_preds[f'{m}_mu'] = primary_run['preds'][m]['mu'][val_indices]
        df_val_preds[f'{m}_sigma'] = primary_run['preds'][m]['sigma'][val_indices]
        df_val_preds[f'{m}_nu'] = primary_run['preds'][m]['nu'][val_indices]
        df_val_preds[f'{m}_log_p'] = primary_run['preds'][m]['log_p'][val_indices]
        
    for k in range(selected_K):
        df_val_preds[f'pi_state_{k}'] = primary_run['filtered_pi_all'][val_indices, k]
        
    df_val_preds.to_csv(f"{out_dir}/validation_predictions_primary.csv", index=False)
    print(f"Saved primary validation predictions to {out_dir}/validation_predictions_primary.csv")
    
    # Save Primary Validation Metrics
    val_summary = {
        'selected_K': selected_K,
        'selected_lambda': best_lambda,
        'n_val_sessions': len(val_indices),
        'metrics': primary_run['val_metrics'],
        'dm_test_R1_vs_B4': primary_run['dm_test'],
        'bootstrap_R1_vs_B4': primary_run['bootstrap'],
        'occupancies': primary_run['occupancies'],
        'mdn_check': {
            'b4_student_t_nll': b4_nll,
            'b4_mdn_nll': mdn_nll,
            'mdn_improvement_nats': mdn_delta,
            'verdict': 'Student-t retained (MDN does not improve or is less stable)' if mdn_delta < 0.01 else 'MDN evaluated'
        }
    }
    with open(f"{out_dir}/validation_metrics_summary.json", "w") as f:
        json.dump(val_summary, f, indent=2)
    print(f"Saved primary validation metrics summary to {out_dir}/validation_metrics_summary.json")
    
    # 5. Mid-2012 Sensitivity Benchmark Run
    print(f"\n================================================================================")
    print(f"MID-2012 SENSITIVITY BENCHMARK RUN (Start: 2012-07-02, K={selected_K}, lambda={best_lambda})")
    print(f"================================================================================")
    idx_2012 = df_dev[df_dev['date'] == '2012-07-02'].index[0]  # 629
    sens_run = run_walk_forward(
        df_all,
        val_start_idx=val_start_idx,
        K_regimes=selected_K,
        lambda_reg=best_lambda,
        start_train_idx=idx_2012,
        block_size=21,
        include_mdn=False
    )
    
    df_sens_preds = pd.DataFrame({
        'date': df_all['date'].iloc[val_indices].values,
        'target_y': df_all['target_y_next2'].iloc[val_indices].values,
        'rv_20d': df_all['rv_20d'].iloc[val_indices].values
    })
    for m in ['B0', 'B1', 'B2', 'B3', 'B4', 'R1']:
        df_sens_preds[f'{m}_mu'] = sens_run['preds'][m]['mu'][val_indices]
        df_sens_preds[f'{m}_sigma'] = sens_run['preds'][m]['sigma'][val_indices]
        df_sens_preds[f'{m}_nu'] = sens_run['preds'][m]['nu'][val_indices]
        df_sens_preds[f'{m}_log_p'] = sens_run['preds'][m]['log_p'][val_indices]
    df_sens_preds.to_csv(f"{out_dir}/validation_predictions_sensitivity_2012.csv", index=False)
    
    sens_summary = {
        'training_start_date': '2012-07-02',
        'training_start_index': int(idx_2012),
        'n_val_sessions': len(val_indices),
        'metrics': sens_run['val_metrics'],
        'dm_test_R1_vs_B4': sens_run['dm_test'],
        'bootstrap_R1_vs_B4': sens_run['bootstrap'],
        'comparison_with_full_sample': {
            'full_b4_nll': primary_run['val_metrics']['B4']['nll'],
            'sens_b4_nll': sens_run['val_metrics']['B4']['nll'],
            'full_r1_nll': primary_run['val_metrics']['R1']['nll'],
            'sens_r1_nll': sens_run['val_metrics']['R1']['nll'],
            'full_dm_diff': primary_run['dm_test']['mean_differential'],
            'sens_dm_diff': sens_run['dm_test']['mean_differential']
        }
    }
    with open(f"{out_dir}/sensitivity_analysis_summary.json", "w") as f:
        json.dump(sens_summary, f, indent=2)
    print(f"Saved sensitivity analysis summary to {out_dir}/sensitivity_analysis_summary.json")
    
    # 6. In-Sample Development Fit (2010–2019)
    print(f"\n================================================================================")
    print(f"IN-SAMPLE DEVELOPMENT FIT (2010–2019, N=2,231 pairs)")
    print(f"================================================================================")
    insample_res = fit_insample_development(df_dev, lambda_reg=best_lambda, K_regimes=selected_K)
    with open(f"{out_dir}/insample_metrics_summary.json", "w") as f:
        json.dump(insample_res['insample_metrics'], f, indent=2)
    print(f"Saved in-sample metrics to {out_dir}/insample_metrics_summary.json")
    
    # 7. Verification of Mathematical Density Integrity
    print(f"\n================================================================================")
    print(f"MATHEMATICAL DENSITY INTEGRATION & STABILITY VERIFICATION")
    print(f"================================================================================")
    # Check that predicted densities integrate to 1.0 across a grid of samples
    # For Student-t: integral of pdf from -inf to inf is analytically 1.0; check numerical integral for 5 dates
    test_dates_idx = [0, 50, 150, 250, 450]
    integration_checks = []
    for idx in test_dates_idx:
        mu = df_val_preds['R1_mu'].iloc[idx]
        sig = df_val_preds['R1_sigma'].iloc[idx]
        nu = df_val_preds['R1_nu'].iloc[idx]
        dist = stats.t(df=nu, loc=mu, scale=sig)
        integral, _ = integrate.quad(lambda z: dist.pdf(z), mu - 20 * sig, mu + 20 * sig)
        integration_checks.append({
            'date': df_val_preds['date'].iloc[idx],
            'mu': float(mu),
            'sigma': float(sig),
            'nu': float(nu),
            'numerical_integral': float(integral),
            'integral_error': float(abs(integral - 1.0))
        })
        print(f"Date {df_val_preds['date'].iloc[idx]}: mu={mu:+.6f}, sigma={sig:.6f}, nu={nu:.2f} -> Numerical Integral = {integral:.8f} (Error: {abs(integral - 1.0):.2e})")
        
    with open(f"{out_dir}/density_integration_checks.json", "w") as f:
        json.dump(integration_checks, f, indent=2)
        
    print("\n================================================================================")
    print("STAGE 7 MODELING & VALIDATION RUN COMPLETE!")
    print("================================================================================")

if __name__ == "__main__":
    main()
