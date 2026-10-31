"""
check_step3_convergence.py
==========================
Step 3 (fix/optimizer-calibration) acceptance check for the float64 / preconditioned
StudentTRegression fit. Development and validation data only; writes one JSON report.

For the in-sample development fit and the six representative validation refits
(the optimizer-audit notes Section 5, tau = 2515 + 21k, k in {0, 3, 6, 12, 18, 23}),
for each of B2, B3, B4, R1:
  1. gap of the penalised objective to an independent SciPy float64 optimum (< 1e-6)
  2. three random starts (natural-scale perturbations, see random_start_fit): objective
     difference, and max |delta log p| on the scoring
     block (predictions must agree to < 1e-6; R1's design is exactly singular
     (pi_0 + pi_1 = 1, defect 1e.3), so its objective is nearly flat along a direction
     that changes only the penalty, never the predictions)
  3. one-label perturbation (drop one training label, refit):
       - optimizer component: max |log p_torch - log p_reference| on the dropped-label refit
         (< 1e-6 means the optimizer adds no instability beyond statistical influence)
       - mean |delta log p| for torch and for the reference, and the ratio to B0
         (reported; the handoff's "within 3x of B0" is a heuristic, not a pass criterion,
         because a 24-parameter model has more single-label influence than B0's 2)
  4. B4 nu (handoff: ~5.5-5.8)
Only rows with valid_supervised_pair_all5 are scored.

Run from the repository root: python scratch/check_step3_convergence.py
"""
import json
import os
import sys
import warnings

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import torch

from src.models.density_models import ModelB0_UnconditionalGaussian, StudentTRegression
from src.models.walk_forward_pipeline import Q_COLS, X_COLS, build_refit_inputs, load_datasets
from tests.reference_optimizer import reference_log_density, reference_optimum

LAM = 0.01
TOL = 1e-6
OUT = "output/stage7_models_v2/step3_convergence_check.json"
warnings.simplefilter("error", RuntimeWarning)  # any non-converged fit aborts the check


def designs(refit):
    return {"B2": refit["Q_train_scaled"], "B3": refit["X_train_scaled"],
            "B4": refit["QX_train_scaled"], "R1": refit["QXpi_train"]}


def random_start_fit(X, y, rng):
    """
    Random start at the model's natural scale: mu-weights N(0, 0.1) in preconditioned units
    (theta_mu = sd(y) * phi, i.e. 0.1 sd(y) per unit robust-z), sigma-weights N(0, 0.1),
    raw_nu U(0.5, 4) (nu in ~[3.1, 6.1]). fit() resets both biases to their data-based
    initial values; weights and raw_nu stay random.
    """
    m = StudentTRegression(in_features=X.shape[1], l2_reg=LAM)
    s = float(np.std(y, ddof=1))
    with torch.no_grad():
        m.fc_mu.weight.copy_(torch.as_tensor(s * 0.1 * rng.standard_normal(m.fc_mu.weight.shape)))
        m.fc_sig.weight.copy_(torch.as_tensor(0.1 * rng.standard_normal(m.fc_sig.weight.shape)))
        m.raw_nu.fill_(float(rng.uniform(0.5, 4.0)))
    return m.fit(X, y)


def score_block(df, refit, score_idx):
    Q = refit["scaler_Q"].transform(df[Q_COLS].iloc[score_idx].values)
    X = refit["scaler_X"].transform(df[X_COLS].iloc[score_idx].values)
    pi = refit["pi_eval"][score_idx]  # start_train_idx = 0
    return {"B2": Q, "B3": X, "B4": np.column_stack([Q, X]), "R1": np.column_stack([Q, X, pi])}


def maxabs(a, b):
    return float(np.max(np.abs(a - b)))


