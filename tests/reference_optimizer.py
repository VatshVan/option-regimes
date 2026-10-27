"""
Independent float64 reference optimum for the StudentTRegression objective
(the optimizer-audit notes Section 5). Uses SciPy L-BFGS-B with an analytic
gradient and no torch, so it can audit the torch optimizer.
theta = [raw_nu, w_mu (d), b_mu, w_sig (d), b_sig]
"""
import numpy as np
from scipy.optimize import minimize
from scipy.special import digamma, expit, gammaln

SIGMA_MIN = 1e-4
NU_MIN = 2.1


def softplus(x):
    return np.logaddexp(0.0, x)


def unpack(theta, d):
    return theta[0], theta[1:1 + d], theta[1 + d], theta[2 + d:2 + 2 * d], theta[2 + 2 * d]


def objective_and_grad(theta, X, y, lam):
    d = X.shape[1]
    rn, wm, bm, ws, bs = unpack(theta, d)
    mu = X @ wm + bm
    a = X @ ws + bs
    sig = softplus(a) + SIGMA_MIN
    nu = softplus(rn) + NU_MIN
    z = (y - mu) / sig
    u = 1.0 + z * z / nu
    ll = gammaln((nu + 1) / 2) - gammaln(nu / 2) - 0.5 * np.log(np.pi * nu) - np.log(sig) - (nu + 1) / 2 * np.log(u)
    f = -ll.mean() + lam * (wm @ wm + ws @ ws)

    w = (nu + 1) / (nu * u)
    dmu = w * z / sig
    dsig = (-1 + w * z * z) / sig
    dnu = 0.5 * (digamma((nu + 1) / 2) - digamma(nu / 2)) - 0.5 / nu - 0.5 * np.log(u) + (nu + 1) / 2 * (z * z / nu ** 2) / u
    g = np.empty_like(theta)
    g[0] = -dnu.mean() * expit(rn)
    g[1:1 + d] = -(dmu[:, None] * X).mean(0) + 2 * lam * wm
    g[1 + d] = -dmu.mean()
    gs = -(dsig * expit(a))
    g[2 + d:2 + 2 * d] = (gs[:, None] * X).mean(0) + 2 * lam * ws
    g[2 + 2 * d] = gs.mean()
    return f, g


def b1_objective_and_grad(theta, rv, y):
    """
    ModelB1 objective (mean Student-t NLL, no penalty) and gradient.
    theta = [mu, p_a0, p_a1, p_nu]; sigma = softplus(p_a0) + 1e-4 + softplus(p_a1) * rv.
    """
    mu, pa0, pa1, rn = theta
    sig = softplus(pa0) + SIGMA_MIN + softplus(pa1) * rv
    nu = softplus(rn) + NU_MIN
    z = (y - mu) / sig
    u = 1.0 + z * z / nu
    ll = gammaln((nu + 1) / 2) - gammaln(nu / 2) - 0.5 * np.log(np.pi * nu) - np.log(sig) - (nu + 1) / 2 * np.log(u)
    w = (nu + 1) / (nu * u)
    dmu = w * z / sig
    dsig = (-1 + w * z * z) / sig
    dnu = 0.5 * (digamma((nu + 1) / 2) - digamma(nu / 2)) - 0.5 / nu - 0.5 * np.log(u) + (nu + 1) / 2 * (z * z / nu ** 2) / u
    g = np.array([
        -dmu.mean(),
        -(dsig * expit(pa0)).mean(),
        -(dsig * expit(pa1) * rv).mean(),
        -dnu.mean() * expit(rn),
    ])
    return -ll.mean(), g


def b1_reference_optimum(rv, y):
    rv = np.asarray(rv, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    s = np.std(y, ddof=1)
    theta0 = np.array([np.mean(y), np.log(max(1e-4, np.expm1(0.5 * s))), np.log(np.expm1(0.05)), np.log(np.expm1(5.0 - 2.1))])
    res = minimize(
        b1_objective_and_grad, theta0, args=(rv, y), jac=True, method="L-BFGS-B",
        options=dict(maxiter=50000, maxfun=100000, ftol=1e-16, gtol=1e-12, maxcor=50),
    )
    return res.fun, res.x


def reference_log_density(theta, X, y):
    """Per-row Student-t log density at parameters theta."""
    from scipy import stats
    X = np.asarray(X, dtype=np.float64)
    d = X.shape[1]
    rn, wm, bm, ws, bs = unpack(theta, d)
    mu = X @ wm + bm
    sig = softplus(X @ ws + bs) + SIGMA_MIN
    nu = softplus(rn) + NU_MIN
    return stats.t.logpdf(y, df=nu, loc=mu, scale=sig)


def initial_theta(X, y):
    """Same starting point as StudentTRegression.fit."""
    d = X.shape[1]
    theta = np.zeros(3 + 2 * d)
    theta[0] = 2.85
    theta[1 + d] = np.mean(y)
    theta[2 + 2 * d] = np.log(max(1e-4, np.expm1(np.std(y, ddof=1))))
    return theta


def reference_optimum(X, y, lam, theta0=None):
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if theta0 is None:
        theta0 = initial_theta(X, y)
    res = minimize(
        objective_and_grad, theta0, args=(X, y, lam), jac=True, method="L-BFGS-B",
        options=dict(maxiter=50000, maxfun=100000, ftol=1e-16, gtol=1e-11, maxcor=50),
    )
    return res.fun, res.x
