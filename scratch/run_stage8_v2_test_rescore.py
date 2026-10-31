"""
run_stage8_v2_test_rescore.py
=============================
Step 8 (fix/optimizer-calibration): POST-HOC re-score of the 2022-2023 test partition under
the configuration frozen on validation, following output/stage8_test_v2/step8_test_protocol.md
(committed before this script loaded the test file). Writes to output/stage8_test_v2/ only.

Runs (lambda 1e-4, K 2, converged fits; training = all matured dev + validation + test labels):
  clipped           frozen configuration (Step 6 adopted control)        -> primary
  clipped_strict    as clipped, 2022-01-03 removed from every training set
  unclipped         Step 5 configuration
Primary decision: Q1 (B4 vs B3), N=500 (2022-01-03 not scored), one-sided HAC DM, 5 lags,
alpha 0.05. Everything else is secondary and reported without a decision.

Run from the repository root: python scratch/run_stage8_v2_test_rescore.py
"""
import json
import os
import sys
import time
import warnings

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
from scipy import stats

from src.models.evaluation_metrics import (compute_crps_student_t_vectorized, compute_interval_coverage,
                                           gaussian_crps)
from src.models.paired_comparisons import COMPARISONS, run_comparisons, summarize_differential
from src.models.recalibration import prequential_scale_recalibration
from src.models.walk_forward_pipeline import run_walk_forward

OUT_DIR = "output/stage8_test_v2"
DEV = "output/stage7_datasets/spx_stage7_operational_development_2010_2019.csv"
VAL = "output/stage7_datasets/spx_stage7_operational_validation_2020_2021.csv"
TEST = "output/stage8_test/spx_features_test_2022_2023.csv"
GATE_D_PREDS = "output/stage8_test/test_predictions.csv"
GATE_D_SUMMARY = "output/stage8_test/test_metrics_summary.json"
LAMBDA, K, CLIP = 1e-4, 2, (0.005, 0.995)
MODELS = ["B0", "B1", "B2", "B3", "B4", "R1"]
BREACH = "2022-01-03"
GAP_DATES = ["2022-05-11", "2022-06-17", "2022-06-24", "2022-12-16", "2023-01-03"]
ALPHA = 0.05
RUNS = {
    "clipped": {"clip_quantiles": CLIP},
    "clipped_strict": {"clip_quantiles": CLIP, "exclude_train_dates": [BREACH]},
    "unclipped": {},
}


def model_metrics(preds, y, idx):
    out = {}
    for m in MODELS:
        mu, sig, nu, lp = (preds[m][f][idx] for f in ["mu", "sigma", "nu", "log_p"])
        if m == "B0":
            pit = stats.norm.cdf(y, mu, sig)
            crps = float(np.mean([gaussian_crps(y[i], mu[i], sig[i]) for i in range(len(y))]))
            cov = {}
            for c in [0.50, 0.80, 0.95]:
                lo, hi = stats.norm.ppf((1 - c) / 2, mu, sig), stats.norm.ppf((1 + c) / 2, mu, sig)
                cov[f"coverage_{int(c * 100)}"] = float(np.mean((y >= lo) & (y <= hi)))
        else:
            pit = stats.t.cdf(y, df=nu, loc=mu, scale=sig)
            crps = float(np.mean(compute_crps_student_t_vectorized(y, mu, sig, nu)))
            cov = compute_interval_coverage(y, mu, sig, nu)
        ks = stats.kstest(pit, "uniform")
        out[m] = {"nll": float(-np.mean(lp)), "crps": crps, "pit_ks_stat": float(ks.statistic),
                  "pit_ks_pvalue": float(ks.pvalue), "coverages": cov, "max_sigma": float(np.max(sig))}
    return out


def recalibrated_log_p(preds, y, row_idx, blocks, refit_tau):
    out, paths = {}, {}
    for m in MODELS:
        nu = None if m == "B0" else preds[m]["nu"]
        r = prequential_scale_recalibration(y, preds[m]["mu"], preds[m]["sigma"], nu, row_idx, blocks, refit_tau)
        out[m], paths[m] = r["log_p"], {str(b): v["c"] for b, v in r["per_block"].items()}
    return out, paths


