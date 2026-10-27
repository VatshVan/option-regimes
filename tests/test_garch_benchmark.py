import numpy as np
import pytest

from src.models.garch_benchmark import PCT, gjr_t_forecasts


def _simulated_returns(n=3000, seed=3):
    rng = np.random.default_rng(seed)
    omega, alpha, gamma, beta, nu = 0.02, 0.03, 0.10, 0.88, 6.0
    r, h = np.zeros(n), np.zeros(n)
    h[0] = omega / (1 - alpha - gamma / 2 - beta)
    for t in range(n):
        if t:
            e = r[t - 1] * PCT
            h[t] = omega + (alpha + gamma * (e < 0)) * e ** 2 + beta * h[t - 1]
        z = rng.standard_t(nu) * np.sqrt((nu - 2) / nu)
        r[t] = (0.03 + np.sqrt(h[t]) * z) / PCT
    return r


def test_two_step_forecast_targets_r_t_plus_2():
    r = _simulated_returns()
    tau, origins = 2500, np.arange(2501, 2520)
    pred, info = gjr_t_forecasts(r, origins, tau)
    assert info["converged"]
    p = info["params"]
    # independent GJR recursion with the frozen parameters (start-up effects vanish by t ~ 2500)
    resid = PCT * r - p["mu"]
    h = np.empty(len(r))
    h[0] = np.var(resid[: tau + 1])
    for t in range(1, len(r)):
        h[t] = p["omega"] + (p["alpha[1]"] + p["gamma[1]"] * (resid[t - 1] < 0)) * resid[t - 1] ** 2 + p["beta[1]"] * h[t - 1]
    for i, t in enumerate(origins):
        h1 = h[t + 1]  # h_{t+1|t}: uses r_t, known at origin t
        h2 = p["omega"] + (p["alpha[1]"] + 0.5 * p["gamma[1]"] + p["beta[1]"]) * h1  # E_t[h_{t+2}]
        nu = p["nu"]
        assert pred["sigma"][i] == pytest.approx(np.sqrt(h2 * (nu - 2) / nu) / PCT, rel=1e-8)


def test_parameters_use_only_data_through_tau():
    r = _simulated_returns()
    tau, origins = 2500, np.arange(2501, 2520)
    _, info = gjr_t_forecasts(r, origins, tau)
    r2 = r.copy()
    r2[tau + 1:] *= 5.0  # change everything after the estimation window
    _, info2 = gjr_t_forecasts(r2, origins, tau)
    assert info2["params"] == info["params"]
