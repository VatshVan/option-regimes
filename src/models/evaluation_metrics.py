"""
evaluation_metrics.py
=====================
Statistical evaluation metrics for physical return density forecasting.
Governing specification: stage5_modeling_specification.md Section 7.

Metrics:
- Negative Log-Likelihood (NLL)
- Continuous Ranked Probability Score (CRPS)
- Probability Integral Transform (PIT) & Kolmogorov-Smirnov test
- Central interval empirical coverage (50%, 80%, 95%)
- Tail pinball losses (alpha in {0.01, 0.05, 0.10, 0.90, 0.95, 0.99})
- Paired Diebold-Mariano test with Newey-West HAC variance
- Stationary block bootstrap for loss differential
"""

import math
import numpy as np
from scipy import stats
import scipy.special as sp
from scipy.integrate import quad

def compute_nll(log_densities: np.ndarray) -> float:
    """Mean Negative Log-Likelihood (nats per session)."""
    return float(-np.mean(log_densities))

def compute_crps_student_t_vectorized(y: np.ndarray, mu: np.ndarray, sigma: np.ndarray, nu: np.ndarray) -> np.ndarray:
    """
    Computes Continuous Ranked Probability Score (CRPS) for generalized Student-t distributions:
    CRPS(F, y) = int_{-infty}^y F(z)^2 dz + int_y^infty (1 - F(z))^2 dz
    using the exact closed-form analytical expression (Jordan, Krüger, & Lerch, 2019):
      CRPS(F_{nu, mu, sigma}, y) = sigma * [ z*(2*F(z) - 1) + 2*f(z)*((nu + z^2)/(nu - 1)) - C(nu) ]
    where:
      z = (y - mu) / sigma
      C(nu) = [2 * sqrt(nu) / (nu - 1)] * [B(1/2, nu - 1/2) / B(1/2, nu/2)^2]
    Valid for nu > 1. Exact over the full real line (-infty, infty) to machine precision (< 1e-14).
    """
    y = np.asarray(y, dtype=np.float64)
    mu = np.asarray(mu, dtype=np.float64)
    sigma = np.asarray(sigma, dtype=np.float64)
    nu = np.asarray(nu, dtype=np.float64)
    
    z = (y - mu) / sigma
    F = stats.t.cdf(z, df=nu)
    f = stats.t.pdf(z, df=nu)
    
    term1 = z * (2.0 * F - 1.0)
    term2 = 2.0 * f * (nu + z ** 2) / (nu - 1.0)
    term3 = (2.0 * np.sqrt(nu) / (nu - 1.0)) * sp.beta(0.5, nu - 0.5) / (sp.beta(0.5, nu / 2.0) ** 2)
    
    return sigma * (term1 + term2 - term3)

def student_t_crps(y: float, mu: float, sigma: float, nu: float) -> float:
    """Scalar interface for Student-t CRPS."""
    return float(compute_crps_student_t_vectorized(np.array([y]), np.array([mu]), np.array([sigma]), np.array([nu]))[0])

def gaussian_crps(y: float, mu: float, sigma: float) -> float:
    """Analytical CRPS for Normal distribution."""
    z = (y - mu) / sigma
    phi = stats.norm.pdf(z)
    Phi = stats.norm.cdf(z)
    crps = sigma * (z * (2.0 * Phi - 1.0) + 2.0 * phi - 1.0 / math.sqrt(math.pi))
    return float(crps)

def compute_pit_values_student_t(y: np.ndarray, mu: np.ndarray, sigma: np.ndarray, nu: np.ndarray) -> np.ndarray:
    """Computes PIT values u_t = F(y_t) for Student-t densities."""
    return stats.t.cdf(y, df=nu, loc=mu, scale=sigma)

