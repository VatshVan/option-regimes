"""
density_models.py
=================
Implementation of physical return density forecasting models (B0 - B4 and R1)
and 2-component Mixture Density Network (MDN) fallback comparator.
Governing specification: stage5_modeling_specification.md Section 4.

Models:
- RobustScaler: Training-only robust median/IQR feature scaler.
- ModelB0_UnconditionalGaussian: Unconditional expanding Gaussian benchmark.
- ModelB1_RVLocationScaleStudentT: Student-t location-scale conditioned on RV_20d.
- StudentTRegression: Parameterized location-scale Student-t regression model (used for B2, B3, B4, R1).
- MixtureDensityNetwork2: 2-component Student-t Mixture Density Network (MDN fallback check).
"""

import math
import warnings
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import stats
from typing import Tuple, Dict, Any, Optional

def _student_t_log_lik(y: torch.Tensor, mu: torch.Tensor, sig: torch.Tensor, nu: torch.Tensor) -> torch.Tensor:
    """Per-observation Student-t log density log t_nu((y - mu) / sig) - log sig."""
    z = (y - mu) / sig
    log_norm = (
        torch.lgamma(0.5 * (nu + 1.0))
        - torch.lgamma(0.5 * nu)
        - 0.5 * torch.log(math.pi * nu)
        - torch.log(sig)
    )
    log_kernel = -0.5 * (nu + 1.0) * torch.log(1.0 + (z ** 2) / nu)
    return log_norm + log_kernel


def _lbfgs_fit_report(
    optimizer: torch.optim.LBFGS,
    params,
    penalized_fn,
    unpenalized_fn,
    nu_fn,
) -> Dict[str, Any]:
    """
    Post-hoc diagnostics for a completed single torch LBFGS.step call.
    Reads the optimizer state and re-evaluates the objective at the final
    parameters; it does not modify parameters, so fitted predictions are unchanged.
    stop_reason reproduces the order of termination checks in torch LBFGS.step.
    """
    group = optimizer.param_groups[0]
    state = optimizer.state[optimizer._params[0]]
    n_iter = int(state.get("n_iter", 0))
    func_evals = int(state.get("func_evals", 0))

    for p in params:
        p.grad = None
    with torch.enable_grad():
        loss = penalized_fn()
        loss.backward()
    flat_grad = torch.cat([p.grad.reshape(-1) for p in params])
    for p in params:
        p.grad = None
    with torch.no_grad():
        unpen = float(unpenalized_fn())
        nu = float(nu_fn())
    max_abs_grad = float(flat_grad.abs().max())
    loss_val = float(loss.detach())

    prev_flat_grad = state.get("prev_flat_grad")
    prev_loss = state.get("prev_loss")
    d, t = state.get("d"), state.get("t")
    tol_change = group["tolerance_change"]
    if n_iter == 0:
        stop_reason = "grad_tol_at_init"
    elif prev_flat_grad is not None and torch.equal(prev_flat_grad, flat_grad):
        # gtd break: prev_flat_grad is overwritten with the current gradient before the check
        stop_reason = "directional_derivative_tol"
    elif n_iter >= group["max_iter"]:
        stop_reason = "max_iter"
    elif func_evals >= group["max_eval"]:
        stop_reason = "max_eval"
    elif max_abs_grad <= group["tolerance_grad"]:
        stop_reason = "grad_tol"
    elif d is not None and float(d.mul(t).abs().max()) <= tol_change:
        stop_reason = "step_tol"
    elif prev_loss is not None and abs(float(loss_val) - float(prev_loss)) < tol_change:
        stop_reason = "loss_change_tol"
    else:
        stop_reason = "unknown"

    return {
        "n_iter": n_iter,
        "func_evals": func_evals,
        "max_iter": int(group["max_iter"]),
        "max_eval": int(group["max_eval"]),
        "stop_reason": stop_reason,
        "converged": stop_reason in ("grad_tol", "grad_tol_at_init"),
        "penalized_loss": loss_val,
        "unpenalized_nll": unpen,
        "max_abs_grad": max_abs_grad,
        "nu": nu,
        "dtype": str(flat_grad.dtype).replace("torch.", ""),
    }


