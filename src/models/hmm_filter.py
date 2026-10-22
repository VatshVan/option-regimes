"""
hmm_filter.py
=============
Causal Hidden Markov Model (HMM) with continuous Gaussian emissions for regime filtering.
Governing specification: stage5_modeling_specification.md Section 5.

Features:
- Bivariate emission vector: y_t = [std_return, std_RV20d]^T
- K in {2, 3} latent regimes
- Diagonal covariance matrices with variance floor (sigma^2 >= 1e-4)
- In-sample Baum-Welch EM estimation
- Canonical state sorting by volatility to prevent label switching across refits
- Causal forward-only filtering recursion (pi_t in Delta^{K-1})
- Strict anti-leakage: zero smoothed probabilities, zero Viterbi paths
- Diagnostics: occupancy >= 5%, dwell time >= 5 sessions
"""

import math
import numpy as np
from scipy.stats import norm

class CausalGaussianHMM:
    def __init__(self, n_states: int = 2, max_iter: int = 100, tol: float = 1e-4, random_state: int = 42):
        assert n_states in [2, 3], "Protocol restricts K to 2 or 3 latent regimes"
        self.n_states = n_states
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        
        # Parameters
        self.pi_init = None  # Initial state distribution (K,)
        self.trans_mat = None  # Transition matrix (K, K)
        self.means = None  # Emission means (K, D)
        self.vars = None  # Emission variances (K, D)
        self.is_fitted = False
        
    def _init_params(self, Y: np.ndarray):
        """Initializes parameters using quantiles of the volatility feature (dim 1)."""
        rng = np.random.RandomState(self.random_state)
        N, D = Y.shape
        K = self.n_states
        
        # Initial state probabilities
        self.pi_init = np.full(K, 1.0 / K)
        
        # Transition matrix initialized with strong diagonal persistence (e.g., 0.95)
        self.trans_mat = np.full((K, K), (1.0 - 0.95) / (K - 1))
        np.fill_diagonal(self.trans_mat, 0.95)
        
        # Emission means and variances sorted by volatility feature (column 1)
        # Partition data into K volatility quantiles
        vol_col = Y[:, 1]
        quantiles = np.linspace(0, 100, K + 1)
        self.means = np.zeros((K, D))
        self.vars = np.zeros((K, D))
        
        for k in range(K):
            q_low = np.percentile(vol_col, quantiles[k])
            q_high = np.percentile(vol_col, quantiles[k + 1])
            mask = (vol_col >= q_low) & (vol_col <= q_high)
            if np.sum(mask) < 2:
                self.means[k] = np.mean(Y, axis=0) + rng.randn(D) * 0.1
                self.vars[k] = np.var(Y, axis=0)
            else:
                self.means[k] = np.mean(Y[mask], axis=0)
                self.vars[k] = np.var(Y[mask], axis=0)
                
        # Enforce minimum variance floor
        self.vars = np.maximum(self.vars, 1e-4)

    def _emission_log_prob(self, Y: np.ndarray) -> np.ndarray:
        """Computes log N(y_t; mu_k, diag(var_k)) for all t and k. Returns (N, K)."""
        N, D = Y.shape
        K = self.n_states
        log_B = np.zeros((N, K))
        
        for k in range(K):
            # log N(y; mu, sigma^2) = -0.5 * sum(log(2*pi*var) + (y - mu)^2 / var)
            diff = Y - self.means[k]
            var = self.vars[k]
            log_pdf = -0.5 * (np.sum(np.log(2.0 * math.pi * var)) + np.sum((diff ** 2) / var, axis=1))
            log_B[:, k] = log_pdf
            
        return log_B

    def fit(self, Y: np.ndarray):
        """Fits Gaussian HMM parameters on in-sample emissions using Baum-Welch EM."""
        N, D = Y.shape
        K = self.n_states
        self._init_params(Y)
        
        prev_log_lik = -np.inf
        
        for iteration in range(self.max_iter):
            # --- E-Step: Forward-Backward on Training Set ---
            log_B = self._emission_log_prob(Y)
            B = np.exp(log_B - np.max(log_B, axis=1, keepdims=True))
            
            # Forward pass with scaling
            alpha = np.zeros((N, K))
            c = np.zeros(N)
            
            # t = 0
            alpha[0] = self.pi_init * B[0]
            c[0] = np.sum(alpha[0])
            if c[0] == 0 or np.isnan(c[0]):
                c[0] = 1e-12
            alpha[0] /= c[0]
            
            for t in range(1, N):
                alpha[t] = B[t] * np.dot(alpha[t - 1], self.trans_mat)
                c[t] = np.sum(alpha[t])
                if c[t] == 0 or np.isnan(c[t]):
                    c[t] = 1e-12
                alpha[t] /= c[t]
                
            # Log-likelihood
            log_lik = np.sum(np.log(c))
            
            # Backward pass with same scaling
            beta = np.zeros((N, K))
            beta[N - 1] = 1.0 / c[N - 1]
            
            for t in range(N - 2, -1, -1):
                beta[t] = np.dot(self.trans_mat, B[t + 1] * beta[t + 1]) / c[t]
                
            # Posteriors gamma_t(k) = P(z_t = k | Y_{1:N})
            gamma = alpha * beta
            gamma_sum = np.sum(gamma, axis=1, keepdims=True)
            gamma_sum[gamma_sum == 0] = 1e-12
            gamma /= gamma_sum
            
            # Transitions: vectorized sum_xi
            term2 = B[1:] * beta[1:]
            trans_sums = np.sum(alpha[:-1] * (term2 @ self.trans_mat.T), axis=1, keepdims=True)
            trans_sums[trans_sums == 0] = 1e-12
            alpha_scaled = alpha[:-1] / trans_sums
            sum_xi = (alpha_scaled.T @ term2) * self.trans_mat
            sum_gamma = np.sum(gamma[:-1], axis=0, keepdims=True).T
            sum_gamma[sum_gamma == 0] = 1e-12
            self.trans_mat = sum_xi / sum_gamma
            # Normalize rows
            row_sums = np.sum(self.trans_mat, axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1.0
            self.trans_mat /= row_sums
            
            # Means and Variances
            gamma_k_sum = np.sum(gamma, axis=0)
            gamma_k_sum[gamma_k_sum == 0] = 1e-12
            
            for k in range(K):
                w = gamma[:, k:k+1]
                self.means[k] = np.sum(w * Y, axis=0) / gamma_k_sum[k]
                diff = Y - self.means[k]
                self.vars[k] = np.sum(w * (diff ** 2), axis=0) / gamma_k_sum[k]
                
            # Enforce variance floor
            self.vars = np.maximum(self.vars, 1e-4)
            
            # Convergence check
            if abs(log_lik - prev_log_lik) < self.tol:
                break
            prev_log_lik = log_lik
            
        # Canonicalize state ordering by realized volatility mean (column 1)
        # State 0 = Low Vol, State 1 = High Vol (State 2 = Extreme Vol)
        order = np.argsort(self.means[:, 1])
        self._reorder_states(order)
        self.is_fitted = True
        return self

    def _reorder_states(self, order: np.ndarray):
        """Permutes states to match canonical volatility ordering."""
        self.pi_init = self.pi_init[order]
        self.trans_mat = self.trans_mat[order, :][:, order]
        self.means = self.means[order]
        self.vars = self.vars[order]

    def forward_filter(self, Y: np.ndarray) -> np.ndarray:
        """
        Propagates CAUSAL forward filtering recursion pi_t = P(z_t = k | y_1, ..., y_t).
        Never uses future observations.
        Returns: (N, K) array of filtered state probabilities pi_t in Delta^{K-1}.
        """
        assert self.is_fitted, "Model must be fitted before forward filtering"
        N, D = Y.shape
        K = self.n_states
        
        log_B = self._emission_log_prob(Y)
        B = np.exp(log_B - np.max(log_B, axis=1, keepdims=True))
        
        pi_filtered = np.zeros((N, K))
        alpha = np.zeros(K)
        
        # t = 0
        alpha = self.pi_init * B[0]
        c = np.sum(alpha)
        if c == 0 or np.isnan(c):
            c = 1e-12
        alpha /= c
        pi_filtered[0] = alpha
        
        # t = 1, ..., N-1
        for t in range(1, N):
            alpha = B[t] * np.dot(alpha, self.trans_mat)
            c = np.sum(alpha)
            if c == 0 or np.isnan(c):
                c = 1e-12
            alpha /= c
            pi_filtered[t] = alpha
            
        return pi_filtered

    def compute_dwell_times(self) -> np.ndarray:
        """Expected dwell time E[D_k] = 1 / (1 - A_kk) in sessions."""
        dwell = np.zeros(self.n_states)
        for k in range(self.n_states):
            diag = self.trans_mat[k, k]
            if diag >= 1.0:
                dwell[k] = 1000.0
            else:
                dwell[k] = 1.0 / (1.0 - diag)
        return dwell

    def compute_occupancies(self, pi_filtered: np.ndarray) -> np.ndarray:
        """Empirical occupancy of argmax state across filtered trajectory."""
        argmax_states = np.argmax(pi_filtered, axis=1)
        occupancies = np.zeros(self.n_states)
        for k in range(self.n_states):
            occupancies[k] = np.mean(argmax_states == k)
        return occupancies
