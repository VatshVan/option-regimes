"""
Tests for the Step 6 control options of build_refit_inputs / build_scoring_inputs.
Development data only.
"""
import numpy as np
import pandas as pd
import pytest

from src.models.walk_forward_pipeline import Q_COLS, X_COLS, build_refit_inputs, build_scoring_inputs
from tests.conftest import DEV_PATH


@pytest.fixture(scope="module")
def dev_df():
    return pd.read_csv(DEV_PATH)


def test_defaults_reproduce_primary_design(dev_df):
    tau = 2000
    score_idx = np.arange(tau + 1, tau + 22)
    r = build_refit_inputs(dev_df, tau, tau + 22)
    s = build_scoring_inputs(dev_df, r, score_idx)
    Q = r["scaler_Q"].transform(dev_df[Q_COLS].iloc[score_idx].values)
    X = r["scaler_X"].transform(dev_df[X_COLS].iloc[score_idx].values)
    np.testing.assert_array_equal(s["QX"], np.column_stack([Q, X]))
    np.testing.assert_array_equal(s["QXpi"], np.column_stack([Q, X, r["pi_eval"][score_idx]]))
    assert r["QXpi_train"].shape[1] == 13 and s["n_clipped"] == 0


def test_clipping_uses_training_quantiles(dev_df):
    tau = 2000
    score_idx = np.arange(tau + 1, tau + 22)
    r = build_refit_inputs(dev_df, tau, tau + 22, clip_quantiles=(0.005, 0.995))
    s = build_scoring_inputs(dev_df, r, score_idx)
    q_lo, q_hi = r["clip_bounds"]["Q"]
    np.testing.assert_allclose(q_hi, np.quantile(r["Q_train_scaled"], 0.995, axis=0))
    assert np.all(s["Q"] >= q_lo) and np.all(s["Q"] <= q_hi)
    # training rows are not clipped
    assert r["Q_train_scaled"].max() > q_hi.max() or r["Q_train_scaled"].min() < q_lo.min()
    unclipped = build_scoring_inputs(dev_df, build_refit_inputs(dev_df, tau, tau + 22), score_idx)
    inside = (unclipped["Q"] >= q_lo) & (unclipped["Q"] <= q_hi)
    np.testing.assert_array_equal(s["Q"][inside], unclipped["Q"][inside])


def test_q_column_subset_and_pi_state_selection(dev_df):
    tau = 2000
    q = [c for c in Q_COLS if c != "ATM_IV_30d"]
    r = build_refit_inputs(dev_df, tau, tau + 22, q_cols=q, r1_pi_states=[1])
    s = build_scoring_inputs(dev_df, r, np.arange(tau + 1, tau + 22))
    assert r["Q_train_scaled"].shape[1] == 4 and r["QXpi_train"].shape[1] == 4 + 6 + 1
    np.testing.assert_array_equal(r["QXpi_train"][:, -1], r["pi_eval"][r["train_sup_indices"], 1])
    assert s["QXpi"].shape[1] == 11


def test_pi_ablations(dev_df):
    tau, end = 2000, 2022
    base = build_refit_inputs(dev_df, tau, end)
    sh = build_refit_inputs(dev_df, tau, end, pi_ablation="shuffle")
    rv = build_refit_inputs(dev_df, tau, end, pi_ablation="rv_median")
    tr = base["train_sup_indices"]
    sc = np.arange(tau + 1, end)
    np.testing.assert_array_equal(sh["pi_eval"], base["pi_eval"])  # true filter output untouched
    for rows in (tr, sc):  # permutation within training rows and within the scoring block
        assert not np.array_equal(sh["pi_r1"][rows], base["pi_eval"][rows])
        np.testing.assert_array_equal(np.sort(sh["pi_r1"][rows, 1]), np.sort(base["pi_eval"][rows, 1]))
    np.testing.assert_array_equal(sh["QXpi_train"][:, -2:], sh["pi_r1"][tr])
    thr = np.median(dev_df["rv_20d"].values[tr])
    np.testing.assert_array_equal(rv["pi_r1"][:, 1], (dev_df["rv_20d"].values[:end] > thr).astype(float))
    np.testing.assert_array_equal(rv["pi_r1"].sum(axis=1), 1.0)
    s = build_scoring_inputs(dev_df, rv, sc)
    np.testing.assert_array_equal(s["QXpi"][:, -1], rv["pi_r1"][sc, 1])
