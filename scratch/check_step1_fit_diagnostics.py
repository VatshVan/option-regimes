"""
check_step1_fit_diagnostics.py
==============================
Step 1 (fix/optimizer-calibration) acceptance check: re-runs the primary
validation walk-forward (K=2, lambda=0.01) with fit reports enabled and verifies
predictions are identical to output/stage7_models/validation_predictions_primary.csv.
Prints optimizer stop reasons per model. Validation data only; writes nothing.
Run from the repository root: python scratch/check_step1_fit_diagnostics.py
"""
import sys, json, collections
sys.path.insert(0, ".")
import numpy as np, pandas as pd
from src.models.walk_forward_pipeline import load_datasets, run_walk_forward, fit_insample_development

df_dev, df_val = load_datasets()
df_all = pd.concat([df_dev, df_val], ignore_index=True)
res = run_walk_forward(df_all, val_start_idx=len(df_dev), K_regimes=2, lambda_reg=0.01)
vi = res['val_indices']
saved = pd.read_csv("output/stage7_models/validation_predictions_primary.csv")
assert len(saved) == len(vi)
worst = 0.0
for m in ['B0', 'B1', 'B2', 'B3', 'B4', 'R1']:
    for f in ['mu', 'sigma', 'nu', 'log_p']:
        new = res['preds'][m][f][vi]; old = saved[f'{m}_{f}'].values
        if np.all(np.isnan(old)) and np.all(np.isnan(new)):
            continue
        diff = float(np.nanmax(np.abs(new - old)))
        worst = max(worst, diff)
        if diff > 0:
            print(f"  {m}_{f}: max|diff| = {diff:.3e}")
print("max |diff| over all prediction columns:", worst)

reasons = collections.Counter()
for b in res['refit_diagnostics']:
    for m, r in b['fit_reports'].items():
        reasons[(m, r['stop_reason'])] += 1
print("stop reasons:", dict(reasons))
for k in [0, 3, 6, 12, 18, 23]:
    b = res['refit_diagnostics'][k]
    print(b['refit_date'], {m: (r['n_iter'], r['func_evals'], round(r['penalized_loss'], 5), f"{r['max_abs_grad']:.1e}", round(r['nu'], 3)) for m, r in b['fit_reports'].items()})

ins = fit_insample_development(df_dev, lambda_reg=0.01)
print("in-sample:", {m: (r['stop_reason'], r['n_iter'], round(r['unpenalized_nll'], 4)) for m, r in ins['fit_reports'].items()})
json.dumps(res['refit_diagnostics'])
print("diagnostics JSON-serialisable: OK")
