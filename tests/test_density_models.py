"""
Unit tests for src/models/density_models.py and the evaluation path in
src/models/walk_forward_pipeline.py.

Tests marked xfail(strict=True) document confirmed defects in the current code
(CLAUDE_CODE_HANDOFF.md Sections 1b, 1e). They must start passing once the
corresponding fix lands, at which point strict xfail fails and the marker
must be removed.
"""
import math

import numpy as np
import pandas as pd
import pytest
import torch
from scipy import stats

from src.models.density_models import (
    ModelB0_UnconditionalGaussian,
    ModelB1_RVLocationScaleStudentT,
    StudentTRegression,
)
from src.models.walk_forward_pipeline import Q_COLS, X_COLS, run_walk_forward
from tests.reference_optimizer import objective_and_grad, reference_optimum

LAM = 0.01


def _set_params(model, w_mu, b_mu, w_sig, b_sig, raw_nu):
    with torch.no_grad():
        model.fc_mu.weight.copy_(torch.as_tensor(w_mu).reshape(1, -1))
        model.fc_mu.bias.fill_(b_mu)
        model.fc_sig.weight.copy_(torch.as_tensor(w_sig).reshape(1, -1))
        model.fc_sig.bias.fill_(b_sig)
        model.raw_nu.fill_(raw_nu)


def _synthetic(n=3000, d=3, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, d))
    w_mu = np.array([0.002, -0.001, 0.0])[:d]
    w_sig = np.array([0.3, 0.0, -0.2])[:d]
    mu = X @ w_mu + 0.0005
    sig = np.logaddexp(0, X @ w_sig + math.log(math.expm1(0.01))) + 1e-4
    y = mu + sig * rng.standard_t(6.0, size=n)
    return X, y, w_mu, w_sig


# ---------------------------------------------------------------- density

def test_log_density_matches_scipy_float64():
    rng = np.random.default_rng(1)
    d = 4
    X = rng.standard_normal((200, d))
    y = 0.01 * rng.standard_t(5, size=200)
    m = StudentTRegression(in_features=d, l2_reg=0.0).double()
    w_mu, w_sig = 1e-3 * rng.standard_normal(d), 0.2 * rng.standard_normal(d)
    _set_params(m, w_mu, 2e-4, w_sig, -4.5, 1.3)
    with torch.no_grad():
        nll = float(m.unpenalized_nll(torch.tensor(X), torch.tensor(y)))
    mu = X @ w_mu + 2e-4
    sig = np.logaddexp(0, X @ w_sig - 4.5) + 1e-4
    nu = np.logaddexp(0, 1.3) + 2.1
    ref = -stats.t.logpdf(y, df=nu, loc=mu, scale=sig).mean()
    assert abs(nll - ref) < 1e-12


def test_log_density_method_matches_scipy():
    X, y, _, _ = _synthetic(n=500, seed=2)
    m = StudentTRegression(in_features=3, l2_reg=LAM).fit(X, y)
    mu, sig, nu = m.predict(X)
    np.testing.assert_allclose(m.log_density(X, y), stats.t.logpdf(y, df=nu, loc=mu, scale=sig), rtol=0, atol=1e-12)


def test_penalized_objective_matches_reference_implementation():
    rng = np.random.default_rng(3)
    d = 3
    X = rng.standard_normal((300, d))
    y = 0.01 * rng.standard_t(5, size=300)
    theta = np.concatenate([[1.1], 1e-3 * rng.standard_normal(d), [1e-4], 0.1 * rng.standard_normal(d), [-4.4]])
    m = StudentTRegression(in_features=d, l2_reg=LAM).double()
    _set_params(m, theta[1:1 + d], theta[1 + d], theta[2 + d:2 + 2 * d], theta[2 + 2 * d], theta[0])
    with torch.no_grad():
        f_torch = float(m.nll_loss(torch.tensor(X), torch.tensor(y)))
    f_ref, _ = objective_and_grad(theta, X, y, LAM)
    assert abs(f_torch - f_ref) < 1e-12


