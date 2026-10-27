"""
run_step6_sigma_controls.py
===========================
Step 6 (fix/optimizer-calibration): sigma-extrapolation controls, evaluated with the
pre-declared rule in output/stage7_models_v2/step6_decision_rule.md (committed before
this script was run). Development + validation data only; the test file is never loaded.

Baseline: Step 5 primary run (validation_predictions_primary_v2.csv, lambda 1e-4, K 2).
Controls: (a) scoring-time clipping to training [0.5%, 99.5%] quantiles; (b1)/(b2) drop
ATM_IV_30d / QKurt_30d, run only if (a) fails criterion 1; (c) R1 with pi_1 only, always
run, and also combined with any adopted control.

Each run must pass the convergence gate, and every model the control does not touch
must reproduce the baseline log scores exactly (|delta log p| < 1e-10).

Run from the repository root: python scratch/run_step6_sigma_controls.py
"""
import json
import os
import sys
import time
import warnings

sys.path.insert(0, ".")
import numpy as np
import pandas as pd

from src.models.evaluation_metrics import diebold_mariano_test
from src.models.paired_comparisons import COMPARISONS, run_comparisons, stress_mask
from src.models.walk_forward_pipeline import Q_COLS, load_datasets, run_walk_forward

OUT_DIR = "output/stage7_models_v2"
BASELINE = f"{OUT_DIR}/validation_predictions_primary_v2.csv"
LAMBDA, K = 1e-4, 2
MODELS = ["B0", "B1", "B2", "B3", "B4", "R1"]
SIGMA_MAX = 0.10          # criterion 1
NLL_TOL = 0.005           # criterion 2a
DM_ALPHA = 0.05           # criterion 2b (one-sided, worse direction, HAC 5 lags)
REPRO_TOL = 1e-10

CONTROLS = {
    "a_clip": {"kwargs": {"clip_quantiles": (0.005, 0.995)}, "applies_to": ["B2", "B3", "B4", "R1"]},
    "b1_drop_ATM_IV_30d": {"kwargs": {"q_cols": [c for c in Q_COLS if c != "ATM_IV_30d"]}, "applies_to": ["B2", "B4", "R1"]},
    "b2_drop_QKurt_30d": {"kwargs": {"q_cols": [c for c in Q_COLS if c != "QKurt_30d"]}, "applies_to": ["B2", "B4", "R1"]},
    "c_r1_pi1_only": {"kwargs": {"r1_pi_states": [1]}, "applies_to": ["R1"]},
}


def run_control(name, kwargs, applies_to, df_all, n_dev, base, dates, excl):
    print(f"\n=== control {name}: {kwargs} ===")
    res = run_walk_forward(df_all, val_start_idx=n_dev, K_regimes=K, lambda_reg=LAMBDA, **kwargs)
    vi = res["val_indices"]
    assert list(df_all["date"].values[vi]) == list(dates)
    fails = [(b["refit_date"], m) for b in res["refit_diagnostics"] for m, r in b["fit_reports"].items() if not r["converged"]]
    fails += [(b["refit_date"], "HMM") for b in res["refit_diagnostics"] if not b["hmm_converged"]]
    if fails:
        raise SystemExit(f"Convergence gate failed for {name}: {fails}")

    log_p = {m: res["preds"][m]["log_p"][vi] for m in MODELS}
    sigma = {m: res["preds"][m]["sigma"][vi] for m in MODELS}
    untouched = [m for m in MODELS if m not in applies_to]
    repro = {m: float(np.max(np.abs(log_p[m] - base[f"{m}_log_p"].values))) for m in untouched}
    bad = {m: v for m, v in repro.items() if v > REPRO_TOL}
    if bad:
        raise SystemExit(f"{name}: untouched models do not reproduce the baseline: {bad}")

    crit1 = {m: float(np.max(sigma[m][excl])) for m in applies_to}
    crit2 = {}
    for m in ["B2", "B3", "B4"]:
        if m not in applies_to:
            continue
        d = log_p[m] - base[f"{m}_log_p"].values
        worse = diebold_mariano_test(-d, max_lag=5)  # H1: mean d < 0 (control worse)
        crit2[m] = {
            "nll_change": float(-np.mean(d)),
            "dm_p_worse_one_sided_lag5": float(worse["p_value_one_sided"]),
            "pass": bool(-np.mean(d) <= NLL_TOL and worse["p_value_one_sided"] >= DM_ALPHA),
        }
    c1_pass = all(v < SIGMA_MAX for v in crit1.values())
    c2_pass = all(v["pass"] for v in crit2.values())
    n_clipped = int(sum(b["n_scoring_feature_values_clipped"] for b in res["refit_diagnostics"]))

    out = {
        "kwargs": {k: list(v) if isinstance(v, (list, tuple)) else v for k, v in kwargs.items()},
        "applies_to": applies_to,
        "reproduction_check_untouched_models": repro,
        "criterion1_max_sigma_mar_apr_2020": crit1,
        "criterion1_pass": c1_pass,
        "criterion2": crit2,
        "criterion2_pass": c2_pass,
        "adopted": bool(c1_pass and c2_pass),
        "n_scoring_feature_values_clipped": n_clipped,
        "nll": {m: float(-np.mean(log_p[m])) for m in MODELS},
        "nll_ex_stress": {m: float(-np.mean(log_p[m][~excl])) for m in MODELS},
        "max_sigma": {m: float(np.max(sigma[m])) for m in MODELS},
        "comparisons": run_comparisons(log_p, dates, base["block"].values, exclude=excl),
    }
    pred = base[["date", "block", "target_y", "stress_window"]].copy()
    for m in MODELS:
        for f in ["mu", "sigma", "nu", "log_p"]:
            pred[f"{m}_{f}"] = res["preds"][m][f][vi]
    pred.to_csv(f"{OUT_DIR}/step6_predictions_{name}.csv", index=False)
    print(f"{name}: crit1 {crit1} -> {c1_pass}; crit2 {crit2} -> {c2_pass}; adopted={out['adopted']}")
    return out


