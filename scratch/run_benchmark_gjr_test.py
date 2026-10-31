"""
run_benchmark_gjr_test.py
=========================
POST-HOC: GJR-GARCH(1,1)-t benchmark on the 2022-2023 test partition, per
output/stage8_test_v2/step8_addendum_gjr_benchmark.md (committed before this script loaded
the test file). B0-R1 are read from the frozen Step 8 prediction files, not refitted.

Run from the repository root: python scratch/run_benchmark_gjr_test.py
"""
import json
import sys
import time

sys.path.insert(0, ".")
import numpy as np
import pandas as pd

from src.models.garch_benchmark import gjr_t_forecasts, log_density
from src.models.paired_comparisons import run_comparisons
from src.models.recalibration import prequential_scale_recalibration

OUT_DIR = "output/stage8_test_v2"
DEV = "output/stage7_datasets/spx_stage7_operational_development_2010_2019.csv"
VAL = "output/stage7_datasets/spx_stage7_operational_validation_2020_2021.csv"
TEST = "output/stage8_test/spx_features_test_2022_2023.csv"
CONFIGS = {"clipped": f"{OUT_DIR}/test_predictions_clipped.csv",
           "unclipped": f"{OUT_DIR}/test_predictions_unclipped.csv"}
BREACH = "2022-01-03"
GAP_DATES = ["2022-05-11", "2022-06-17", "2022-06-24", "2022-12-16", "2023-01-03"]
BLOCK = 21
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
    df_all = pd.concat([pd.read_csv(DEV), pd.read_csv(VAL), pd.read_csv(TEST)], ignore_index=True)
    test_start, n = len(df_all) - len(pd.read_csv(TEST)), len(df_all)
    r = df_all["r_1d"].values
    assert not np.isnan(r).any()

    # refit origins exactly as run_walk_forward (val_start_idx = test_start)
    taus = list(range(test_start - 1, n - 1, BLOCK))
    windows = {}
    for b, tau in enumerate(taus):
        s, e = max(test_start, tau + 1), min(n, tau + 1 + BLOCK)
        if s < e:
            windows[b] = (tau, s, e)

    gjr = {f: np.full(n, np.nan) for f in ["mu", "sigma", "nu"]}
    fits = []
    for b, (tau, s, e) in windows.items():
        pred, info = gjr_t_forecasts(r, np.arange(s, e), tau)
        if not info["converged"]:
            raise SystemExit(f"GJR fit did not converge at block {b}")
        for f in gjr:
            gjr[f][s:e] = pred[f]
        fits.append({"block": b, "refit_date": str(df_all["date"].iloc[tau]), **info})

    pos = {d: i for i, d in enumerate(df_all["date"].values)}
    results = {}
    for cfg, path in CONFIGS.items():
        base = pd.read_csv(path)
        idx = np.array([pos[d] for d in base["date"]])
        y = base["target_y"].values
        # the last two origins' targets use 2024 closes (beyond the return series); check the rest
        inside = idx + 2 < n
        assert inside.sum() >= len(idx) - 2 and np.allclose(y[inside], r[idx[inside] + 2]), "target is not r_{t+2}"
        expected_block = np.array([next(b for b, (tau, s, e) in windows.items() if s <= i < e) for i in idx])
        assert np.array_equal(expected_block, base["block"].values), "refit blocks differ from Step 8"
        dates, blocks = base["date"].values, base["block"].values
        refit_tau = {b: w[0] for b, w in windows.items()}
        preds = {m: {f: base[f"{m}_{f}"].values for f in ["mu", "sigma", "nu"]} for m in MODELS[:-1]}
        preds["GJR"] = {f: gjr[f][idx] for f in ["mu", "sigma", "nu"]}
        raw_all = {m: base[f"{m}_log_p"].values for m in MODELS[:-1]}
        raw_all["GJR"] = log_density(y, preds["GJR"])
        samples = {"primary_N500": dates != BREACH, "full_N501": np.ones(len(dates), bool),
                   "actual_quote_N495": (dates != BREACH) & ~np.isin(dates, GAP_DATES)}
        results[cfg] = {}
        for sname, mask in samples.items():
            raw = {m: v[mask] for m, v in raw_all.items()}
            recal = {}
            for m in MODELS:
                nu = None if m == "B0" else preds[m]["nu"][mask]
                recal[m] = prequential_scale_recalibration(y[mask], preds[m]["mu"][mask], preds[m]["sigma"][mask], nu,
                                                           idx[mask], blocks[mask], refit_tau)["log_p"]
            results[cfg][sname] = {
                "n": int(mask.sum()),
                "nll_raw": {m: float(-np.mean(v)) for m, v in raw.items()},
                "nll_recalibrated": {m: float(-np.mean(v)) for m, v in recal.items()},
                "comparisons_raw": run_comparisons(raw, dates[mask], blocks[mask], comparisons=COMPARISONS),
                "comparisons_recalibrated": run_comparisons(recal, dates[mask], blocks[mask], comparisons=COMPARISONS),
            }
        if cfg == "clipped":
            pd.DataFrame({"date": dates, "block": blocks, "target_y": y, "GJR_mu": preds["GJR"]["mu"],
                          "GJR_sigma": preds["GJR"]["sigma"], "GJR_nu": preds["GJR"]["nu"],
                          "GJR_log_p": raw_all["GJR"]}).to_csv(f"{OUT_DIR}/benchmark_gjr_predictions_test.csv", index=False)

    head = results["clipped"]["primary_N500"]["comparisons_raw"]["B4_vs_GJR"]["full"]
    decision = {"comparison": "B4_vs_GJR", "sample": "primary_N500", "configuration": "clipped",
                "mean_d": head["mean_d"], "dm_stat_lag5": head["dm"]["lag_5"]["dm_stat"],
                "p_one_sided_lag5": head["dm"]["lag_5"]["p_value_one_sided"], "alpha": 0.05,
                "reject_equal_accuracy": bool(head["dm"]["lag_5"]["p_value_one_sided"] < 0.05),
                "label": "POST-HOC: test partition already observed"}
    with open(f"{OUT_DIR}/benchmark_gjr_test.json", "w") as f:
        json.dump({"addendum": f"{OUT_DIR}/step8_addendum_gjr_benchmark.md", "headline": decision,
                   "fits": fits, "results": results}, f, indent=2)

    print(json.dumps(decision, indent=2))
    for cfg, rr in results.items():
        for sname, s in rr.items():
            print(f"\n[{cfg} / {sname}, N={s['n']}] NLL: " + ", ".join(f"{m} {v:.4f}" for m, v in s["nll_raw"].items()))
            for n_, *_ in COMPARISONS:
                a, b = s["comparisons_raw"][n_]["full"], s["comparisons_recalibrated"][n_]["full"]
                print(f"  {n_:10s} raw {a['mean_d']:+.4f} p5 {a['dm']['lag_5']['p_value_one_sided']:.3f} "
                      f"p21 {a['dm']['lag_21']['p_value_one_sided']:.3f} CI [{a['bootstrap']['ci_95_lower']:+.4f},{a['bootstrap']['ci_95_upper']:+.4f}] "
                      f"yrs {({k: round(v['mean_d'], 4) for k, v in a['by_year'].items()})} blk+ {a['n_blocks_positive']}/{a['n_blocks']} "
                      f"| recal {b['mean_d']:+.4f} p5 {b['dm']['lag_5']['p_value_one_sided']:.3f}")
    print(f"\ndone in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
