"""
paired_comparisons.py
=====================
Paired log-score comparisons between density models (CLAUDE_CODE_HANDOFF.md Section 3).

For models A (challenger) and B (comparator) scored on the same rows,
d_t = log p_A(y_t) - log p_B(y_t); positive d favours A.
"""

from typing import Any, Dict, Optional, Sequence

import numpy as np
import pandas as pd

from src.models.evaluation_metrics import diebold_mariano_test, stationary_block_bootstrap

# (name, challenger A, comparator B, question)
COMPARISONS = [
    ("Q1_B4_vs_B3", "B4", "B3", "Incremental option-implied Q over historical P-state X"),
    ("Q2a_B2_vs_B1", "B2", "B1", "Q alone vs trailing-RV Student-t"),
    ("Q2b_B2_vs_B0", "B2", "B0", "Q alone vs unconditional Gaussian"),
    ("Q3_B3_vs_B1", "B3", "B1", "X alone vs trailing-RV Student-t"),
    ("R1_vs_B4", "R1", "B4", "Regime probabilities over Q + X (secondary)"),
]
HAC_LAGS = (5, 10, 21)
STRESS_WINDOW = ("2020-03-01", "2020-04-30")


def summarize_differential(
    d: np.ndarray,
    dates: Sequence[str],
    block_ids: Sequence[int],
    hac_lags: Sequence[int] = HAC_LAGS,
    n_boot: int = 2000,
    expected_block_len: int = 5,
    seed: int = 42,
    with_breakdown: bool = True,
) -> Dict[str, Any]:
    """Mean, HAC DM at several lags, stationary bootstrap CI, and per-year / per-block means."""
    d = np.asarray(d, dtype=np.float64)
    assert np.all(np.isfinite(d)), "differential contains non-finite values"
    dates = pd.to_datetime(pd.Series(list(dates)))
    out = {
        "n": int(len(d)),
        "mean_d": float(np.mean(d)),
        "dm": {f"lag_{L}": diebold_mariano_test(d, max_lag=L) for L in hac_lags},
        "bootstrap": stationary_block_bootstrap(d, n_boot=n_boot, expected_block_len=expected_block_len, seed=seed),
    }
    if with_breakdown:
        frame = pd.DataFrame({"d": d, "year": dates.dt.year.values, "block": np.asarray(block_ids)})
        out["by_year"] = {str(y): {"n": int(len(g)), "mean_d": float(g["d"].mean())} for y, g in frame.groupby("year")}
        blocks = frame.groupby("block")["d"].agg(["count", "mean"])
        out["by_block"] = {str(b): {"n": int(r["count"]), "mean_d": float(r["mean"])} for b, r in blocks.iterrows()}
        out["n_blocks_positive"] = int((blocks["mean"] > 0).sum())
        out["n_blocks"] = int(len(blocks))
    return out


def stress_mask(dates: Sequence[str], window=STRESS_WINDOW) -> np.ndarray:
    """True for origins inside the stress window (inclusive)."""
    dt = pd.to_datetime(pd.Series(list(dates)))
    return ((dt >= pd.Timestamp(window[0])) & (dt <= pd.Timestamp(window[1]))).values


def run_comparisons(
    log_p: Dict[str, np.ndarray],
    dates: Sequence[str],
    block_ids: Sequence[int],
    comparisons=COMPARISONS,
    exclude: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """
    All paired comparisons on the full scored sample and, if exclude is given, on the
    sample without the excluded rows (e.g. stress_mask(dates)).
    """
    dates = np.asarray(list(dates))
    block_ids = np.asarray(block_ids)
    results = {}
    for name, a, b, question in comparisons:
        d = np.asarray(log_p[a]) - np.asarray(log_p[b])
        entry = {"challenger": a, "comparator": b, "question": question,
                 "full": summarize_differential(d, dates, block_ids)}
        if exclude is not None:
            keep = ~np.asarray(exclude)
            entry["excluding_stress"] = summarize_differential(d[keep], dates[keep], block_ids[keep])
            entry["excluding_stress"]["excluded_rows"] = int((~keep).sum())
        results[name] = entry
    return results
