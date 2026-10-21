"""
options_moments.py
==================
Implementation of model-free option moments and implied volatility inversion:
1. Martin (2017) Simple Variance Swap Index (SVIX)
2. Bakshi, Kapadia, and Madan (2003) Risk-Neutral Skewness (QSkew) and Kurtosis (QKurt)
3. Black-76 ATM Implied Volatility (ATM_IV)
4. Constant-maturity 30-day and 60-day interpolation and Term Structure Slope
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq

from .options_cleaning import invert_synthetic_forward, screen_otm_quotes


def compute_martin_svix(
    strikes: np.ndarray,
    prices: np.ndarray,
    F_parity: float,
    r: float,
    T: float
) -> Tuple[Optional[float], Optional[float], Dict[str, Any]]:
    """
    Computes Martin (2017) Simple Variance Swap Index (SVIX) via forward-normalized
    discrete trapezoidal quadrature over retained out-of-the-money options.
    
    Formula:
        SVIX^2 = (2 * exp(r * T) / (T * F^2)) * sum(M(K_i) * delta_K_i)
        
    Parameters
    ----------
    strikes : np.ndarray
        Sorted 1D array of retained strike prices.
    prices : np.ndarray
        Array of option midpoint prices corresponding to strikes.
    F_parity : float
        Synthetic forward price.
    r : float
        Annualized continuously compounded risk-free rate.
    T : float
        Time to expiration in years (DTE / 365.0).
        
    Returns
    -------
    svix_ann : float or None
        Annualized SVIX in decimal units (e.g. 0.1200 for 12.00%).
    svix_sq : float or None
        Annualized simple return variance (SVIX^2).
    diagnostics : Dict[str, Any]
        Integration details including strike bounds and discrete integral value.
    """
    diag: Dict[str, Any] = {
        "status": "FAILED",
        "num_strikes": len(strikes),
        "k_min": None,
        "k_max": None,
        "integral_value": None,
        "failure_reason": None
    }
    
    if len(strikes) < 15:
        diag["failure_reason"] = f"Insufficient strikes for numerical quadrature (got {len(strikes)}, min required: 15)"
        return None, None, diag
        
    if T <= 0 or F_parity <= 0:
        diag["failure_reason"] = f"Invalid maturity T={T} or forward F={F_parity}"
        return None, None, diag
        
    N = len(strikes)
    delta_k = np.zeros(N)
    delta_k[0] = 0.5 * (strikes[1] - strikes[0])
    delta_k[-1] = 0.5 * (strikes[-1] - strikes[-2])
    delta_k[1:-1] = 0.5 * (strikes[2:] - strikes[:-2])
    
    integral_val = float(np.sum(prices * delta_k))
    svix_sq = (2.0 * np.exp(r * T) / (T * (F_parity ** 2))) * integral_val
    svix_ann = float(np.sqrt(max(svix_sq, 0.0)))
    
    diag.update({
        "status": "SUCCESS",
        "k_min": float(strikes[0]),
        "k_max": float(strikes[-1]),
        "integral_value": integral_val,
        "svix_sq": float(svix_sq),
        "svix_ann": svix_ann,
        "finite_strike_note": "Discrete finite-grid estimate without tail extrapolation"
    })
    
    return svix_ann, svix_sq, diag


def compute_bkm_moments(
    strikes: np.ndarray,
    prices: np.ndarray,
    types: np.ndarray,
    F_parity: float,
    r: float,
    T: float,
    ref_price: Optional[float] = None
) -> Tuple[Optional[float], Optional[float], Dict[str, Any]]:
    """
    Computes Bakshi, Kapadia, and Madan (2003) centered, standardized risk-neutral
    skewness (QSkew) and centered, standardized risk-neutral kurtosis (QKurt;
    non-excess kurtosis, Gaussian benchmark = 3.0) from raw quadratic (V),
    cubic (W), and quartic (X) contract integrals.
    
    Mathematical Definitions:
    -------------------------
    1. Raw option-implied contract moments (prices of power payoff contracts):
       V(t, tau) = E_t^Q [ exp(-r*tau) * R^2 ]  (Volatility contract price)
       W(t, tau) = E_t^Q [ exp(-r*tau) * R^3 ]  (Cubic contract price)
       X(t, tau) = E_t^Q [ exp(-r*tau) * R^4 ]  (Quartic contract price)
       where R = ln(S_T / S_ref).
       Undiscounted raw moments: E^Q[R^2] = exp(r*tau)*V, E^Q[R^3] = exp(r*tau)*W, E^Q[R^4] = exp(r*tau)*X.
       
    2. Risk-neutral expected log return (mean):
       mu_Q = exp(r*tau) - 1 - (exp(r*tau)/2)*V - (exp(r*tau)/6)*W - (exp(r*tau)/24)*X
       
    3. Risk-neutral central moments (centered about mu_Q):
       Var_Q = E^Q[(R - mu_Q)^2] = exp(r*tau)*V - (mu_Q)^2
       mu_3  = E^Q[(R - mu_Q)^3] = exp(r*tau)*W - 3*mu_Q*exp(r*tau)*V + 2*(mu_Q)^3
       mu_4  = E^Q[(R - mu_Q)^4] = exp(r*tau)*X - 4*mu_Q*exp(r*tau)*W + 6*(mu_Q)^2*exp(r*tau)*V - 3*(mu_Q)^4
       
    4. Standardized dimensionless shape parameters:
       QSkew = mu_3 / (Var_Q)^(3/2)   [Centered, standardized 3rd central moment]
       QKurt = mu_4 / (Var_Q)^2       [Centered, standardized 4th central moment (non-excess; normal = 3.0)]
       
    Parameters
    ----------
    strikes : np.ndarray
        Sorted 1D array of strike prices.
    prices : np.ndarray
        Midpoint prices of retained OTM options.
    types : np.ndarray
        Array of 'C' (call) or 'P' (put) flags.
    F_parity : float
        Synthetic forward price.
    r : float
        Risk-free rate.
    T : float
        Time to expiration in years.
    ref_price : float, optional
        Reference price for moneyness ln(K / S_ref). Default is F_parity.
        
    Returns
    -------
    qskew : float or None
        Centered, standardized risk-neutral skewness (dimensionless).
    qkurt : float or None
        Centered, standardized risk-neutral kurtosis (dimensionless; non-excess, Gaussian = 3.0).
    diagnostics : Dict[str, Any]
        Details of V, W, X contract prices, mu_Q, Var_Q, and central moments.
    """
    diag: Dict[str, Any] = {
        "status": "FAILED",
        "qskew": None,
        "qkurt": None,
        "V_contract": None,
        "W_contract": None,
        "X_contract": None,
        "mu_Q": None,
        "var_Q": None,
        "failure_reason": None
    }
    
    if len(strikes) < 15:
        diag["failure_reason"] = f"Insufficient strikes for BKM integration ({len(strikes)} < 15)"
        return None, None, diag
        
    S_ref = ref_price if ref_price is not None else F_parity
    if S_ref <= 0 or T <= 0:
        diag["failure_reason"] = f"Invalid reference price {S_ref} or maturity {T}"
        return None, None, diag
        
    N = len(strikes)
    delta_k = np.zeros(N)
    delta_k[0] = 0.5 * (strikes[1] - strikes[0])
    delta_k[-1] = 0.5 * (strikes[-1] - strikes[-2])
    delta_k[1:-1] = 0.5 * (strikes[2:] - strikes[:-2])
    
    h_v = np.zeros(N)
    h_w = np.zeros(N)
    h_x = np.zeros(N)
    
    for i in range(N):
        K = strikes[i]
        if types[i] == 'C' or K >= S_ref:
            # Call side: K >= S_ref
            m = np.log(K / S_ref)
            h_v[i] = (2.0 * (1.0 - m)) / (K ** 2)
            h_w[i] = (6.0 * m - 3.0 * (m ** 2)) / (K ** 2)
            h_x[i] = (12.0 * (m ** 2) - 4.0 * (m ** 3)) / (K ** 2)
        else:
            # Put side: K < S_ref
            m = np.log(S_ref / K)
            h_v[i] = (2.0 * (1.0 + m)) / (K ** 2)
            h_w[i] = -(6.0 * m + 3.0 * (m ** 2)) / (K ** 2)
            h_x[i] = (12.0 * (m ** 2) + 4.0 * (m ** 3)) / (K ** 2)
            
    V = float(np.sum(h_v * prices * delta_k))
    W = float(np.sum(h_w * prices * delta_k))
    X = float(np.sum(h_x * prices * delta_k))
    
    ert = np.exp(r * T)
    mu_q = ert - 1.0 - (ert / 2.0) * V - (ert / 6.0) * W - (ert / 24.0) * X
    var_q = ert * V - (mu_q ** 2)
    
    if var_q <= 1e-12:
        diag["failure_reason"] = f"Non-positive risk-neutral variance {var_q}"
        return None, None, diag
        
    mu_3 = ert * W - 3.0 * mu_q * ert * V + 2.0 * (mu_q ** 3)
    mu_4 = ert * X - 4.0 * mu_q * ert * W + 6.0 * (mu_q ** 2) * ert * V - 3.0 * (mu_q ** 4)
    qskew = mu_3 / (var_q ** 1.5)
    qkurt = mu_4 / (var_q ** 2)
    
    diag.update({
        "status": "SUCCESS",
        "V_contract_raw": V,
        "W_contract_raw": W,
        "X_contract_raw": X,
        "undiscounted_raw_m2": float(ert * V),
        "undiscounted_raw_m3": float(ert * W),
        "undiscounted_raw_m4": float(ert * X),
        "mu_Q": float(mu_q),
        "var_Q_central_m2": float(var_q),
        "mu_3_central": float(mu_3),
        "mu_4_central": float(mu_4),
        "model_free_vol": float(np.sqrt(max(var_q / T, 0.0))),
        "qskew": float(qskew),
        "qkurt": float(qkurt),
        "kurtosis_type": "Centered, standardized 4th central moment (non-excess; normal = 3.0)",
        "ref_price": float(S_ref)
    })
    
    return float(qskew), float(qkurt), diag


def bs_call_black76(F: float, K: float, r: float, T: float, sigma: float) -> float:
    """Black-76 European forward call pricing function."""
    if sigma <= 0 or T <= 0:
        return max(0.0, (F - K) * np.exp(-r * T))
    d1 = (np.log(F / K) + 0.5 * (sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return float(np.exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2)))


def bs_put_black76(F: float, K: float, r: float, T: float, sigma: float) -> float:
    """Black-76 European forward put pricing function."""
    if sigma <= 0 or T <= 0:
        return max(0.0, (K - F) * np.exp(-r * T))
    d1 = (np.log(F / K) + 0.5 * (sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return float(np.exp(-r * T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1)))


def invert_black76_iv(
    price: float,
    F: float,
    K: float,
    r: float,
    T: float,
    is_call: bool = True
) -> Optional[float]:
    """
    Numerically inverts Black-76 implied volatility from an option midpoint price.
    
    Parameters
    ----------
    price : float
        Observed midpoint price.
    F : float
        Synthetic forward price.
    K : float
        Strike price.
    r : float
        Risk-free rate.
    T : float
        Time to expiration in years.
    is_call : bool
        True if call, False if put.
        
    Returns
    -------
    iv : float or None
        Annualized implied volatility in decimal (e.g. 0.1019 for 10.19%).
    """
    intrinsic = max(0.0, (F - K) * np.exp(-r * T)) if is_call else max(0.0, (K - F) * np.exp(-r * T))
    if price <= intrinsic or price <= 0 or T <= 0 or F <= 0:
        return None
        
    pricing_fn = bs_call_black76 if is_call else bs_put_black76
    try:
        iv = brentq(lambda sig: pricing_fn(F, K, r, T, sig) - price, 1e-4, 5.0, xtol=1e-7)
        return float(iv)
    except Exception:
        return None


def compute_tenor_moments(
    df_tenor: pd.DataFrame,
    r: float,
    min_bid: float = 0.05,
    max_rel_spread: float = 0.35,
    ref_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Orchestrates quote screening, forward inversion, SVIX, BKM moments, and ATM IV
    for a single maturity tenor.
    """
    res: Dict[str, Any] = {
        "status": "FAILED",
        "DTE": None,
        "T": None,
        "F_parity": None,
        "K_star": None,
        "ATM_IV": None,
        "SVIX": None,
        "SVIX_sq": None,
        "QSkew": None,
        "QKurt": None,
        "num_otm_strikes": 0,
        "diagnostics": {}
    }
    
    # 1. Forward Inversion
    F_parity, K_star, diag_fwd = invert_synthetic_forward(df_tenor, r, min_bid=min_bid)
    res["diagnostics"]["forward_inversion"] = diag_fwd
    if F_parity is None or K_star is None:
        res["failure_reason"] = diag_fwd.get("failure_reason", "Forward inversion failed")
        return res
        
    dte = float(diag_fwd["DTE"])
    T = float(diag_fwd["T"])
    res["DTE"] = dte
    res["T"] = T
    res["F_parity"] = F_parity
    res["K_star"] = K_star
    
    # 2. Contract-Wise OTM Screening
    df_otm, diag_screen = screen_otm_quotes(
        df_tenor, F_parity, min_bid=min_bid, max_rel_spread=max_rel_spread
    )
    res["diagnostics"]["screening"] = diag_screen
    res["num_otm_strikes"] = len(df_otm)
    
    if len(df_otm) < 15:
        res["failure_reason"] = f"Insufficient liquid OTM strikes ({len(df_otm)} < 15)"
        return res
        
    strikes = df_otm['strike'].values
    prices = df_otm['price'].values
    types = df_otm['type'].values
    
    # 3. Martin SVIX
    svix_ann, svix_sq, diag_svix = compute_martin_svix(strikes, prices, F_parity, r, T)
    res["diagnostics"]["svix"] = diag_svix
    res["SVIX"] = svix_ann
    res["SVIX_sq"] = svix_sq
    
    # 4. BKM Moments
    qskew, qkurt, diag_bkm = compute_bkm_moments(
        strikes, prices, types, F_parity, r, T, ref_price=ref_price
    )
    res["diagnostics"]["bkm"] = diag_bkm
    res["QSkew"] = qskew
    res["QKurt"] = qkurt
    
    # 5. ATM Implied Volatility Inversion
    # Invert from ATM call quote midpoint
    c_mid = diag_fwd.get("C_mid")
    if c_mid is not None:
        atm_iv = invert_black76_iv(c_mid, F_parity, K_star, r, T, is_call=True)
        res["ATM_IV"] = atm_iv
    
    if svix_ann is not None and qskew is not None and res["ATM_IV"] is not None:
        res["status"] = "SUCCESS"
    else:
        res["status"] = "PARTIAL"
        
    return res


