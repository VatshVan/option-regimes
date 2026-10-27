import numpy as np
import pytest
from scipy import stats

from src.models.recalibration import fit_scale_factor, prequential_scale_recalibration


def test_fit_scale_factor_recovers_known_inflation():
    rng = np.random.default_rng(0)
    sigma = np.full(20000, 0.01)
    y = 1.3 * sigma * rng.standard_t(5, size=sigma.size)
    c = fit_scale_factor(y, np.zeros_like(y), sigma, np.full_like(y, 5.0))
    assert c == pytest.approx(1.3, rel=0.02)
    c_gauss = fit_scale_factor(1.3 * sigma * rng.standard_normal(sigma.size), np.zeros_like(y), sigma)
    assert c_gauss == pytest.approx(1.3, rel=0.02)


def _setup():
    rng = np.random.default_rng(1)
    n_blocks, size = 4, 21
    row_idx = np.arange(100, 100 + n_blocks * size)
    blocks = np.repeat(np.arange(n_blocks), size)
    refit_tau = {b: 99 + b * size for b in range(n_blocks)}  # block b scores tau_b + 1 ... tau_b + 21
    sigma = np.full(row_idx.size, 0.01)
    y = 1.5 * sigma * rng.standard_t(6, size=row_idx.size)
    return y, sigma, row_idx, blocks, refit_tau


def test_prequential_uses_only_matured_past_rows():
    y, sigma, row_idx, blocks, refit_tau = _setup()
    nu = np.full(y.size, 6.0)
    out = prequential_scale_recalibration(y, np.zeros_like(y), sigma, nu, row_idx, blocks, refit_tau)
    assert out["per_block"][0]["c"] == 1.0 and out["per_block"][0]["n_eligible"] == 0
    for b in range(1, 4):
        pb = out["per_block"][b]
        assert pb["max_eligible_row"] <= refit_tau[b] - 2
        assert pb["n_eligible"] == int(np.sum(row_idx <= refit_tau[b] - 2))
    # changing outcomes in block 2 and later must not change c for blocks <= 2
    y2 = y.copy()
    y2[blocks >= 2] *= 10
    out2 = prequential_scale_recalibration(y2, np.zeros_like(y), sigma, nu, row_idx, blocks, refit_tau)
    for b in range(3):
        assert out2["per_block"][b]["c"] == out["per_block"][b]["c"]


def test_recalibrated_log_density_uses_scaled_sigma():
    y, sigma, row_idx, blocks, refit_tau = _setup()
    nu = np.full(y.size, 6.0)
    out = prequential_scale_recalibration(y, np.zeros_like(y), sigma, nu, row_idx, blocks, refit_tau)
    np.testing.assert_allclose(out["log_p"], stats.t.logpdf(y, df=6.0, loc=0.0, scale=out["c"] * sigma))