def test_autograd_matches_finite_differences_float64():
    rng = np.random.default_rng(4)
    d = 3
    X = torch.tensor(rng.standard_normal((100, d)))
    y = torch.tensor(0.01 * rng.standard_t(5, size=100))
    m = StudentTRegression(in_features=d, l2_reg=LAM).double()
    _set_params(m, 1e-3 * rng.standard_normal(d), 1e-4, 0.2 * rng.standard_normal(d), -4.5, 1.0)

    # module autograd vs central finite differences of the module objective
    loss = m.nll_loss(X, y)
    grads = torch.autograd.grad(loss, list(m.parameters()))
    h = 1e-7
    for p, g in zip(m.parameters(), grads):
        flat = p.data.view(-1)
        for i in range(flat.numel()):
            orig = float(flat[i])
            flat[i] = orig + h
            with torch.no_grad():
                fp = float(m.nll_loss(X, y))
            flat[i] = orig - h
            with torch.no_grad():
                fm = float(m.nll_loss(X, y))
            flat[i] = orig
            assert (fp - fm) / (2 * h) == pytest.approx(float(g.view(-1)[i]), abs=1e-6, rel=1e-5)


def _extreme_input_predictions():
    m = StudentTRegression(in_features=2, l2_reg=LAM)
    _set_params(m, [0.0, 0.0], 0.0, [5.0, -5.0], 0.0, -50.0)
    X = np.array([[-1e3, 1e3], [1e3, -1e3], [0.0, 0.0]])
    return m, m.predict(X)


def test_sigma_bounds_under_extreme_inputs():
    m, (_, sig, _) = _extreme_input_predictions()
    assert np.all(np.isfinite(sig))
    assert np.all(sig >= np.float32(m.sigma_min))


@pytest.mark.xfail(strict=True, reason="float32: softplus(raw_nu)+2.1 rounds to 2.0999999 < 2.1 (fixed by float64 in Step 3)")
def test_nu_lower_bound_under_extreme_inputs():
    _, (_, _, nu) = _extreme_input_predictions()
    assert np.all(nu >= 2.1)


# ---------------------------------------------------------------- fitting

def test_synthetic_parameter_recovery():
    X, y, w_mu, w_sig = _synthetic(n=20000, seed=5)
    m = StudentTRegression(in_features=3, l2_reg=0.0).fit(X, y)
    np.testing.assert_allclose(m.fc_sig.weight.detach().numpy().ravel(), w_sig, atol=0.05)
    np.testing.assert_allclose(m.fc_mu.weight.detach().numpy().ravel(), w_mu, atol=3e-4)
    assert 4.0 < m.fit_report_["nu"] < 9.0


def test_fit_is_deterministic(dev_design):
    a = StudentTRegression(in_features=11, l2_reg=LAM).fit(dev_design["QX"], dev_design["y"])
    b = StudentTRegression(in_features=11, l2_reg=LAM).fit(dev_design["QX"], dev_design["y"])
    for pa, pb in zip(a.parameters(), b.parameters()):
        assert torch.equal(pa, pb)
    b1a = ModelB1_RVLocationScaleStudentT().fit(dev_design["rv"], dev_design["y"])
    b1b = ModelB1_RVLocationScaleStudentT().fit(dev_design["rv"], dev_design["y"])
    assert (b1a.mu, b1a.alpha_0, b1a.alpha_1, b1a.nu) == (b1b.mu, b1b.alpha_0, b1b.alpha_1, b1b.nu)


def test_fit_report_fields(dev_design):
    m = StudentTRegression(in_features=5, l2_reg=LAM).fit(dev_design["Q"], dev_design["y"])
    r = m.fit_report_
    for key in ["n_iter", "func_evals", "stop_reason", "converged", "penalized_loss",
                "unpenalized_nll", "max_abs_grad", "nu"]:
        assert key in r
    assert r["penalized_loss"] >= r["unpenalized_nll"]
    assert r["nu"] == pytest.approx(float(m.predict(dev_design["Q"][:1])[2][0]))


