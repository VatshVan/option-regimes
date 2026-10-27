"""
Tests for src/models/hmm_filter.py against independent log-space computations.
"""
import numpy as np
import pytest
from scipy.special import logsumexp
from scipy.stats import norm

from src.models.hmm_filter import CausalGaussianHMM


def _emissions(hmm, Y):
    return np.stack([norm.logpdf(Y, hmm.means[k], np.sqrt(hmm.vars[k])).sum(axis=1)
                     for k in range(hmm.n_states)], axis=1)


def log_forward(hmm, Y):
    """Independent log-space forward recursion: returns log p(Y) and filtered probabilities."""
    log_B = _emissions(hmm, Y)
    log_A = np.log(hmm.trans_mat)
    log_alpha = np.log(hmm.pi_init) + log_B[0]
    filtered = [log_alpha - logsumexp(log_alpha)]
    for t in range(1, len(Y)):
        log_alpha = log_B[t] + logsumexp(log_alpha[:, None] + log_A, axis=0)
        filtered.append(log_alpha - logsumexp(log_alpha))
    return float(logsumexp(log_alpha)), np.exp(np.array(filtered))


@pytest.fixture(scope="module")
def two_regime_data():
    rng = np.random.default_rng(11)
    n = 1500
    z = np.zeros(n, dtype=int)
    for t in range(1, n):
        z[t] = z[t - 1] if rng.random() < 0.97 else 1 - z[t - 1]
    r = np.where(z == 1, 2.0, 0.7) * rng.standard_normal(n)
    v = np.where(z == 1, 1.5, -0.5) + 0.3 * rng.standard_normal(n)
    return np.column_stack([r, v])


def test_monitored_log_likelihood_is_true_log_likelihood(two_regime_data):
    Y = two_regime_data
    hmm = CausalGaussianHMM(n_states=2, max_iter=1).fit(Y)
    ref = CausalGaussianHMM(n_states=2)
    ref._init_params(Y)  # history[0] is evaluated at the initial parameters
    ll_ref, _ = log_forward(ref, Y)
    assert hmm.log_lik_history_[0] == pytest.approx(ll_ref, rel=1e-12, abs=1e-8)


def test_em_log_likelihood_is_monotone(two_regime_data):
    hmm = CausalGaussianHMM(n_states=2, max_iter=200, tol=1e-8).fit(two_regime_data)
    diffs = np.diff(hmm.log_lik_history_)
    assert np.all(diffs >= -1e-7)
    assert hmm.converged_ and hmm.n_iter_ == len(hmm.log_lik_history_)


def test_forward_filter_matches_log_space_and_is_causal(two_regime_data):
    Y = two_regime_data
    hmm = CausalGaussianHMM(n_states=2, max_iter=50).fit(Y[:1000])
    pi = hmm.forward_filter(Y)
    _, pi_ref = log_forward(hmm, Y)
    np.testing.assert_allclose(pi, pi_ref, atol=1e-10)
    # causality: filtering a prefix gives the same probabilities as filtering the full series
    np.testing.assert_allclose(hmm.forward_filter(Y[:700]), pi[:700], atol=0)


def test_states_sorted_by_volatility(two_regime_data):
    hmm = CausalGaussianHMM(n_states=2).fit(two_regime_data)
    assert hmm.means[0, 1] < hmm.means[1, 1]
    np.testing.assert_allclose(hmm.trans_mat.sum(axis=1), 1.0)