def compute_pit_values_gaussian(y: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Computes PIT values u_t = F(y_t) for Gaussian densities."""
    return stats.norm.cdf(y, loc=mu, scale=sigma)

def compute_interval_coverage(y: np.ndarray, mu: np.ndarray, sigma: np.ndarray, nu: np.ndarray, nominal_coverages=[0.50, 0.80, 0.95]) -> dict:
    """Computes empirical coverage rates for central predictive intervals."""
    coverages = {}
    for cov in nominal_coverages:
        alpha = 1.0 - cov
        lower_q = stats.t.ppf(alpha / 2.0, df=nu, loc=mu, scale=sigma)
        upper_q = stats.t.ppf(1.0 - alpha / 2.0, df=nu, loc=mu, scale=sigma)
        in_interval = (y >= lower_q) & (y <= upper_q)
        coverages[f"coverage_{int(cov*100)}"] = float(np.mean(in_interval))
    return coverages

def compute_pinball_loss(y: np.ndarray, mu: np.ndarray, sigma: np.ndarray, nu: np.ndarray, alphas=[0.01, 0.05, 0.10, 0.90, 0.95, 0.99]) -> dict:
    """Computes quantile pinball losses."""
    pinball = {}
    for alpha in alphas:
        q = stats.t.ppf(alpha, df=nu, loc=mu, scale=sigma)
        loss = (y - q) * (alpha - (y < q).astype(float))
        pinball[f"pinball_{int(alpha*100):02d}"] = float(np.mean(loss))
    return pinball

def diebold_mariano_test(d: np.ndarray, max_lag: int = None) -> dict:
    """
    Paired Diebold-Mariano test with Newey-West HAC variance estimation.
    d_t = ln p_1(y_t) - ln p_0(y_t) = ell_0(y_t) - ell_1(y_t).
    Positive d_t indicates Model 1 has lower loss (higher likelihood).
    """
    N = len(d)
    d_bar = float(np.mean(d))
    
    # Automatic bandwidth rule: L = floor(4 * (N/100)^(2/9))
    if max_lag is None:
        max_lag = max(1, int(math.floor(4.0 * (N / 100.0) ** (2.0 / 9.0))))
        
    # Sample autocovariances
    d_centered = d - d_bar
    gamma_0 = np.sum(d_centered ** 2) / N
    
    nw_var = gamma_0
    for l in range(1, max_lag + 1):
        weight = 1.0 - (l / (max_lag + 1.0))  # Bartlett kernel
        gamma_l = np.sum(d_centered[l:] * d_centered[:-l]) / N
        nw_var += 2.0 * weight * gamma_l
        
    se = math.sqrt(max(1e-12, nw_var / N))
    dm_stat = d_bar / se
    p_value_one_sided = 1.0 - stats.norm.cdf(dm_stat)
    p_value_two_sided = 2.0 * (1.0 - stats.norm.cdf(abs(dm_stat)))
    
    return {
        "mean_differential": d_bar,
        "hac_se": se,
        "bandwidth_lags": max_lag,
        "dm_stat": dm_stat,
        "p_value_one_sided": float(p_value_one_sided),
        "p_value_two_sided": float(p_value_two_sided)
    }

def stationary_block_bootstrap(d: np.ndarray, n_boot: int = 2000, expected_block_len: int = 5, seed: int = 42) -> dict:
    """
    Politis & Romano (1994) stationary block bootstrap for loss differential d_t.
    Computes 95% bootstrap confidence interval.
    """
    N = len(d)
    rng = np.random.RandomState(seed)
    p_geom = 1.0 / expected_block_len
    
    boot_means = np.zeros(n_boot)
    for b in range(n_boot):
        sample_indices = []
        cur_idx = rng.randint(0, N)
        for _ in range(N):
            sample_indices.append(cur_idx)
            if rng.rand() < p_geom:
                cur_idx = rng.randint(0, N)
            else:
                cur_idx = (cur_idx + 1) % N
        boot_means[b] = np.mean(d[sample_indices])
        
    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))
    
    return {
        "boot_mean": float(np.mean(boot_means)),
        "ci_95_lower": ci_lower,
        "ci_95_upper": ci_upper,
        "excludes_zero": bool(ci_lower > 0.0 or ci_upper < 0.0)
    }