@pytest.mark.xfail(strict=True, reason="Root cause 1: torch LBFGS max_iter=60 float32 stops far from the optimum (handoff 1b)")
def test_fit_reaches_reference_optimum(dev_design):
    m = StudentTRegression(in_features=11, l2_reg=LAM).fit(dev_design["QX"], dev_design["y"])
    f_ref, _ = reference_optimum(dev_design["QX"], dev_design["y"], LAM)
    assert m.fit_report_["converged"]
    assert m.fit_report_["penalized_loss"] - f_ref < 1e-6


@pytest.mark.xfail(strict=True, reason="Root cause 2: unequal optimisation error breaks nesting B4 >= B2, B3 (handoff 1c)")
def test_nested_models_penalized_optimum(dev_design):
    y = dev_design["y"]
    f = {}
    for name, key in [("B2", "Q"), ("B3", "X"), ("B4", "QX")]:
        X = dev_design[key]
        f[name] = StudentTRegression(in_features=X.shape[1], l2_reg=LAM).fit(X, y).fit_report_["penalized_loss"]
    assert f["B4"] <= f["B2"] + 1e-7
    assert f["B4"] <= f["B3"] + 1e-7


def test_reference_optimum_respects_nesting(dev_design):
    """Sanity check of the reference itself: at true optima B4 beats B2 and B3."""
    y = dev_design["y"]
    f2, _ = reference_optimum(dev_design["Q"], y, LAM)
    f3, _ = reference_optimum(dev_design["X"], y, LAM)
    f4, _ = reference_optimum(dev_design["QX"], y, LAM)
    assert f4 <= f2 + 1e-9 and f4 <= f3 + 1e-9


# ---------------------------------------------------------------- B0 / evaluation

def test_b0_closed_form():
    y = np.random.default_rng(6).normal(0.001, 0.01, size=500)
    m = ModelB0_UnconditionalGaussian().fit(y)
    assert m.mu == pytest.approx(y.mean())
    assert m.sigma == pytest.approx(y.std(ddof=1))
    np.testing.assert_allclose(m.log_density(y), stats.norm.logpdf(y, y.mean(), y.std(ddof=1)))


def _synthetic_walk_forward_frame(n_dev=400, n_val=84, seed=7):
    rng = np.random.default_rng(seed)
    n = n_dev + n_val
    regime = (np.arange(n) // 60) % 2
    vol = np.where(regime == 1, 0.02, 0.007)
    vol[n_dev:] *= 2.0  # B0's expanding sigma moves materially between validation blocks
    r = vol * rng.standard_normal(n)
    df = pd.DataFrame({"date": pd.bdate_range("2015-01-01", periods=n).strftime("%Y-%m-%d")})
    for c in Q_COLS:
        df[c] = vol * (1 + 0.1 * rng.standard_normal(n))
    df["r_1d"] = r
    df["rv_20d"] = pd.Series(r).rolling(20, min_periods=1).std().fillna(0.01).values * math.sqrt(252)
    for c in X_COLS:
        if c not in df:
            df[c] = vol * (1 + 0.1 * rng.standard_normal(n))
    df["target_y_next2"] = vol * rng.standard_t(5, size=n)
    df["valid_supervised_pair_all5"] = True
    return df, n_dev


@pytest.mark.xfail(strict=True, reason="Defect 1e.1: B0 PIT uses mu[0], sigma[0] for all rows (walk_forward_pipeline.py)")
def test_b0_pit_uses_per_row_parameters():
    df, n_dev = _synthetic_walk_forward_frame()
    res = run_walk_forward(df, val_start_idx=n_dev, K_regimes=2, lambda_reg=LAM)
    vi = res["val_indices"]
    mu, sig = res["preds"]["B0"]["mu"][vi], res["preds"]["B0"]["sigma"][vi]
    assert np.ptp(sig) > 1e-4, "test frame must make B0 sigma vary across blocks"
    y = df["target_y_next2"].values[vi]
    ks = stats.kstest(stats.norm.cdf(y, loc=mu, scale=sig), "uniform")
    assert res["val_metrics"]["B0"]["pit_ks_pvalue"] == pytest.approx(ks.pvalue, rel=1e-12)