def main():
    t0 = time.time()
    warnings.simplefilter("always", RuntimeWarning)
    df_dev, df_val, df_test = pd.read_csv(DEV), pd.read_csv(VAL), pd.read_csv(TEST)
    df_all = pd.concat([df_dev, df_val, df_test], ignore_index=True)
    test_start = len(df_dev) + len(df_val)
    gate_d = pd.read_csv(GATE_D_PREDS)
    os.makedirs(OUT_DIR, exist_ok=True)

    results, run_info = {}, {}
    for run, kwargs in RUNS.items():
        res = run_walk_forward(df_all, val_start_idx=test_start, K_regimes=K, lambda_reg=LAMBDA, **kwargs)
        fails = [(b["refit_date"], m) for b in res["refit_diagnostics"] for m, r in b["fit_reports"].items() if not r["converged"]]
        fails += [(b["refit_date"], "HMM") for b in res["refit_diagnostics"] if not b["hmm_converged"]]
        if fails:
            raise SystemExit(f"Convergence gate failed for {run}: {fails}")
        vi = res["val_indices"]
        dates = df_all["date"].values[vi]
        assert list(dates) == list(gate_d["date"]), "scored test rows differ from Gate D"
        y = df_all["target_y_next2"].values[vi]
        ids = np.full(len(df_all), -1)
        for blk in res["refit_diagnostics"]:
            ids[blk["scoring_window"]["score_start_idx"]:blk["scoring_window"]["score_end_idx"]] = blk["block"]
        blocks = ids[vi]
        refit_tau = {b["block"]: b["refit_origin_tau"] for b in res["refit_diagnostics"]}
        preds = {m: {f: res["preds"][m][f][vi] for f in ["mu", "sigma", "nu", "log_p"]} for m in MODELS}

        samples = {"primary_N500": dates != BREACH}
        if run != "clipped_strict":
            samples["full_N501"] = np.ones(len(dates), dtype=bool)
            samples["actual_quote_N495"] = (dates != BREACH) & ~np.isin(dates, GAP_DATES)
        run_res = {}
        for s, mask in samples.items():
            sub = {m: {f: v[mask] for f, v in p.items()} for m, p in preds.items()}
            raw = {m: sub[m]["log_p"] for m in MODELS}
            recal, paths = recalibrated_log_p(sub, y[mask], vi[mask], blocks[mask], refit_tau)
            run_res[s] = {
                "n": int(mask.sum()),
                "model_metrics": model_metrics(preds, y[mask], np.where(mask)[0]),
                "nll_recalibrated": {m: float(-np.mean(v)) for m, v in recal.items()},
                "comparisons_raw": run_comparisons(raw, dates[mask], blocks[mask]),
                "comparisons_recalibrated": run_comparisons(recal, dates[mask], blocks[mask]),
                "scale_factor_paths": paths,
            }
        results[run] = run_res
        run_info[run] = {"kwargs": {k: list(v) for k, v in kwargs.items()},
                         "n_refits": len(res["refit_diagnostics"]),
                         "max_abs_grad": max(r["max_abs_grad"] for b in res["refit_diagnostics"] for r in b["fit_reports"].values()),
                         "n_scoring_feature_values_clipped": int(sum(b["n_scoring_feature_values_clipped"] for b in res["refit_diagnostics"]))}
        pred = pd.DataFrame({"date": dates, "block": blocks, "target_y": y})
        for m in MODELS:
            for f in ["mu", "sigma", "nu", "log_p"]:
                pred[f"{m}_{f}"] = preds[m][f]
        pred.to_csv(f"{OUT_DIR}/test_predictions_{run}.csv", index=False)
        print(f"{run}: done ({time.time() - t0:.0f}s)")

    # primary decision
    q1 = results["clipped"]["primary_N500"]["comparisons_raw"]["Q1_B4_vs_B3"]["full"]
    p_primary = q1["dm"]["lag_5"]["p_value_one_sided"]
    decision = {"comparison": "Q1_B4_vs_B3", "sample": "primary_N500", "configuration": "clipped",
                "mean_d": q1["mean_d"], "dm_stat_lag5": q1["dm"]["lag_5"]["dm_stat"],
                "p_one_sided_lag5": p_primary, "alpha": ALPHA, "reject_equal_accuracy": bool(p_primary < ALPHA),
                "label": "POST-HOC re-score of an already-observed test partition"}

    # Gate D side-by-side (unconverged Stage 7 configuration, lambda 0.01)
    mask = gate_d["date"].values != BREACH
    gd_dates = gate_d["date"].values[mask]
    gd_blocks = pd.read_csv(f"{OUT_DIR}/test_predictions_clipped.csv")["block"].values[mask]
    gd = run_comparisons({m: gate_d[f"{m}_log_p"].values[mask] for m in MODELS}, gd_dates, gd_blocks)

    with open(f"{OUT_DIR}/test_rescore_v2.json", "w") as f:
        json.dump({"protocol": f"{OUT_DIR}/step8_test_protocol.md", "label": decision["label"],
                   "lambda": LAMBDA, "K": K, "primary_decision": decision, "runs": run_info,
                   "results": results, "gate_d_saved_predictions_comparisons_N500": gd,
                   "gate_d_summary_file": GATE_D_SUMMARY}, f, indent=2)

    print("\n=== PRIMARY (post-hoc) ===")
    print(json.dumps(decision, indent=2))
    for run in RUNS:
        for s, r in results[run].items():
            print(f"\n[{run} / {s}, N={r['n']}]  NLL: " + ", ".join(f"{m} {v['nll']:.4f}" for m, v in r["model_metrics"].items()))
            for n, *_ in COMPARISONS:
                a, b = r["comparisons_raw"][n]["full"], r["comparisons_recalibrated"][n]["full"]
                print(f"  {n:16s} raw {a['mean_d']:+.4f} p5 {a['dm']['lag_5']['p_value_one_sided']:.3f} "
                      f"p21 {a['dm']['lag_21']['p_value_one_sided']:.3f} CI [{a['bootstrap']['ci_95_lower']:+.4f},{a['bootstrap']['ci_95_upper']:+.4f}] "
                      f"yrs {({k: round(v['mean_d'], 4) for k, v in a['by_year'].items()})} blk+ {a['n_blocks_positive']}/{a['n_blocks']} "
                      f"| recal {b['mean_d']:+.4f} p5 {b['dm']['lag_5']['p_value_one_sided']:.3f}")
    print("\n[Gate D saved predictions, N=500]")
    for n, *_ in COMPARISONS:
        a = gd[n]["full"]
        print(f"  {n:16s} {a['mean_d']:+.4f} p5 {a['dm']['lag_5']['p_value_one_sided']:.3f}")
    print(f"\ndone in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
