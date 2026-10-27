"""
run_benchmark_gjr_validation.py
===============================
GJR-GARCH(1,1)-t benchmark (B5) on validation 2020-2021, per
output/stage7_models_v2/benchmark_gjr_specification.md (committed before fitting).
Development + validation data only; the test file is not loaded.

Run from the repository root: python scratch/run_benchmark_gjr_validation.py
"""
import json
import sys
import time

sys.path.insert(0, ".")
import numpy as np
import pandas as pd

from src.models.garch_benchmark import gjr_t_forecasts, log_density
from src.models.paired_comparisons import run_comparisons, stress_mask
from src.models.recalibration import prequential_scale_recalibration
from src.models.walk_forward_pipeline import load_datasets

OUT_DIR = "output/stage7_models_v2"
DIAG = f"{OUT_DIR}/refit_diagnostics_primary_v2.json"
CONFIGS = {"clipped": f"{OUT_DIR}/step6_predictions_a_clip.csv",
           "unclipped": f"{OUT_DIR}/validation_predictions_primary_v2.csv"}
COMPARISONS = [
    ("B4_vs_GJR", "B4", "GJR", "Q + X Student-t regression vs GJR-GARCH-t"),
    ("B2_vs_GJR", "B2", "GJR", "Q-only regression vs GJR-GARCH-t"),
    ("B3_vs_GJR", "B3", "GJR", "X-only regression vs GJR-GARCH-t"),
    ("B1_vs_GJR", "B1", "GJR", "Trailing-RV Student-t vs GJR-GARCH-t"),
    ("GJR_vs_B0", "GJR", "B0", "GJR-GARCH-t vs unconditional Gaussian"),
]
MODELS = ["B0", "B1", "B2", "B3", "B4", "GJR"]


def main():
    t0 = time.time()
    df_dev, df_val = load_datasets()
    df_all = pd.concat([df_dev, df_val], ignore_index=True)
    r = df_all["r_1d"].values
    blocks_info = json.load(open(DIAG))["blocks"]

    n = len(df_all)
    gjr = {f: np.full(n, np.nan) for f in ["mu", "sigma", "nu"]}
    fits = []
    for blk in blocks_info:
        tau = blk["refit_origin_tau"]
        s, e = blk["scoring_window"]["score_start_idx"], blk["scoring_window"]["score_end_idx"]
        pred, info = gjr_t_forecasts(r, np.arange(s, e), tau)
        if not info["converged"]:
            raise SystemExit(f"GJR fit did not converge at {blk['refit_date']}")
        for f in gjr:
            gjr[f][s:e] = pred[f]
        fits.append({"refit_date": blk["refit_date"], **info})

    results = {}
    for cfg, path in CONFIGS.items():
        base = pd.read_csv(path)
        pos = {d: i for i, d in enumerate(df_all["date"].values)}
        idx = np.array([pos[d] for d in base["date"]])
        y = base["target_y"].values
        assert np.allclose(y, df_all["target_y_next2"].values[idx])
        assert np.allclose(y, r[idx + 2]), "target is not r_{t+2}"
        dates, blocks = base["date"].values, base["block"].values
        excl = stress_mask(dates)
        preds = {m: {f: base[f"{m}_{f}"].values for f in ["mu", "sigma", "nu"]} for m in MODELS[:-1]}
        preds["GJR"] = {f: gjr[f][idx] for f in ["mu", "sigma", "nu"]}
        raw = {m: base[f"{m}_log_p"].values for m in MODELS[:-1]}
        raw["GJR"] = log_density(y, preds["GJR"])
        refit_tau = {b["block"]: b["refit_origin_tau"] for b in blocks_info}
        recal = {}
        for m in MODELS:
            nu = None if m == "B0" else preds[m]["nu"]
            recal[m] = prequential_scale_recalibration(y, preds[m]["mu"], preds[m]["sigma"], nu, idx, blocks, refit_tau)["log_p"]
        results[cfg] = {
            "nll_raw": {m: float(-np.mean(v)) for m, v in raw.items()},
            "nll_recalibrated": {m: float(-np.mean(v)) for m, v in recal.items()},
            "gjr_max_sigma_mar_apr_2020": float(np.max(preds["GJR"]["sigma"][excl])),
            "comparisons_raw": run_comparisons(raw, dates, blocks, comparisons=COMPARISONS, exclude=excl),
            "comparisons_recalibrated": run_comparisons(recal, dates, blocks, comparisons=COMPARISONS, exclude=excl),
        }
        pd.DataFrame({"date": dates, "block": blocks, "target_y": y, "GJR_mu": preds["GJR"]["mu"],
                      "GJR_sigma": preds["GJR"]["sigma"], "GJR_nu": preds["GJR"]["nu"],
                      "GJR_log_p": raw["GJR"]}).to_csv(f"{OUT_DIR}/benchmark_gjr_predictions_validation.csv", index=False)

    with open(f"{OUT_DIR}/benchmark_gjr_validation.json", "w") as f:
        json.dump({"specification": f"{OUT_DIR}/benchmark_gjr_specification.md", "fits": fits, "results": results}, f, indent=2)

    print("GJR params (first / last refit):", fits[0]["params"], fits[-1]["params"])
    for cfg, rr in results.items():
        print(f"\n[{cfg}] NLL raw: " + ", ".join(f"{m} {v:.4f}" for m, v in rr["nll_raw"].items()))
        print(f"  GJR max sigma Mar-Apr 2020: {rr['gjr_max_sigma_mar_apr_2020']:.4f}")
        for n_, *_ in COMPARISONS:
            a, b = rr["comparisons_raw"][n_], rr["comparisons_recalibrated"][n_]
            print(f"  {n_:12s} raw {a['full']['mean_d']:+.4f} p5 {a['full']['dm']['lag_5']['p_value_one_sided']:.3f} "
                  f"p21 {a['full']['dm']['lag_21']['p_value_one_sided']:.3f} "
                  f"CI [{a['full']['bootstrap']['ci_95_lower']:+.4f},{a['full']['bootstrap']['ci_95_upper']:+.4f}] "
                  f"ex-stress {a['excluding_stress']['mean_d']:+.4f} (p5 {a['excluding_stress']['dm']['lag_5']['p_value_one_sided']:.3f}) "
                  f"yrs {({k: round(v['mean_d'], 4) for k, v in a['full']['by_year'].items()})} "
                  f"| recal {b['full']['mean_d']:+.4f} p5 {b['full']['dm']['lag_5']['p_value_one_sided']:.3f}")
    print(f"\ndone in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