def _grad_and_hessian(params, penalized_fn):
    """Objective value, flat gradient and exact (symmetrised) Hessian over params."""
    loss = penalized_fn()
    grads = torch.autograd.grad(loss, params, create_graph=True)
    g = torch.cat([x.reshape(-1) for x in grads])
    rows = []
    for i in range(g.numel()):
        second = torch.autograd.grad(g[i], params, retain_graph=True, allow_unused=True)
        rows.append(torch.cat([torch.zeros(p.numel(), dtype=g.dtype) if s is None else s.reshape(-1)
                               for p, s in zip(params, second)]))
    H = torch.stack(rows).detach()
    return float(loss.detach()), g.detach(), 0.5 * (H + H.T)


def _loss_and_grad(params, penalized_fn):
    loss = penalized_fn()
    grads = torch.autograd.grad(loss, params)
    return float(loss.detach()), torch.cat([x.reshape(-1) for x in grads])


def _add_to_params(params, step):
    with torch.no_grad():
        offset = 0
        for p in params:
            n = p.numel()
            p.add_(step[offset:offset + n].view_as(p))
            offset += n


def _newton_polish(params, penalized_fn, target_grad: float, max_steps: int) -> Dict[str, Any]:
    """
    Exact-Hessian damped Newton refinement after L-BFGS. A step is taken only when the
    Hessian is positive definite; the Newton direction is backtracked (halving, at most
    max_backtracks times) until it gives an Armijo decrease, or, at the float64 round-off
    floor, keeps the objective within round-off while lowering max|grad|. If no step size
    qualifies, the parameters are left unchanged and polishing stops. Near a strict minimum
    full steps are accepted and convergence is quadratic regardless of conditioning (e.g.
    R1's pi/intercept near-null direction). Returns step count and the Hessian spectrum.
    """
    max_backtracks = 30
    loss, g, H = _grad_and_hessian(params, penalized_fn)
    steps = 0
    while steps < max_steps and float(g.abs().max()) > target_grad:
        try:
            chol = torch.linalg.cholesky(H)
        except RuntimeError:
            break
        direction = -torch.cholesky_solve(g.unsqueeze(1), chol).squeeze(1)
        slope = float(g @ direction)  # < 0 for positive-definite H
        roundoff = 1e-14 * max(1.0, abs(loss))
        accepted = False
        t = 1.0
        for _ in range(max_backtracks):
            _add_to_params(params, t * direction)
            new_loss, new_g = _loss_and_grad(params, penalized_fn)
            armijo = new_loss <= loss + 1e-4 * t * slope
            floor = new_loss <= loss + roundoff and float(new_g.abs().max()) < float(g.abs().max())
            if armijo or floor:
                accepted = True
                break
            _add_to_params(params, -t * direction)
            t *= 0.5
        if not accepted:
            break
        loss, g, H = _grad_and_hessian(params, penalized_fn)
        steps += 1
    eig = torch.linalg.eigvalsh(H)
    return {
        "newton_steps": steps,
        "hessian_min_eig": float(eig.min()),
        "hessian_max_eig": float(eig.max()),
        "hessian_positive_definite": bool(eig.min() > 0),
    }


