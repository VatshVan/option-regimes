import numpy as np
import pandas as pd
import pytest

from src.models.paired_comparisons import run_comparisons, stress_mask, summarize_differential


def _frame(n=84):
    dates = pd.bdate_range("2020-02-03", periods=n).strftime("%Y-%m-%d").tolist()
    blocks = np.arange(n) // 21
    return dates, blocks


def test_summary_breakdowns_are_exact():
    dates, blocks = _frame()
    d = np.random.default_rng(0).standard_normal(len(dates)) * 0.01
    s = summarize_differential(d, dates, blocks, n_boot=200)
    assert s["mean_d"] == pytest.approx(d.mean())
    for b in range(4):
        assert s["by_block"][str(b)]["mean_d"] == pytest.approx(d[blocks == b].mean())
    assert sum(v["n"] for v in s["by_block"].values()) == len(d)
    assert s["dm"]["lag_5"]["bandwidth_lags"] == 5 and s["dm"]["lag_21"]["bandwidth_lags"] == 21


def test_stress_mask_is_inclusive_window():
    m = stress_mask(["2020-02-28", "2020-03-02", "2020-04-30", "2020-05-01"])
    assert m.tolist() == [False, True, True, False]


def test_run_comparisons_sign_and_exclusion():
    dates, blocks = _frame()
    rng = np.random.default_rng(1)
    base = rng.standard_normal(len(dates))
    log_p = {m: base.copy() for m in ["B0", "B1", "B2", "B3", "B4", "R1"]}
    log_p["B4"] = base + 0.1  # B4 better than B3 everywhere
    res = run_comparisons(log_p, dates, blocks, exclude=stress_mask(dates))
    q1 = res["Q1_B4_vs_B3"]
    assert q1["full"]["mean_d"] == pytest.approx(0.1)
    assert q1["excluding_stress"]["excluded_rows"] == int(stress_mask(dates).sum())
    assert q1["excluding_stress"]["n"] == len(dates) - q1["excluding_stress"]["excluded_rows"]
    assert res["R1_vs_B4"]["full"]["mean_d"] == pytest.approx(-0.1)
