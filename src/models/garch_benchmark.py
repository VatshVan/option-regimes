"""
garch_benchmark.py
==================
GJR-GARCH(1,1)-t benchmark (B5) for the one-day physical density of
y_t = ln(S_{t+2} / S_{t+1}) = r_{t+2}
(output/stage7_models_v2/benchmark_gjr_specification.md).

At refit origin tau, parameters are estimated on r_0 ... r_tau; for each scoring origin t the
predictive density is the two-step-ahead forecast from information through r_t with the
parameters frozen at tau: Student-t with location mu, d.o.f. nu and
scale sqrt(h_{t+2|t} * (nu - 2) / nu).
"""

from typing import Any, Dict, Sequence, Tuple

import numpy as np
from arch import arch_model
from scipy import stats

PCT = 100.0  # returns are fitted in percent for numerical stability


def fit_gjr_t(returns: np.ndarray, tau: int, last_index: int):
    """Fit on returns[0 .. tau]; the model holds returns[0 .. last_index] for filtering."""
    am = arch_model(PCT * np.asarray(returns[: last_index + 1], dtype=np.float64),
                    mean="Constant", vol="GARCH", p=1, o=1, q=1, dist="t")
    return am.fit(last_obs=tau + 1, disp="off", options={"maxiter": 1000})


def gjr_t_forecasts(returns: np.ndarray, origins: Sequence[int], tau: int) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
    """
    Predictive Student-t parameters for targets r_{t+2} at origins t (all > tau, consecutive),
    with parameters estimated on r_0 .. r_tau.
    """
    origins = np.asarray(origins)
    res = fit_gjr_t(returns, tau, int(origins.max()))
    fc = res.forecast(start=int(origins.min()), horizon=2, reindex=False)
    h2 = fc.variance["h.2"].values
    assert len(h2) == len(origins), "forecast origins do not match requested origins"
    mu, nu = float(res.params["mu"]), float(res.params["nu"])
    out = {
        "mu": np.full(len(origins), mu / PCT),
        "sigma": np.sqrt(h2 * (nu - 2.0) / nu) / PCT,
        "nu": np.full(len(origins), nu),
    }
    info = {"converged": bool(res.convergence_flag == 0), "params": {k: float(v) for k, v in res.params.items()},
            "loglikelihood": float(res.loglikelihood), "n_obs": int(tau + 1)}
    return out, info


def log_density(y, pred) -> np.ndarray:
    return stats.t.logpdf(y, df=pred["nu"], loc=pred["mu"], scale=pred["sigma"])
