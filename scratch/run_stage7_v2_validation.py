"""
run_stage7_v2_validation.py
===========================
Step 5 (fix/optimizer-calibration): validation-only walk-forward rerun with converged
fits. Development + validation data only (2010-2021); the 2022-2023 test file is never
loaded. Writes to output/stage7_models_v2/ and does not touch output/stage7_models/.

Protocol
1. lambda grid {1e-4, 1e-3, 1e-2}, K = 2, primary expanding window from 2010-01-04.
2. Convergence gate: every B1/B2/B3/B4/R1 fit and every HMM fit in every refit must be
   converged; otherwise the script stops before writing results.
3. lambda selected by the Stage 7 rule (minimum B4 validation NLL), unchanged.
4. Section-3 paired comparisons at the selected lambda (positive d favours the challenger):
   Q1 B4-B3, Q2 B2-B1 and B2-B0, Q3 B3-B1, R1-B4 (secondary): mean d, HAC DM at lags
   5/10/21, stationary bootstrap CI (2000 reps, mean block 5, seed 42), by year, by
   21-session block, and excluding origins dated 2020-03-01..2020-04-30.
5. Secondary diagnostics per model: NLL, CRPS, PIT KS (B0 per-row), 50/80/95% coverage,
   predicted-sigma summary.
6. The same comparisons recomputed from the saved Stage 7 predictions (unconverged fits)
   for a side-by-side view, and a compact per-lambda sensitivity table.

Run from the repository root: python scratch/run_stage7_v2_validation.py
"""
import json
import os
import sys
import time
import warnings

sys.path.insert(0, ".")
import numpy as np
import pandas as pd

from src.models.paired_comparisons import COMPARISONS, run_comparisons, stress_mask
from src.models.walk_forward_pipeline import load_datasets, run_walk_forward

OUT_DIR = "output/stage7_models_v2"
SAVED_V1_PREDS = "output/stage7_models/validation_predictions_primary.csv"
LAMBDAS = [1e-4, 1e-3, 1e-2]
K = 2
MODELS = ["B0", "B1", "B2", "B3", "B4", "R1"]


def convergence_failures(res):
    failures = []
    for blk in res["refit_diagnostics"]:
        if not blk["hmm_converged"]:
            failures.append((blk["refit_date"], "HMM", blk["hmm_n_iter"]))
        for m, rep in blk["fit_reports"].items():
            if not rep["converged"]:
                failures.append((blk["refit_date"], m, rep["stop_reason"], rep["max_abs_grad"]))
    return failures


def block_ids_for(res, df_all):
    """Refit block number for each scored validation row."""
    ids = np.full(len(df_all), -1)
    for blk in res["refit_diagnostics"]:
        sw = blk["scoring_window"]
        ids[sw["score_start_idx"]:sw["score_end_idx"]] = blk["block"]
    out = ids[res["val_indices"]]
    assert np.all(out >= 0)
    return out


def sigma_summary(sigma, dates):
    mar = stress_mask(dates)
    return {
        "mean": float(np.mean(sigma)),
        "median": float(np.median(sigma)),
        "max": float(np.max(sigma)),
        "max_mar_apr_2020": float(np.max(sigma[mar])) if mar.any() else None,
        "n_sigma_gt_0.05": int(np.sum(sigma > 0.05)),
    }


def fit_report_summary(res):
    out = {}
    for m in ["B1", "B2", "B3", "B4", "R1"]:
        reps = [blk["fit_reports"][m] for blk in res["refit_diagnostics"]]
        out[m] = {
            "n_fits": len(reps),
            "all_converged": all(r["converged"] for r in reps),
            "max_abs_grad_max": max(r["max_abs_grad"] for r in reps),
            "n_iter_range": [min(r["n_iter"] for r in reps), max(r["n_iter"] for r in reps)],
            "nu_range": [min(r["nu"] for r in reps), max(r["nu"] for r in reps)],
            "hessian_min_eig_min": min(r["hessian_min_eig"] for r in reps),
        }
    return out


def compact(comparisons):
    return {name: {
        "mean_d": c["full"]["mean_d"],
        "dm_p_one_sided_lag5": c["full"]["dm"]["lag_5"]["p_value_one_sided"],
        "boot_ci": [c["full"]["bootstrap"]["ci_95_lower"], c["full"]["bootstrap"]["ci_95_upper"]],
        "mean_d_ex_stress": c["excluding_stress"]["mean_d"],
        "dm_p_one_sided_lag5_ex_stress": c["excluding_stress"]["dm"]["lag_5"]["p_value_one_sided"],
    } for name, c in comparisons.items()}


