"""
check_step4_hmm_b1_b0.py
========================
Step 4 (fix/optimizer-calibration) check. Validation data only; writes one JSON report.

For each of the 25 primary validation refits (K=2), compares against the saved Stage 7
record (output/stage7_models/hmm_refit_diagnostics_primary.json and
validation_predictions_primary.csv):
  - HMM with the true-log-likelihood monitor: iterations, convergence, max |delta A|,
    and max |delta pi| on the validation rows the refit scores
  - B1 with the float64 / preconditioned / Newton-polished fit: convergence and nu
Also recomputes the B0 validation PIT KS test with per-row parameters from the saved B0
predictions (B0 is closed form and unchanged) and the previously reported value.

Run from the repository root: python scratch/check_step4_hmm_b1_b0.py
"""
import json
import os
import sys
import warnings

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
from scipy import stats

from src.models.density_models import ModelB1_RVLocationScaleStudentT
from src.models.walk_forward_pipeline import build_refit_inputs, load_datasets

OUT = "output/stage7_models_v2/step4_hmm_b1_b0_check.json"
SAVED_DIAG = "output/stage7_models/hmm_refit_diagnostics_primary.json"
SAVED_PREDS = "output/stage7_models/validation_predictions_primary.csv"
SAVED_SUMMARY = "output/stage7_models/validation_metrics_summary.json"
warnings.simplefilter("error", RuntimeWarning)


def main():
    df_dev, df_val = load_datasets()
    df_all = pd.concat([df_dev, df_val], ignore_index=True)
    n_dev = len(df_dev)
    saved_blocks = json.load(open(SAVED_DIAG))["blocks"]
    saved_preds = pd.read_csv(SAVED_PREDS)
    saved_pi = dict(zip(saved_preds["date"], saved_preds[["pi_state_0", "pi_state_1"]].values))

    rows = []
    for blk in saved_blocks:
        tau = blk["refit_origin_tau"]
        score_start, score_end = blk["scoring_window"]["score_start_idx"], blk["scoring_window"]["score_end_idx"]
        refit = build_refit_inputs(df_all, tau, score_end)
        hmm = refit["hmm"]
        idx = np.arange(score_start, score_end)
        idx = idx[df_all["valid_supervised_pair_all5"].values[idx]]
        pi_new = refit["pi_eval"][idx]
        pi_old = np.array([saved_pi[d] for d in df_all["date"].values[idx]])
        b1 = ModelB1_RVLocationScaleStudentT().fit(refit["rv_train"], refit["y_train"])
        rows.append({
            "refit_date": blk["refit_date"],
            "hmm_n_iter": hmm.n_iter_,
            "hmm_converged": hmm.converged_,
            "hmm_final_log_lik": hmm.log_lik_history_[-1],
            "max_abs_dA": float(np.max(np.abs(hmm.trans_mat - np.array(blk["hmm_transition_matrix"])))),
            "max_abs_dpi_scored": float(np.max(np.abs(pi_new - pi_old))) if len(idx) else 0.0,
            "mean_abs_dpi_scored": float(np.mean(np.abs(pi_new - pi_old))) if len(idx) else 0.0,
            "dwell_new": [float(x) for x in hmm.compute_dwell_times()],
            "dwell_saved": blk["hmm_expected_dwell_times"],
            "b1_converged": b1.fit_report_["converged"],
            "b1_n_iter": b1.fit_report_["n_iter"],
            "b1_newton_steps": b1.fit_report_["newton_steps"],
            "b1_max_abs_grad": b1.fit_report_["max_abs_grad"],
            "b1_nu": b1.nu,
            "b1_nu_saved": float(saved_preds.loc[saved_preds["date"].isin(df_all["date"].values[idx]), "B1_nu"].iloc[0]) if len(idx) else None,
            "b1_insample_nll": b1.fit_report_["unpenalized_nll"],
        })
        r = rows[-1]
        print(f"{r['refit_date']}: HMM iter={r['hmm_n_iter']:2d} conv={r['hmm_converged']} "
              f"max|dA|={r['max_abs_dA']:.1e} max|dpi|={r['max_abs_dpi_scored']:.1e} | "
              f"B1 conv={r['b1_converged']} nu={r['b1_nu']:.3f} (saved {r['b1_nu_saved']})")

    y = saved_preds["target_y"].values
    ks_per_row = stats.kstest(stats.norm.cdf(y, saved_preds["B0_mu"].values, saved_preds["B0_sigma"].values), "uniform")
    ks_row0 = stats.kstest(stats.norm.cdf(y, saved_preds["B0_mu"].values[0], saved_preds["B0_sigma"].values[0]), "uniform")
    reported = json.load(open(SAVED_SUMMARY))
    reported_b0 = reported["metrics"]["B0"]["pit_ks_pvalue"]

    summary = {
        "hmm_all_converged": all(r["hmm_converged"] for r in rows),
        "hmm_n_iter_range": [min(r["hmm_n_iter"] for r in rows), max(r["hmm_n_iter"] for r in rows)],
        "hmm_max_abs_dA": max(r["max_abs_dA"] for r in rows),
        "hmm_max_abs_dpi_scored": max(r["max_abs_dpi_scored"] for r in rows),
        "b1_all_converged": all(r["b1_converged"] for r in rows),
        "b1_nu_range": [min(r["b1_nu"] for r in rows), max(r["b1_nu"] for r in rows)],
        "b0_val_pit_ks_pvalue_per_row": float(ks_per_row.pvalue),
        "b0_val_pit_ks_stat_per_row": float(ks_per_row.statistic),
        "b0_val_pit_ks_pvalue_row0_bug": float(ks_row0.pvalue),
        "b0_val_pit_ks_pvalue_reported_stage7": reported_b0,
    }
    print(json.dumps(summary, indent=2))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"summary": summary, "refits": rows}, f, indent=2)
    print("saved", OUT)


if __name__ == "__main__":
    main()