def _run_lbfgs(
    params,
    penalized_fn,
    unpenalized_fn,
    nu_fn,
    max_iter: int = 2000,
    grad_tol: float = 1e-8,
    rel_change_tol: float = 1e-15,
    history_size: int = 100,
    max_newton_steps: int = 20,
    lbfgs_chunk: int = 100,
    label: str = "model",
) -> Dict[str, Any]:
    """
    Minimises penalized_fn over params with float64 L-BFGS (strong Wolfe line search) run in
    chunks of at most lbfgs_chunk iterations, each followed by an exact-Hessian Newton polish
    (_newton_polish); stops as soon as the fit is converged or max_iter L-BFGS iterations are spent.
    Chunking stops L-BFGS from crawling along near-null directions (R1's pi/intercept
    direction) that a Newton step resolves at once.

    Each L-BFGS chunk stops at max|grad| <= grad_tol, when step / objective change falls below
    rel_change_tol * max(1, |f0|) (the float64 round-off floor), or at its iteration budget; the
    last chunk's stop reason is kept as 'stop_reason'. All loss / gradient / nu fields are
    evaluated at the final point.

    Converged means max|grad| <= grad_tol at the final point AND a positive-definite Hessian
    (a strict local minimum). Otherwise a RuntimeWarning is issued.
    """
    with torch.no_grad():
        f0 = float(penalized_fn())
    tol_change = rel_change_tol * max(1.0, abs(f0))
    total_iter, total_evals, total_newton, rounds = 0, 0, 0, 0
    while True:
        budget = min(lbfgs_chunk, max_iter - total_iter)
        optimizer = torch.optim.LBFGS(
            params, lr=1.0, line_search_fn="strong_wolfe", max_iter=budget,
            max_eval=max(budget + 1, int(budget * 1.25)), tolerance_grad=grad_tol,
            tolerance_change=tol_change, history_size=history_size,
        )

        def closure():
            optimizer.zero_grad()
            loss = penalized_fn()
            loss.backward()
            return loss

        optimizer.step(closure)
        lbfgs = _lbfgs_fit_report(optimizer, params, penalized_fn, unpenalized_fn, nu_fn)
        polish = _newton_polish(params, penalized_fn, target_grad=1e-2 * grad_tol, max_steps=max_newton_steps)
        report = _lbfgs_fit_report(optimizer, params, penalized_fn, unpenalized_fn, nu_fn)
        total_iter += lbfgs["n_iter"]
        total_evals += lbfgs["func_evals"]
        total_newton += polish["newton_steps"]
        rounds += 1
        converged = report["max_abs_grad"] <= grad_tol and polish["hessian_positive_definite"]
        no_progress = lbfgs["n_iter"] <= 1 and polish["newton_steps"] == 0
        if converged or no_progress or total_iter >= max_iter:
            break

    report.update(polish)
    report.update({
        "stop_reason": lbfgs["stop_reason"],
        "n_iter": total_iter,
        "func_evals": total_evals,
        "max_iter": max_iter,
        "newton_steps": total_newton,
        "lbfgs_rounds": rounds,
        "lbfgs_max_abs_grad": lbfgs["max_abs_grad"],
        "grad_tol": grad_tol,
        "tolerance_change": tol_change,
        "history_size": history_size,
        "initial_loss": f0,
    })
    report["converged"] = bool(converged)
    if not report["converged"]:
        warnings.warn(
            f"{label} not converged: lbfgs_stop={report['stop_reason']}, "
            f"max|grad|={report['max_abs_grad']:.2e}, n_iter={report['n_iter']}, "
            f"newton_steps={report['newton_steps']}, hessian_min_eig={report['hessian_min_eig']:.2e}",
            RuntimeWarning,
        )
    return report


