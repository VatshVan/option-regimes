"""
recalibration.py
================
Prequential (past-only) scale recalibration of density forecasts
(output/stage7_models_v2/step7_specification.md, Section 1).

For refit block b with origin tau_b, a common factor c_b multiplies the predicted scale of
every row scored in block b. c_b maximises the log score of previously scored rows whose
labels have matured at tau_b (row index s <= tau_b - 2); no outcome from block b or later
is used.
"""

from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar


def log_density(y, mu, sigma, nu=None) -> np.ndarray:
    """Student-t log density (Gaussian where nu is None / NaN)."""
    y, mu, sigma = (np.asarray(a, dtype=np.float64) for a in (y, mu, sigma))
    if nu is None or np.all(np.isnan(nu)):
        return stats.norm.logpdf(y, loc=mu, scale=sigma)
    return stats.t.logpdf(y, df=np.asarray(nu, dtype=np.float64), loc=mu, scale=sigma)


def fit_scale_factor(y, mu, sigma, nu=None, bounds: Tuple[float, float] = (0.25, 4.0)) -> float:
    """c maximising sum log f(y; mu, c * sigma, nu) on [bounds]."""
    res = minimize_scalar(lambda c: -np.sum(log_density(y, mu, c * np.asarray(sigma), nu)),
                          bounds=bounds, method="bounded", options={"xatol": 1e-8})
    return float(res.x)


def prequential_scale_recalibration(
    y: Sequence[float],
    mu: Sequence[float],
    sigma: Sequence[float],
    nu: Optional[Sequence[float]],
    row_idx: Sequence[int],
    block_ids: Sequence[int],
    refit_tau: Dict[int, int],
    min_rows: int = 21,
    bounds: Tuple[float, float] = (0.25, 4.0),
) -> Dict[str, Any]:
    """
    y, mu, sigma, nu: scored rows (nu None for Gaussian); row_idx: their index in the full
    frame; block_ids: their refit block; refit_tau: block -> refit origin index.
    Returns per-row factor c, recalibrated log scores, and per-block factors / sample sizes.
    """
    y, mu, sigma = (np.asarray(a, dtype=np.float64) for a in (y, mu, sigma))
    nu = None if nu is None else np.asarray(nu, dtype=np.float64)
    row_idx, block_ids = np.asarray(row_idx), np.asarray(block_ids)
    c = np.ones(len(y))
    per_block = {}
    for b in sorted(set(block_ids.tolist())):
        eligible = row_idx <= refit_tau[b] - 2
        n = int(eligible.sum())
        if n >= min_rows:
            cb = fit_scale_factor(y[eligible], mu[eligible], sigma[eligible],
                                  None if nu is None else nu[eligible], bounds)
        else:
            cb = 1.0
        c[block_ids == b] = cb
        per_block[int(b)] = {"c": cb, "n_eligible": n, "max_eligible_row": int(row_idx[eligible].max()) if n else None}
    return {"c": c, "log_p": log_density(y, mu, c * sigma, nu), "per_block": per_block}