def main():
    t0 = time.time()
    warnings.simplefilter("always", RuntimeWarning)
    df_dev, df_val = load_datasets()
    df_all = pd.concat([df_dev, df_val], ignore_index=True)
    n_dev = len(df_dev)
    base = pd.read_csv(BASELINE)
    dates = base["date"].values
    excl = stress_mask(dates)
    assert np.array_equal(excl, base["stress_window"].values)

    base_logp = {m: base[f"{m}_log_p"].values for m in MODELS}
    results = {"baseline": {
        "nll": {m: float(-np.mean(base_logp[m])) for m in MODELS},
        "max_sigma": {m: float(base[f"{m}_sigma"].max()) for m in MODELS},
        "max_sigma_mar_apr_2020": {m: float(base.loc[excl, f"{m}_sigma"].max()) for m in MODELS},
        "comparisons": run_comparisons(base_logp, dates, base["block"].values, exclude=excl),
    }}
    order = ["a_clip"]
    results["a_clip"] = run_control("a_clip", **CONTROLS["a_clip"], df_all=df_all, n_dev=n_dev, base=base, dates=dates, excl=excl)
    if not results["a_clip"]["criterion1_pass"]:
        for b in ["b1_drop_ATM_IV_30d", "b2_drop_QKurt_30d"]:
            results[b] = run_control(b, **CONTROLS[b], df_all=df_all, n_dev=n_dev, base=base, dates=dates, excl=excl)
            order.append(b)
    results["c_r1_pi1_only"] = run_control("c_r1_pi1_only", **CONTROLS["c_r1_pi1_only"], df_all=df_all, n_dev=n_dev,
                                           base=base, dates=dates, excl=excl)
    order.append("c_r1_pi1_only")
    adopted = [n for n in order if n != "c_r1_pi1_only" and results[n]["adopted"]]
    for n in adopted:
        combo = f"c_r1_pi1_only+{n}"
        kw = {**CONTROLS[n]["kwargs"], **CONTROLS["c_r1_pi1_only"]["kwargs"]}
        results[combo] = run_control(combo, kw, CONTROLS[n]["applies_to"], df_all, n_dev, base, dates, excl)
        order.append(combo)

    summary = {"rule_file": f"{OUT_DIR}/step6_decision_rule.md", "lambda": LAMBDA, "K": K,
               "run_order": order, "adopted_controls": adopted,
               "thresholds": {"sigma_max": SIGMA_MAX, "nll_tol": NLL_TOL, "dm_alpha": DM_ALPHA}}
    with open(f"{OUT_DIR}/step6_sigma_controls.json", "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    print(f"\nadopted controls: {adopted}")
    print(f"{'run':30s} " + " ".join(f"{n:>13s}" for n, *_ in COMPARISONS) + "   (mean d, DM p lag5)")
    for run in ["baseline"] + order:
        c = results[run]["comparisons"]
        print(f"{run:30s} " + " ".join(f"{c[n]['full']['mean_d']:+.4f}/{c[n]['full']['dm']['lag_5']['p_value_one_sided']:.3f}" for n, *_ in COMPARISONS))
    print(f"\ndone in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