def main():
    df_dev, df_val = load_datasets()
    df_all = pd.concat([df_dev, df_val], ignore_index=True)
    n_dev = len(df_dev)
    rng = np.random.default_rng(2024)
    report = []

    # Development case: last dev row as refit origin on dev data only; scored in-sample on its own training rows
    cases = [("dev_insample", df_dev, n_dev - 1)]
    cases += [(f"val_k{k}", df_all, n_dev - 1 + 21 * k) for k in [0, 3, 6, 12, 18, 23]]
    for name, df, tau in cases:
        score_end = min(len(df), tau + 1 + 21)
        refit = build_refit_inputs(df, tau, score_end)
        y = refit["y_train"]
        drop = int(rng.integers(len(y)))
        keep = np.delete(np.arange(len(y)), drop)
        if name == "dev_insample":
            y_score, Xs = y, designs(refit)
        else:
            score_idx = np.arange(tau + 1, score_end)
            score_idx = score_idx[df["valid_supervised_pair_all5"].values[score_idx]]
            y_score, Xs = df["target_y_next2"].values[score_idx], score_block(df, refit, score_idx)
        assert np.all(np.isfinite(y_score))

        b0_full = ModelB0_UnconditionalGaussian().fit(y).log_density(y_score)
        b0_drop = ModelB0_UnconditionalGaussian().fit(y[keep]).log_density(y_score)
        b0_pert = float(np.mean(np.abs(b0_full - b0_drop)))

        row = {"case": name, "tau": int(tau), "refit_date": str(df["date"].iloc[tau]),
               "n_train": int(len(y)), "n_scored": int(len(y_score)), "dropped_label_pos": drop,
               "b0_one_label_mean_abs_dlogp": b0_pert, "models": {}}
        for mname, X in designs(refit).items():
            Xsc = Xs[mname]
            m = StudentTRegression(in_features=X.shape[1], l2_reg=LAM).fit(X, y)
            rep = m.fit_report_
            logp = m.log_density(Xsc, y_score)
            f_ref, th_ref = reference_optimum(X, y, LAM)

            starts = [random_start_fit(X, y, rng) for _ in range(3)]
            start_obj = max(abs(s.fit_report_["penalized_loss"] - rep["penalized_loss"]) for s in starts)
            start_pred = max(maxabs(s.log_density(Xsc, y_score), logp) for s in starts)

            m_drop = StudentTRegression(in_features=X.shape[1], l2_reg=LAM).fit(X[keep], y[keep])
            _, th_ref_drop = reference_optimum(X[keep], y[keep], LAM)
            logp_drop = m_drop.log_density(Xsc, y_score)
            ref_logp, ref_logp_drop = reference_log_density(th_ref, Xsc, y_score), reference_log_density(th_ref_drop, Xsc, y_score)
            pert = float(np.mean(np.abs(logp - logp_drop)))
            row["models"][mname] = {
                "n_iter": rep["n_iter"], "func_evals": rep["func_evals"], "lbfgs_rounds": rep["lbfgs_rounds"],
                "newton_steps": rep["newton_steps"], "hessian_min_eig": rep["hessian_min_eig"],
                "hessian_max_eig": rep["hessian_max_eig"],
                "stop_reason": rep["stop_reason"], "converged": rep["converged"],
                "max_abs_grad": rep["max_abs_grad"],
                "penalized_loss": rep["penalized_loss"], "reference_loss": float(f_ref),
                "gap_to_reference": rep["penalized_loss"] - float(f_ref),
                "max_abs_dlogp_vs_reference": maxabs(logp, ref_logp),
                "random_start_max_abs_dobjective": float(start_obj),
                "random_start_max_abs_dlogp": float(start_pred),
                "random_start_stop_reasons": [s.fit_report_["stop_reason"] for s in starts],
                "nu": rep["nu"],
                "one_label_mean_abs_dlogp": pert,
                "one_label_mean_abs_dlogp_reference": float(np.mean(np.abs(ref_logp - ref_logp_drop))),
                "one_label_optimizer_component": maxabs(logp_drop, ref_logp_drop),
                "one_label_ratio_to_b0": pert / b0_pert,
            }
        report.append(row)
        print(name, row["refit_date"], {
            mn: (r["stop_reason"], r["n_iter"], f"gap={r['gap_to_reference']:+.1e}",
                 f"start_dlogp={r['random_start_max_abs_dlogp']:.1e}", f"nu={r['nu']:.3f}",
                 f"pert={r['one_label_mean_abs_dlogp']:.1e}", f"opt={r['one_label_optimizer_component']:.1e}",
                 f"/B0={r['one_label_ratio_to_b0']:.2f}")
            for mn, r in row["models"].items()})

    fits = [r for row in report for r in row["models"].values()]
    checks = {
        "all_converged": all(r["converged"] for r in fits),
        "max_abs_gap_to_reference": max(abs(r["gap_to_reference"]) for r in fits),
        "max_abs_dlogp_vs_reference": max(r["max_abs_dlogp_vs_reference"] for r in fits),
        "max_random_start_dlogp": max(r["random_start_max_abs_dlogp"] for r in fits),
        "max_random_start_dobjective": max(r["random_start_max_abs_dobjective"] for r in fits),
        "max_one_label_optimizer_component": max(r["one_label_optimizer_component"] for r in fits),
        "max_one_label_ratio_to_b0_reported": max(r["one_label_ratio_to_b0"] for r in fits),
        "b4_nu_range": [min(row["models"]["B4"]["nu"] for row in report), max(row["models"]["B4"]["nu"] for row in report)],
    }
    checks["pass"] = bool(
        checks["all_converged"]
        and checks["max_abs_gap_to_reference"] < TOL
        and checks["max_abs_dlogp_vs_reference"] < TOL
        and checks["max_random_start_dlogp"] < TOL
        and checks["max_one_label_optimizer_component"] < TOL
    )
    print(json.dumps(checks, indent=2))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"lambda": LAM, "tolerance": TOL, "checks": checks, "cases": report}, f, indent=2)
    print("saved", OUT)


if __name__ == "__main__":
    main()
