"""
compute_report_statistics.py
============================
Read-only, deterministic re-analysis of COMMITTED prediction files for
docs/complete_research_report.md. No model is fitted, no dataset is rebuilt, and the raw
2022-2023 test features are not loaded (only the committed prediction files that were
already scored under their protocols). Output: docs/report_appendices/detailed_statistics.md

Experiment generations are kept separate:
  O-VAL  original Stage 7 validation      output/stage7_models/validation_predictions_primary.csv   (lambda 0.01)
  O-TEST original Gate D test (N=500)      output/stage8_test/test_predictions.csv                   (lambda 0.01)
  R-VAL  revised validation, clipped       output/stage7_models_v2/step6_predictions_a_clip.csv      (lambda 1e-4)
  R-VALU revised validation, unclipped     output/stage7_models_v2/validation_predictions_primary_v2.csv
  R-TEST revised post-hoc test, clipped    output/stage8_test_v2/test_predictions_clipped.csv (N=500)
GJR-GARCH predictions (revised generations only):
  output/stage7_models_v2/benchmark_gjr_predictions_validation.csv, output/stage8_test_v2/benchmark_gjr_predictions_test.csv

Run from the repository root: python docs/report_appendices/compute_report_statistics.py
"""
import sys

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
from scipy import stats

from src.models.evaluation_metrics import (compute_crps_student_t_vectorized, diebold_mariano_test,
                                           gaussian_crps, stationary_block_bootstrap)
from src.models.paired_comparisons import stress_mask

OUT = "docs/report_appendices/detailed_statistics.md"
MODELS = ["B0", "B1", "B2", "B3", "B4", "R1"]
BREACH = "2022-01-03"
CMP = [("Q1", "B4", "B3"), ("Q2a", "B2", "B1"), ("Q2b", "B2", "B0"), ("Q3", "B3", "B1"), ("Regime", "R1", "B4")]
GJR_CMP = [("B4 vs GJR", "B4", "GJR"), ("B2 vs GJR", "B2", "GJR"), ("B3 vs GJR", "B3", "GJR"),
           ("B1 vs GJR", "B1", "GJR"), ("GJR vs B0", "GJR", "B0")]


def add_gjr(frame, path):
    g = pd.read_csv(path)
    assert list(g["date"]) == list(frame["date"])
    for f in ["mu", "sigma", "nu", "log_p"]:
        frame[f"GJR_{f}"] = g[f"GJR_{f}"].values
    return frame


def load():
    gens = {}
    v2 = pd.read_csv("output/stage7_models_v2/validation_predictions_primary_v2.csv")
    o = pd.read_csv("output/stage7_models/validation_predictions_primary.csv")
    assert list(o["date"]) == list(v2["date"])
    o["block"] = v2["block"].values
    gens["O-VAL"] = (o, "original Stage 7 validation 2020-2021, lambda 0.01, unconverged float32 fits", False)
    gd = pd.read_csv("output/stage8_test/test_predictions.csv")
    gd = gd[gd["date"] != BREACH].reset_index(drop=True)
    tb = pd.read_csv("output/stage8_test_v2/test_predictions_clipped.csv")
    tb = tb[tb["date"] != BREACH].reset_index(drop=True)
    assert list(gd["date"]) == list(tb["date"])
    gd["block"] = tb["block"].values
    gens["O-TEST"] = (gd, "original Gate D test 2022-2023, N = 500, lambda 0.01, unconverged fits", False)
    vc = add_gjr(pd.read_csv("output/stage7_models_v2/step6_predictions_a_clip.csv"),
                 "output/stage7_models_v2/benchmark_gjr_predictions_validation.csv")
    gens["R-VAL"] = (vc, "revised validation 2020-2021, converged fits, lambda 1e-4, scoring-time clipping (adopted)", True)
    vu = add_gjr(v2.copy(), "output/stage7_models_v2/benchmark_gjr_predictions_validation.csv")
    gens["R-VALU"] = (vu, "revised validation 2020-2021, converged fits, lambda 1e-4, no clipping (Step 5)", True)
    tc = add_gjr(pd.read_csv("output/stage8_test_v2/test_predictions_clipped.csv"),
                 "output/stage8_test_v2/benchmark_gjr_predictions_test.csv")
    tc = tc[tc["date"] != BREACH].reset_index(drop=True)
    gens["R-TEST"] = (tc, "revised POST-HOC test 2022-2023, N = 500, converged, lambda 1e-4, clipped", True)
    return gens


def crps(frame, m):
    y, mu, s = frame["target_y"].values, frame[f"{m}_mu"].values, frame[f"{m}_sigma"].values
    if m == "B0":
        return np.array([gaussian_crps(y[i], mu[i], s[i]) for i in range(len(y))])
    return compute_crps_student_t_vectorized(y, mu, s, frame[f"{m}_nu"].values)


