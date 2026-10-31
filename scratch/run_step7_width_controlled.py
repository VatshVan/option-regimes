"""
run_step7_width_controlled.py
=============================
Step 7 (fix/optimizer-calibration): width-controlled comparison and R1 ablations, as
pre-declared in output/stage7_models_v2/step7_specification.md (committed before this
script was run). Development + validation data only; the test file is never loaded.

Inputs: Step 5 unclipped baseline and Step 6 adopted clipped predictions.
1. R1 ablations in the clipped configuration: shuffled pi, static RV-median threshold.
   Every run passes the convergence gate and must reproduce B0-B4 of the clipped run
   exactly (|delta log p| < 1e-10).
2. Prequential scale recalibration (src/models/recalibration.py) of every model in both
   configurations; factors use only matured past rows (s <= tau_b - 2).
3. Paired comparisons (Q1, Q2a, Q2b, Q3, R1-B4, and ablation comparisons) with and
   without recalibration.

Run from the repository root: python scratch/run_step7_width_controlled.py
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
from src.models.recalibration import prequential_scale_recalibration
from src.models.walk_forward_pipeline import load_datasets, run_walk_forward

OUT_DIR = "output/stage7_models_v2"
UNCLIPPED = f"{OUT_DIR}/validation_predictions_primary_v2.csv"
CLIPPED = f"{OUT_DIR}/step6_predictions_a_clip.csv"
DIAG = f"{OUT_DIR}/refit_diagnostics_primary_v2.json"
LAMBDA, K, CLIP = 1e-4, 2, (0.005, 0.995)
MODELS = ["B0", "B1", "B2", "B3", "B4", "R1"]
REPRO_TOL = 1e-10
ABLATIONS = {"R1_shuffled_pi": "shuffle", "R1_rv_median": "rv_median"}
ABLATION_COMPARISONS = [
    ("R1_vs_R1_shuffled_pi", "R1", "R1_shuffled_pi", "Timing of regime probabilities (Ablation 2)"),
    ("R1_shuffled_pi_vs_B4", "R1_shuffled_pi", "B4", "Shuffled-pi model vs no-regime model"),
    ("R1_vs_R1_rv_median", "R1", "R1_rv_median", "HMM filter vs static RV-median threshold (Ablation 3)"),
    ("R1_rv_median_vs_B4", "R1_rv_median", "B4", "Static threshold vs no-regime model"),
]


def frame_to_models(df, models):
    return {m: {f: df[f"{m}_{f}"].values for f in ["mu", "sigma", "nu", "log_p"]} for m in models}


def recalibrate(preds, y, row_idx, blocks, refit_tau):
    out, paths = {}, {}
    for m, p in preds.items():
        nu = None if np.all(np.isnan(p["nu"])) else p["nu"]
        r = prequential_scale_recalibration(y, p["mu"], p["sigma"], nu, row_idx, blocks, refit_tau)
        out[m] = r["log_p"]
        paths[m] = {str(b): v["c"] for b, v in r["per_block"].items()}
    return out, paths


def main():
    t0 = time.time()
    warnings.simplefilter("always", RuntimeWarning)
    df_dev, df_val = load_datasets()
    df_all = pd.concat([df_dev, df_val], ignore_index=True)
    n_dev = len(df_dev)
    unclipped, clipped = pd.read_csv(UNCLIPPED), pd.read_csv(CLIPPED)
    assert list(unclipped["date"]) == list(clipped["date"])
    dates = clipped["date"].values
    blocks = clipped["block"].values
    excl = stress_mask(dates)
    y = clipped["target_y"].values
    pos = {d: i for i, d in enumerate(df_all["date"].values)}
    row_idx = np.array([pos[d] for d in dates])
    refit_tau = {b["block"]: b["refit_origin_tau"] for b in json.load(open(DIAG))["blocks"]}

    configs = {"unclipped": frame_to_models(unclipped, MODELS), "clipped": frame_to_models(clipped, MODELS)}

    # 1. ablations (clipped configuration)
    ablation_checks = {}
    for name, mode in ABLATIONS.items():
        res = run_walk_forward(df_all, val_start_idx=n_dev, K_regimes=K, lambda_reg=LAMBDA,
                               clip_quantiles=CLIP, pi_ablation=mode)
        vi = res["val_indices"]
        assert list(df_all["date"].values[vi]) == list(dates)
        fails = [(b["refit_date"], m) for b in res["refit_diagnostics"] for m, r in b["fit_reports"].items() if not r["converged"]]
        fails += [(b["refit_date"], "HMM") for b in res["refit_diagnostics"] if not b["hmm_converged"]]
        if fails:
            raise SystemExit(f"Convergence gate failed for {name}: {fails}")
        repro = {m: float(np.max(np.abs(res["preds"][m]["log_p"][vi] - configs["clipped"][m]["log_p"]))) for m in MODELS[:-1]}
        if max(repro.values()) > REPRO_TOL:
            raise SystemExit(f"{name}: B0-B4 do not reproduce the clipped run: {repro}")
        ablation_checks[name] = {"pi_ablation": mode, "reproduction_B0_B4": repro,
                                 "max_sigma_mar_apr_2020": float(np.max(res["preds"]["R1"]["sigma"][vi][excl]))}
        configs["clipped"][name] = {f: res["preds"]["R1"][f][vi] for f in ["mu", "sigma", "nu", "log_p"]}
        print(f"{name}: R1-ablation NLL {-np.mean(configs['clipped'][name]['log_p']):.5f}; repro max {max(repro.values()):.1e}")

    # 2-3. recalibration and comparisons
    results = {}
    for cfg, preds in configs.items():
        raw = {m: p["log_p"] for m, p in preds.items()}
        recal, paths = recalibrate(preds, y, row_idx, blocks, refit_tau)
        comps = COMPARISONS + (ABLATION_COMPARISONS if cfg == "clipped" else [])
        results[cfg] = {
            "nll_raw": {m: float(-np.mean(v)) for m, v in raw.items()},
            "nll_recalibrated": {m: float(-np.mean(v)) for m, v in recal.items()},
            "scale_factor_paths": paths,
            "comparisons_raw": run_comparisons(raw, dates, blocks, comparisons=comps, exclude=excl),
            "comparisons_recalibrated": run_comparisons(recal, dates, blocks, comparisons=comps, exclude=excl),
        }

    with open(f"{OUT_DIR}/step7_width_controlled.json", "w") as f:
        json.dump({"specification": f"{OUT_DIR}/step7_specification.md", "lambda": LAMBDA, "K": K,
                   "ablation_checks": ablation_checks, "results": results}, f, indent=2)

    for cfg in configs:
        r = results[cfg]
        print(f"\n[{cfg}] NLL raw / recalibrated: " + ", ".join(
            f"{m} {r['nll_raw'][m]:.4f}/{r['nll_recalibrated'][m]:.4f}" for m in r["nll_raw"]))
        names = [c[0] for c in COMPARISONS + (ABLATION_COMPARISONS if cfg == "clipped" else [])]
        for n in names:
            a, b = r["comparisons_raw"][n], r["comparisons_recalibrated"][n]
            print(f"  {n:24s} raw {a['full']['mean_d']:+.4f} (p5 {a['full']['dm']['lag_5']['p_value_one_sided']:.3f}, "
                  f"CI [{a['full']['bootstrap']['ci_95_lower']:+.4f},{a['full']['bootstrap']['ci_95_upper']:+.4f}]) | "
                  f"recal {b['full']['mean_d']:+.4f} (p5 {b['full']['dm']['lag_5']['p_value_one_sided']:.3f}, "
                  f"p21 {b['full']['dm']['lag_21']['p_value_one_sided']:.3f}, "
                  f"CI [{b['full']['bootstrap']['ci_95_lower']:+.4f},{b['full']['bootstrap']['ci_95_upper']:+.4f}], "
                  f"ex-stress {b['excluding_stress']['mean_d']:+.4f})")
        c_last = {m: round(v[max(v, key=int)], 3) for m, v in r["scale_factor_paths"].items()}
        print(f"  final-block scale factors: {c_last}")
    print(f"\ndone in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