def main():
    t0 = time.time()
    warnings.simplefilter("always", RuntimeWarning)
    df_dev, df_val = load_datasets()
    df_all = pd.concat([df_dev, df_val], ignore_index=True)
    n_dev = len(df_dev)
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1-2. lambda grid with convergence gate
    runs, grid = {}, []
    for lam in LAMBDAS:
        res = run_walk_forward(df_all, val_start_idx=n_dev, K_regimes=K, lambda_reg=lam)
        fails = convergence_failures(res)
        if fails:
            raise SystemExit(f"Convergence gate failed for lambda={lam}: {fails}")
        runs[lam] = res
        grid.append({"lambda": lam, "K": K, **{f"{m}_nll": res["val_metrics"][m]["nll"] for m in MODELS}})
        print(f"lambda={lam}: " + ", ".join(f"{m} {res['val_metrics'][m]['nll']:.5f}" for m in MODELS))

    # 3. lambda selection (Stage 7 rule)
    lam_star = min(grid, key=lambda r: r["B4_nll"])["lambda"]
    res = runs[lam_star]
    vi = res["val_indices"]
    dates = df_all["date"].values[vi]
    blocks = block_ids_for(res, df_all)
    excl = stress_mask(dates)
    log_p = {m: res["preds"][m]["log_p"][vi] for m in MODELS}

    # 4. comparisons at lambda*, plus per-lambda sensitivity
    comparisons = run_comparisons(log_p, dates, blocks, exclude=excl)
    per_lambda = {}
    for lam, r in runs.items():
        lp = {m: r["preds"][m]["log_p"][vi] for m in MODELS}
        per_lambda[str(lam)] = compact(run_comparisons(lp, dates, blocks, exclude=excl))

    # 6. same comparisons from saved Stage 7 predictions
    v1 = pd.read_csv(SAVED_V1_PREDS)
    assert list(v1["date"]) == list(dates), "saved Stage 7 rows do not align with v2 scored rows"
    v1_comparisons = run_comparisons({m: v1[f"{m}_log_p"].values for m in MODELS}, dates, blocks, exclude=excl)

    # 5. per-model diagnostics
    model_metrics = {}
    for m in MODELS:
        vm = dict(res["val_metrics"][m])
        sig = res["preds"][m]["sigma"][vi]
        vm["sigma"] = sigma_summary(sig, dates)
        vm["nll_ex_stress"] = float(-np.mean(log_p[m][~excl]))
        vm["nll_stage7_saved"] = float(-np.mean(v1[f"{m}_log_p"].values))
        model_metrics[m] = vm

    # predictions table
    pred = pd.DataFrame({"date": dates, "block": blocks, "target_y": df_all["target_y_next2"].values[vi],
                         "rv_20d": df_all["rv_20d"].values[vi], "stress_window": excl})
    for m in MODELS:
        for f in ["mu", "sigma", "nu", "log_p"]:
            pred[f"{m}_{f}"] = res["preds"][m][f][vi]
    for k in range(K):
        pred[f"pi_state_{k}"] = res["filtered_pi_all"][vi, k]
    pred.to_csv(f"{OUT_DIR}/validation_predictions_primary_v2.csv", index=False)

    with open(f"{OUT_DIR}/lambda_grid_K2_v2.json", "w") as f:
        json.dump({"grid": grid, "selected_lambda": lam_star,
                   "selection_rule": "argmin B4 validation NLL (Stage 7 rule)"}, f, indent=2)
    with open(f"{OUT_DIR}/refit_diagnostics_primary_v2.json", "w") as f:
        json.dump({"lambda": lam_star, "K": K, "fit_report_summary": fit_report_summary(res),
                   "blocks": res["refit_diagnostics"]}, f, indent=2)
    with open(f"{OUT_DIR}/validation_metrics_summary_v2.json", "w") as f:
        json.dump({"lambda": lam_star, "K": K, "n_scored": int(len(vi)),
                   "stress_window": ["2020-03-01", "2020-04-30"], "n_stress_rows": int(excl.sum()),
                   "models": model_metrics}, f, indent=2)
    with open(f"{OUT_DIR}/paired_comparisons_v2.json", "w") as f:
        json.dump({"lambda": lam_star, "K": K, "sign": "d = log p_challenger - log p_comparator; positive favours challenger",
                   "comparisons": comparisons, "stage7_saved_comparisons": v1_comparisons,
                   "per_lambda_sensitivity": per_lambda}, f, indent=2)

    # console summary
    print(f"\nselected lambda = {lam_star}; scored rows = {len(vi)}; stress rows = {int(excl.sum())}")
    print(f"{'comparison':16s} {'mean d':>10s} {'p5':>7s} {'p10':>7s} {'p21':>7s} {'boot CI':>24s} "
          f"{'ex-stress d':>12s} {'p5':>7s} {'blocks+':>8s} | {'stage7 d':>10s}")
    for name, *_ in COMPARISONS:
        c, v = comparisons[name], v1_comparisons[name]
        fu, ex = c["full"], c["excluding_stress"]
        print(f"{name:16s} {fu['mean_d']:+10.5f} {fu['dm']['lag_5']['p_value_one_sided']:7.4f} "
              f"{fu['dm']['lag_10']['p_value_one_sided']:7.4f} {fu['dm']['lag_21']['p_value_one_sided']:7.4f} "
              f"[{fu['bootstrap']['ci_95_lower']:+.5f}, {fu['bootstrap']['ci_95_upper']:+.5f}] "
              f"{ex['mean_d']:+12.5f} {ex['dm']['lag_5']['p_value_one_sided']:7.4f} "
              f"{fu['n_blocks_positive']:3d}/{fu['n_blocks']:<3d} | {v['full']['mean_d']:+10.5f}")
    print("\nmodel   NLL      ex-stress  stage7   CRPS      PIT-KS p  cov50  cov80  cov95  max sigma")
    for m in MODELS:
        vm = model_metrics[m]
        cov = vm["coverages"]
        print(f"{m:6s} {vm['nll']:8.5f} {vm['nll_ex_stress']:9.5f} {vm['nll_stage7_saved']:8.5f} {vm['crps']:.6f} "
              f"{vm['pit_ks_pvalue']:9.4f} {cov['coverage_50']:.3f}  {cov['coverage_80']:.3f}  {cov['coverage_95']:.3f}  "
              f"{vm['sigma']['max']:.4f}")
    print(f"\ndone in {time.time() - t0:.0f}s; outputs in {OUT_DIR}/")


if __name__ == "__main__":
    main()