def pit(frame, m):
    y, mu, s = frame["target_y"].values, frame[f"{m}_mu"].values, frame[f"{m}_sigma"].values
    if m == "B0":
        return stats.norm.cdf(y, mu, s)
    return stats.t.cdf(y, df=frame[f"{m}_nu"].values, loc=mu, scale=s)


def coverage(frame, m, c):
    a = (1 - c) / 2
    y, mu, s = frame["target_y"].values, frame[f"{m}_mu"].values, frame[f"{m}_sigma"].values
    if m == "B0":
        lo, hi = stats.norm.ppf(a, mu, s), stats.norm.ppf(1 - a, mu, s)
    else:
        nu = frame[f"{m}_nu"].values
        lo, hi = stats.t.ppf(a, nu, mu, s), stats.t.ppf(1 - a, nu, mu, s)
    return float(np.mean((y >= lo) & (y <= hi)))


def f(x, d=4):
    return f"{x:+.{d}f}"


def main():
    gens = load()
    L = ["# Appendix B - Detailed statistics recomputed from committed predictions", "",
         "Generated by `docs/report_appendices/compute_report_statistics.py` (read-only; committed prediction files only). "
         "Sign convention: d_t = log p_A(y_t) - log p_B(y_t); positive favours A (the first-named model). "
         "NLL = -mean log score (lower is better). CRPS in return units (lower is better); "
         "dCRPS = CRPS_B - CRPS_A (positive favours A). DM: Newey-West HAC, Bartlett kernel; p1 = one-sided "
         "(H1: mean d > 0), p2 = two-sided. Bootstrap: stationary block, 2,000 replications, mean block 5, seed 42.", ""]
    for gid, (fr, desc, has_gjr) in gens.items():
        L += [f"## {gid}: {desc}", "", f"N = {len(fr)}; dates {fr['date'].iloc[0]} to {fr['date'].iloc[-1]}.", ""]
        ms = MODELS + (["GJR"] if has_gjr else [])
        L += ["| model | NLL | CRPS | PIT KS stat | PIT KS p | cov 50 | cov 80 | cov 95 | mean sigma | max sigma |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        cr = {}
        for m in ms:
            cr[m] = crps(fr, m)
            ks = stats.kstest(pit(fr, m), "uniform")
            L.append(f"| {m} | {-fr[f'{m}_log_p'].mean():.5f} | {cr[m].mean():.6f} | {ks.statistic:.4f} | {ks.pvalue:.4f} | "
                     f"{coverage(fr, m, .5):.3f} | {coverage(fr, m, .8):.3f} | {coverage(fr, m, .95):.3f} | "
                     f"{fr[f'{m}_sigma'].mean():.5f} | {fr[f'{m}_sigma'].max():.4f} |")
        L.append("")
        comps = CMP + (GJR_CMP if has_gjr else [])
        L += ["| comparison | A | B | NLL A | NLL B | mean d | HAC SE (5) | DM (5) | p1 (5) | p2 (5) | p1 (10) | p1 (21) | "
              "boot 95% CI | dCRPS | blocks d>0 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        extra = []
        for name, a, b in comps:
            d = (fr[f"{a}_log_p"] - fr[f"{b}_log_p"]).values
            dm = {k: diebold_mariano_test(d, max_lag=k) for k in (5, 10, 21)}
            bt = stationary_block_bootstrap(d, n_boot=2000, expected_block_len=5, seed=42)
            blk = pd.Series(d).groupby(fr["block"].values).mean()
            L.append(f"| {name} | {a} | {b} | {-fr[f'{a}_log_p'].mean():.5f} | {-fr[f'{b}_log_p'].mean():.5f} | {f(d.mean())} | "
                     f"{dm[5]['hac_se']:.5f} | {dm[5]['dm_stat']:.3f} | {dm[5]['p_value_one_sided']:.4f} | "
                     f"{dm[5]['p_value_two_sided']:.4f} | {dm[10]['p_value_one_sided']:.4f} | {dm[21]['p_value_one_sided']:.4f} | "
                     f"[{f(bt['ci_95_lower'])}, {f(bt['ci_95_upper'])}] | {f(cr[b].mean() - cr[a].mean(), 6)} | "
                     f"{int((blk > 0).sum())}/{len(blk)} |")
            yrs = pd.Series(d).groupby(pd.to_datetime(fr["date"]).dt.year.values).agg(["mean", "count"])
            row = f"| {name} | " + " | ".join(f"{y}: {f(r['mean'])} (n={int(r['count'])})" for y, r in yrs.iterrows())
            if gid in ("O-VAL", "R-VAL", "R-VALU"):
                ex = ~stress_mask(fr["date"].values)
                dme = diebold_mariano_test(d[ex], max_lag=5)
                row += f" | ex-stress {f(d[ex].mean())} (p1 {dme['p_value_one_sided']:.4f}, n={int(ex.sum())})"
            extra.append(row + " |")
        L += ["", "By year (and, for validation, excluding origins dated 2020-03-01 to 2020-04-30):", "",
              "| comparison | breakdown |", "|---|---|"] + [e.replace(" | ", " | ", 1) for e in extra] + [""]
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