class RobustFeatureScaler:
    """
    Robust feature scaler using sample median and Interquartile Range (IQR):
    z = (x - median) / IQR.
    Fitted strictly on in-sample training window.
    """
    def __init__(self, eps: float = 1e-6):
        self.eps = eps
        self.medians: Optional[np.ndarray] = None
        self.iqrs: Optional[np.ndarray] = None
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        X = np.asarray(X, dtype=np.float64)
        self.medians = np.nanmedian(X, axis=0)
        q75 = np.nanpercentile(X, 75.0, axis=0)
        q25 = np.nanpercentile(X, 25.0, axis=0)
        iqr = q75 - q25
        # If IQR is degenerate or zero, replace with 1.0
        iqr[iqr < self.eps] = 1.0
        self.iqrs = iqr
        self.is_fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        assert self.is_fitted, "Scaler must be fitted before transform"
        X = np.asarray(X, dtype=np.float64)
        return (X - self.medians) / self.iqrs

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class ModelB0_UnconditionalGaussian:
    """
    Model B0: Unconditional Gaussian Benchmark.
    Estimates expanding sample mean mu_tau and variance sigma_tau^2 strictly over in-sample targets.
    """
    def __init__(self):
        self.mu: float = 0.0
        self.sigma: float = 0.01
        self.is_fitted = False

    def fit(self, y: np.ndarray):
        y = np.asarray(y, dtype=np.float64)
        assert len(y) > 1, "Need at least 2 samples to compute sample variance"
        self.mu = float(np.mean(y))
        self.sigma = float(np.std(y, ddof=1))
        # Minimum variance floor
        self.sigma = max(self.sigma, 1e-4)
        self.is_fitted = True
        return self

    def predict(self, n_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        assert self.is_fitted, "Model must be fitted before prediction"
        mu_vec = np.full(n_samples, self.mu)
        sigma_vec = np.full(n_samples, self.sigma)
        return mu_vec, sigma_vec

    def log_density(self, y: np.ndarray) -> np.ndarray:
        assert self.is_fitted, "Model must be fitted"
        y = np.asarray(y, dtype=np.float64)
        return stats.norm.logpdf(y, loc=self.mu, scale=self.sigma)


class ModelB1_RVLocationScaleStudentT:
    """
    Model B1: Trailing Volatility Location-Scale Benchmark.
    sigma_t = alpha_0 + alpha_1 * RV_20d,t
    mu_t = mu
    nu >= 2.1
    Optimized via Maximum Likelihood on in-sample training window.
    """
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.mu: float = 0.0
        self.alpha_0: float = 0.005
        self.alpha_1: float = 0.05
        self.nu: float = 5.0
        self.is_fitted = False

    def fit(self, rv20d: np.ndarray, y: np.ndarray, max_iter: int = 60):
        rv20d_t = torch.tensor(rv20d, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.float32)
        
        # Initial guesses
        mu_init = float(y_t.mean())
        std_init = float(y_t.std())
        
        # Parameter tensors:
        # alpha_0 = softplus(p_a0) + 1e-4
        # alpha_1 = softplus(p_a1)
        # nu = softplus(p_nu) + 2.1
        # mu = p_mu
        p_mu = torch.tensor([mu_init], dtype=torch.float32, requires_grad=True)
        p_a0 = torch.tensor([math.log(max(1e-4, math.exp(0.5 * std_init) - 1.0))], dtype=torch.float32, requires_grad=True)
        p_a1 = torch.tensor([math.log(max(1e-4, math.exp(0.05) - 1.0))], dtype=torch.float32, requires_grad=True)
        p_nu = torch.tensor([math.log(max(1e-4, math.exp(5.0 - 2.1) - 1.0))], dtype=torch.float32, requires_grad=True)
        
        params = [p_mu, p_a0, p_a1, p_nu]
        optimizer = torch.optim.LBFGS(params, lr=0.5, line_search_fn="strong_wolfe", max_iter=max_iter)

        def objective():
            a0 = F.softplus(p_a0) + 1e-4
            a1 = F.softplus(p_a1)
            nu = F.softplus(p_nu) + 2.1
            mu = p_mu

            sig = a0 + a1 * rv20d_t
            z = (y_t - mu) / sig

            log_p = (
                torch.lgamma(0.5 * (nu + 1.0))
                - torch.lgamma(0.5 * nu)
                - 0.5 * torch.log(math.pi * nu)
                - torch.log(sig)
                - 0.5 * (nu + 1.0) * torch.log(1.0 + (z ** 2) / nu)
            )
            return -log_p.mean()

        def closure():
            optimizer.zero_grad()
            loss = objective()
            loss.backward()
            return loss

        optimizer.step(closure)
        # B1 has no penalty: penalized and unpenalized objectives coincide
        self.fit_report_ = _lbfgs_fit_report(
            optimizer, params, objective, objective,
            lambda: F.softplus(p_nu) + 2.1,
        )

        self.mu = float(p_mu.item())
        self.alpha_0 = float((F.softplus(p_a0) + 1e-4).item())
        self.alpha_1 = float(F.softplus(p_a1).item())
        self.nu = float((F.softplus(p_nu) + 2.1).item())
        self.is_fitted = True
        return self

    def predict(self, rv20d: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        assert self.is_fitted, "Model must be fitted before prediction"
        rv = np.asarray(rv20d, dtype=np.float64)
        sigma = self.alpha_0 + self.alpha_1 * rv
        sigma = np.maximum(sigma, 1e-4)
        mu = np.full(len(rv), self.mu)
        nu = np.full(len(rv), self.nu)
        return mu, sigma, nu

    def log_density(self, rv20d: np.ndarray, y: np.ndarray) -> np.ndarray:
        mu, sigma, nu = self.predict(rv20d)
        return stats.t.logpdf(y, df=nu, loc=mu, scale=sigma)


class StudentTRegression(nn.Module):
    """
    Location-scale Student-t regression model.
    mu_t = w_mu^T x_t + b_mu
    sigma_t = softplus(w_sig^T x_t + b_sig) + sigma_min (sigma_min = 1e-4)
    nu = softplus(w_nu) + 2.1
    Trained with regularized Negative Log-Likelihood with L2 penalty lambda on weights.
    Used identically for B2 (Q-only, d=5), B3 (X-only, d=6), B4 (combined, d=11), and R1 (d=11+K).

    Fitting is in float64. The location parameters are optimised as phi = theta_mu / s with
    s = sd(y_train): the objective is unchanged, but the mu-curvature (~1/sigma^2 ~ 1e4) is
    rescaled to O(1), which removes the ~1e8 Hessian condition number that stopped the
    original 60-iteration float32 L-BFGS far from the optimum (CLAUDE_CODE_HANDOFF.md 1b).
    """
    def __init__(self, in_features: int, l2_reg: float = 1e-3, sigma_min: float = 1e-4):
        super().__init__()
        self.in_features = in_features
        self.l2_reg = l2_reg
        self.sigma_min = sigma_min

        # Linear layers for location and scale
        self.fc_mu = nn.Linear(in_features, 1, dtype=torch.float64)
        self.fc_sig = nn.Linear(in_features, 1, dtype=torch.float64)
        # Trainable log-degrees of freedom
        self.raw_nu = nn.Parameter(torch.tensor([2.85], dtype=torch.float64))  # softplus(2.85) + 2.1 ~ 5.0
        
        # Initialize location weights near zero, scale weights near zero
        nn.init.zeros_(self.fc_mu.weight)
        nn.init.zeros_(self.fc_mu.bias)
        nn.init.zeros_(self.fc_sig.weight)
        # Initial bias for scale: softplus(-4.6) ~ 0.010
        nn.init.constant_(self.fc_sig.bias, -4.6)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self._outputs(x, self.fc_mu.weight, self.fc_mu.bias)

    def _outputs(self, x: torch.Tensor, w_mu: torch.Tensor, b_mu: torch.Tensor):
        mu = F.linear(x, w_mu, b_mu).squeeze(-1)
        sig = F.softplus(self.fc_sig(x).squeeze(-1)) + self.sigma_min
        nu = F.softplus(self.raw_nu) + 2.1
        return mu, sig, nu

    def nll_loss(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        return self.unpenalized_nll(x, y) + self.penalty()

    def penalty(self, w_mu: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Regularization: L2 penalty strictly on linear weights (excluding biases)
        w_mu = self.fc_mu.weight if w_mu is None else w_mu
        return self.l2_reg * (w_mu.pow(2).sum() + self.fc_sig.weight.pow(2).sum())

    def unpenalized_nll(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        return -torch.mean(_student_t_log_lik(y, *self.forward(x)))

    def fit(self, X: np.ndarray, y: np.ndarray, max_iter: int = 2000,
            grad_tol: float = 1e-8, rel_change_tol: float = 1e-15, history_size: int = 100,
            max_newton_steps: int = 20):
        """
        Penalised maximum likelihood by float64 L-BFGS in preconditioned coordinates
        (see _run_lbfgs for stopping, restart and convergence rules). Non-converged fits
        set fit_report_['converged'] = False and issue a RuntimeWarning.
        Defaults (grad 1e-8, relative change 1e-15, i.e. the float64 round-off floor) put the
        objective within ~1e-15 and per-row log densities within ~1e-6 of an independent
        SciPy optimum; a looser grad 1e-6 left ~1e-5 nats/row along the weak nu direction.
        """
        self.train()
        X_t = torch.as_tensor(np.asarray(X, dtype=np.float64))
        y_t = torch.as_tensor(np.asarray(y, dtype=np.float64))

        # Reset scale bias to match training std
        std_y = float(y_t.std())
        mean_y = float(y_t.mean())
        with torch.no_grad():
            self.fc_mu.bias.fill_(mean_y)
            # softplus inverse: log(exp(std_y) - 1)
            raw_sig_init = math.log(max(1e-4, math.exp(std_y) - 1.0))
            self.fc_sig.bias.fill_(raw_sig_init)

        # Preconditioning: theta_mu = s * phi_mu
        s = std_y
        phi_w = (self.fc_mu.weight.detach() / s).clone().requires_grad_(True)
        phi_b = (self.fc_mu.bias.detach() / s).clone().requires_grad_(True)
        params = [phi_w, phi_b, self.fc_sig.weight, self.fc_sig.bias, self.raw_nu]

        def objective():
            w_mu, b_mu = s * phi_w, s * phi_b
            log_lik = _student_t_log_lik(y_t, *self._outputs(X_t, w_mu, b_mu))
            return -torch.mean(log_lik) + self.penalty(w_mu)

        self.fit_report_ = _run_lbfgs(
            params, objective,
            lambda: -torch.mean(_student_t_log_lik(y_t, *self._outputs(X_t, s * phi_w, s * phi_b))),
            lambda: F.softplus(self.raw_nu) + 2.1,
            max_iter=max_iter, grad_tol=grad_tol, rel_change_tol=rel_change_tol,
            history_size=history_size, max_newton_steps=max_newton_steps,
            label=f"StudentTRegression(d={self.in_features})",
        )
        with torch.no_grad():
            self.fc_mu.weight.copy_(s * phi_w)
            self.fc_mu.bias.copy_(s * phi_b)
        self.fit_report_["mu_precondition_scale"] = s
        self.eval()
        return self

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        self.eval()
        with torch.no_grad():
            X_t = torch.as_tensor(np.asarray(X, dtype=np.float64))
            mu, sig, nu = self.forward(X_t)
            nu_scalar = float(nu.item())
            nu_vec = np.full(len(X), nu_scalar)
            return mu.numpy(), sig.numpy(), nu_vec

    def log_density(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        mu, sig, nu = self.predict(X)
        return stats.t.logpdf(y, df=nu, loc=mu, scale=sig)


class MixtureDensityNetwork2(nn.Module):
    """
    2-Component Student-t Mixture Density Network (MDN).
    Evaluated on validation data to test whether return multi-modality improves predictive density over Student-t.
    p(y | x) = w_1(x) * t(y; mu_1, sig_1, nu_1) + w_2(x) * t(y; mu_2, sig_2, nu_2)
    where w_1(x) = sigmoid(w_w^T x + b_w), w_2(x) = 1 - w_1(x).
    """
    def __init__(self, in_features: int, l2_reg: float = 1e-3, sigma_min: float = 1e-4):
        super().__init__()
        self.in_features = in_features
        self.l2_reg = l2_reg
        self.sigma_min = sigma_min
        
        # Component 1
        self.fc_mu1 = nn.Linear(in_features, 1)
        self.fc_sig1 = nn.Linear(in_features, 1)
        self.raw_nu1 = nn.Parameter(torch.tensor([2.85], dtype=torch.float32))
        
        # Component 2
        self.fc_mu2 = nn.Linear(in_features, 1)
        self.fc_sig2 = nn.Linear(in_features, 1)
        self.raw_nu2 = nn.Parameter(torch.tensor([2.85], dtype=torch.float32))
        
        # Logit for component 1 mixing weight
        self.fc_weight = nn.Linear(in_features, 1)
        
        # Initialize
        nn.init.zeros_(self.fc_mu1.weight)
        nn.init.zeros_(self.fc_mu2.weight)
        nn.init.zeros_(self.fc_sig1.weight)
        nn.init.zeros_(self.fc_sig2.weight)
        nn.init.zeros_(self.fc_weight.weight)
        nn.init.zeros_(self.fc_weight.bias)  # sigmoid(0) = 0.5 (equal 50/50 prior)

    def forward(self, x: torch.Tensor):
        w1 = torch.sigmoid(self.fc_weight(x)).squeeze(-1)
        w2 = 1.0 - w1
        
        mu1 = self.fc_mu1(x).squeeze(-1)
        sig1 = F.softplus(self.fc_sig1(x).squeeze(-1)) + self.sigma_min
        nu1 = F.softplus(self.raw_nu1) + 2.1
        
        mu2 = self.fc_mu2(x).squeeze(-1)
        sig2 = F.softplus(self.fc_sig2(x).squeeze(-1)) + self.sigma_min
        nu2 = F.softplus(self.raw_nu2) + 2.1
        
        return (w1, w2), (mu1, sig1, nu1), (mu2, sig2, nu2)

    def nll_loss(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        (w1, w2), (mu1, sig1, nu1), (mu2, sig2, nu2) = self.forward(x)
        
        # Component 1 log-likelihood
        z1 = (y - mu1) / sig1
        log_norm1 = torch.lgamma(0.5 * (nu1 + 1.0)) - torch.lgamma(0.5 * nu1) - 0.5 * torch.log(math.pi * nu1) - torch.log(sig1)
        log_lik1 = log_norm1 - 0.5 * (nu1 + 1.0) * torch.log(1.0 + (z1 ** 2) / nu1)
        
        # Component 2 log-likelihood
        z2 = (y - mu2) / sig2
        log_norm2 = torch.lgamma(0.5 * (nu2 + 1.0)) - torch.lgamma(0.5 * nu2) - 0.5 * torch.log(math.pi * nu2) - torch.log(sig2)
        log_lik2 = log_norm2 - 0.5 * (nu2 + 1.0) * torch.log(1.0 + (z2 ** 2) / nu2)
        
        # Mixture log-likelihood: log(w1 * exp(log_lik1) + w2 * exp(log_lik2))
        log_w1 = torch.log(torch.clamp(w1, min=1e-8))
        log_w2 = torch.log(torch.clamp(w2, min=1e-8))
        term1 = log_w1 + log_lik1
        term2 = log_w2 + log_lik2
        log_mixture = torch.logaddexp(term1, term2)
        
        nll = -torch.mean(log_mixture)
        reg = self.l2_reg * (
            self.fc_mu1.weight.pow(2).sum() + self.fc_mu2.weight.pow(2).sum()
            + self.fc_sig1.weight.pow(2).sum() + self.fc_sig2.weight.pow(2).sum()
            + self.fc_weight.weight.pow(2).sum()
        )
        return nll + reg

    def fit(self, X: np.ndarray, y: np.ndarray, max_iter: int = 150):
        self.train()
        X_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.float32)
        
        std_y = float(y_t.std())
        mean_y = float(y_t.mean())
        with torch.no_grad():
            self.fc_mu1.bias.fill_(mean_y + 0.1 * std_y)
            self.fc_mu2.bias.fill_(mean_y - 0.1 * std_y)
            raw_sig1 = math.log(max(1e-4, math.exp(0.8 * std_y) - 1.0))
            raw_sig2 = math.log(max(1e-4, math.exp(1.2 * std_y) - 1.0))
            self.fc_sig1.bias.fill_(raw_sig1)
            self.fc_sig2.bias.fill_(raw_sig2)
            
        optimizer = torch.optim.LBFGS(self.parameters(), lr=0.3, line_search_fn="strong_wolfe", max_iter=max_iter)
        
        def closure():
            optimizer.zero_grad()
            loss = self.nll_loss(X_t, y_t)
            loss.backward()
            return loss

        optimizer.step(closure)
        self.eval()
        return self

    def log_density(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        self.eval()
        with torch.no_grad():
            X_t = torch.tensor(X, dtype=torch.float32)
            y_t = torch.tensor(y, dtype=torch.float32)
            (w1, w2), (mu1, sig1, nu1), (mu2, sig2, nu2) = self.forward(X_t)
            
            z1 = (y_t - mu1) / sig1
            log_norm1 = torch.lgamma(0.5 * (nu1 + 1.0)) - torch.lgamma(0.5 * nu1) - 0.5 * torch.log(math.pi * nu1) - torch.log(sig1)
            log_lik1 = log_norm1 - 0.5 * (nu1 + 1.0) * torch.log(1.0 + (z1 ** 2) / nu1)
            
            z2 = (y_t - mu2) / sig2
            log_norm2 = torch.lgamma(0.5 * (nu2 + 1.0)) - torch.lgamma(0.5 * nu2) - 0.5 * torch.log(math.pi * nu2) - torch.log(sig2)
            log_lik2 = log_norm2 - 0.5 * (nu2 + 1.0) * torch.log(1.0 + (z2 ** 2) / nu2)
            
            log_w1 = torch.log(torch.clamp(w1, min=1e-8))
            log_w2 = torch.log(torch.clamp(w2, min=1e-8))
            log_mixture = torch.logaddexp(log_w1 + log_lik1, log_w2 + log_lik2)
            return log_mixture.numpy()