def interpolate_constant_maturity(
    tenor_results: Dict[float, Dict[str, Any]],
    target_dte: float = 30.0
) -> Tuple[Optional[Dict[str, float]], Dict[str, Any]]:
    """
    Linearly interpolates feature moments across tenors to a target constant maturity.
    
    Parameters
    ----------
    tenor_results : Dict[float, Dict[str, Any]]
        Dictionary keyed by DTE containing computed tenor moments.
    target_dte : float
        Target constant maturity in days (e.g., 30.0 or 60.0).
        
    Returns
    -------
    interpolated_features : Dict[str, float] or None
        Dict containing interpolated SVIX, QSkew, QKurt, ATM_IV.
    diagnostics : Dict[str, Any]
        Details on bracketing tenors and interpolation weights.
    """
    valid_dtes = [
        d for d, r in tenor_results.items()
        if r.get("status") in ("SUCCESS", "PARTIAL") and r.get("SVIX") is not None
    ]
    diag: Dict[str, Any] = {
        "target_dte": target_dte,
        "available_valid_dtes": valid_dtes,
        "d_low": None,
        "d_high": None,
        "weight_high": None,
        "is_exact": False,
        "status": "FAILED"
    }
    
    if not valid_dtes:
        diag["failure_reason"] = "No valid tenors available for interpolation"
        return None, diag
        
    d_low_candidates = [d for d in valid_dtes if d <= target_dte]
    d_high_candidates = [d for d in valid_dtes if d >= target_dte]
    
    if not d_low_candidates or not d_high_candidates:
        diag["failure_reason"] = f"Valid tenors do not bracket target DTE {target_dte} (Low: {d_low_candidates}, High: {d_high_candidates})"
        return None, diag
        
    d_low = max(d_low_candidates)
    d_high = min(d_high_candidates)
    diag["d_low"] = d_low
    diag["d_high"] = d_high
    
    features_to_interp = ["SVIX", "QSkew", "QKurt", "ATM_IV"]
    out: Dict[str, float] = {}
    
    if d_low == d_high:
        diag["is_exact"] = True
        diag["weight_high"] = 0.0
        for feat in features_to_interp:
            val = tenor_results[d_low].get(feat)
            out[feat] = float(val) if val is not None else np.nan
    else:
        w = (target_dte - d_low) / (d_high - d_low)
        diag["weight_high"] = float(w)
        for feat in features_to_interp:
            v_low = tenor_results[d_low].get(feat)
            v_high = tenor_results[d_high].get(feat)
            if v_low is not None and v_high is not None and not np.isnan(v_low) and not np.isnan(v_high):
                out[feat] = float((1.0 - w) * v_low + w * v_high)
            else:
                out[feat] = np.nan
                
    diag["status"] = "SUCCESS"
    return out, diag
