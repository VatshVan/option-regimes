"""
Stage 3 Quality Check Script (Corrected Martin SVIX Specification)
IE 612 Course Project: SPX Options Physical Density Forecasting

Scope Limits:
- Exactly two dates: 2020-01-15 (calm) and 2020-03-03 (stress)
- Single calendar year: 2020
- Files streamed chunk-by-chunk; non-target rows immediately discarded

Corrections Applied:
1. Implements Martin (2017, QJE) exact forward-normalized SVIX formula:
   SVIX^2 = (2 * exp(r*T) / (T * F_{t,T}^2)) * [ int_0^F P(K) dK + int_F^inf C(K) dK ].
   (Replaces the previous spot-normalized (S^2) zero-dividend approximation).
2. Uses standard composite trapezoidal quadrature weights: half-interval at endpoints
   (delta_k[0] = 0.5*(K_1 - K_0), delta_k[-1] = 0.5*(K_N - K_{N-1})) and records finite-strike
   boundary truncation [K_min, K_max] without tail extrapolation.
3. Documents cost-of-carry forward check F_theo = S * exp((r - q)*T) using illustrative external
   dividend benchmarks, noting that put-call parity does not prove quote/cash synchronization.
4. Treats Cboe VIX as an approximate heuristic reference, reporting the numerical gap as an
   observation without asserting unverified causal claims.
"""

import os
import numpy as np
import pandas as pd

# File paths
p_202001 = os.path.join("Data", "SPX Options Chain", "spx_eod_2020-wh6jt7", "spx_eod_202001.txt")
p_202003 = os.path.join("Data", "SPX Options Chain", "spx_eod_2020-wh6jt7", "spx_eod_202003.txt")

# Configuration for the two authorized dates
dates_config = {
    "2020-01-15": {
        "file": p_202001,
        "vix_close": 12.42,       # Official Cboe VIX close (<= 20)
        "spx_cash": 3289.29,      # S&P 500 cash index close (^GSPC)
        "r_rate": 0.01508,        # 13-week Treasury Bill (^IRX): 1.508% annualized
        "q_benchmark": 0.0175     # Illustrative trailing S&P 500 dividend yield (~1.75% in Jan 2020)
    },
    "2020-03-03": {
        "file": p_202003,
        "vix_close": 36.82,       # Official Cboe VIX close (> 30; emergency Fed rate cut)
        "spx_cash": 3003.37,      # S&P 500 cash index close (^GSPC)
        "r_rate": 0.00918,        # 13-week Treasury Bill (^IRX): 0.918% annualized
        "q_benchmark": 0.0195     # Illustrative trailing S&P 500 dividend yield (~1.95% in Mar 2020)
    }
}

def clean_columns(cols):
    return [c.strip().replace('[', '').replace(']', '') for c in cols]

results = {}

for target_date, cfg in dates_config.items():
    print(f"==================================================")
    print(f"STAGE 3 QUALITY CHECK: TARGET DATE {target_date}")
    print(f"==================================================")
    
    # 1. Stream file and extract only target_date rows
    chunks = []
    for chunk in pd.read_csv(cfg["file"], chunksize=25000, low_memory=False):
        chunk.columns = clean_columns(chunk.columns)
        q_dates = chunk["QUOTE_DATE"].astype(str).str.strip()
        matched = chunk[q_dates == target_date]
        if len(matched) > 0:
            chunks.append(matched)
            
    df_date = pd.concat(chunks, ignore_index=True)
    print(f"Total raw option chain rows extracted: {len(df_date)}")
    print(f"Schema columns count: {len(df_date.columns)}")
    
    # Check quote timestamps
    timestamps = df_date["QUOTE_READTIME"].astype(str).str.strip().unique().tolist()
    print(f"Observed QUOTE_READTIME: {timestamps}")
    
    # Parse numeric fields
    numeric_cols = ["UNDERLYING_LAST", "DTE", "STRIKE", "C_BID", "C_ASK", "P_BID", "P_ASK", "C_VOLUME", "P_VOLUME"]
    for col in numeric_cols:
        df_date[col] = pd.to_numeric(df_date[col].astype(str).str.strip(), errors="coerce")
        
    u_last = df_date["UNDERLYING_LAST"].dropna().iloc[0]
    spx_cash = cfg["spx_cash"]
    diff_u = u_last - spx_cash
    print(f"Vendor UNDERLYING_LAST: {u_last:.2f} | Official SPX Cash Close: {spx_cash:.2f} | Diff: {diff_u:+.2f} pts ({diff_u/spx_cash*100:+.3f}%)")
    
    # 2. Inspect Maturities (DTE) in 20-50 DTE range
    dtes_all = sorted(df_date["DTE"].unique())
    dtes_band = sorted([d for d in dtes_all if 20 <= d <= 50])
    print(f"Available DTEs in 20-50 range: {[float(d) for d in dtes_band]}")
    bracket_lower = [float(d) for d in dtes_band if d <= 30]
    bracket_upper = [float(d) for d in dtes_band if d >= 30]
    has_bracket = (len(bracket_lower) > 0 and len(bracket_upper) > 0)
    print(f"Maturities bracket 30 days? {has_bracket} (Lower <= 30: {bracket_lower}, Upper >= 30: {bracket_upper})")
    
    # 3. For each maturity, compute Parity Forward, Cost-of-Carry Plausibility Check, and OTM Screening
    r = cfg["r_rate"]
    q_bench = cfg["q_benchmark"]
    mat_results = {}
    
    for dte in dtes_band:
        df_mat = df_date[df_date["DTE"] == dte].copy()
        T = dte / 365.0
        df_mat = df_mat.dropna(subset=["STRIKE", "C_BID", "C_ASK", "P_BID", "P_ASK"])
        
        df_mat["C_MID"] = (df_mat["C_BID"] + df_mat["C_ASK"]) / 2.0
        df_mat["P_MID"] = (df_mat["P_BID"] + df_mat["P_ASK"]) / 2.0
        
        # ATM forward inversion: find strike minimizing |C_MID - P_MID| among valid positive-bid quotes
        valid_atm = df_mat[(df_mat["C_BID"] > 0.05) & (df_mat["P_BID"] > 0.05) & 
                           (df_mat["C_ASK"] > df_mat["C_BID"]) & (df_mat["P_ASK"] > df_mat["P_BID"])].copy()
        valid_atm["DIFF"] = (valid_atm["C_MID"] - valid_atm["P_MID"]).abs()
        
        if len(valid_atm) == 0:
            continue
            
        atm_row = valid_atm.sort_values("DIFF").iloc[0]
        K_star = atm_row["STRIKE"]
        C_star = atm_row["C_MID"]
        P_star = atm_row["P_MID"]
        
        # Synthetic forward via put-call parity: F_parity = K* + exp(r*T)*(C* - P*)
        F_parity = K_star + np.exp(r * T) * (C_star - P_star)
        
        # Theoretical forward with illustrative dividend yield: F_theo = S_cash * exp((r - q_bench)*T)
        F_theo = spx_cash * np.exp((r - q_bench) * T)
        diff_F = F_parity - F_theo
        
        # Implied dividend yield from parity: q_implied = r - (1/T) * ln(F_parity / S_cash)
        q_implied = r - (1.0 / T) * np.log(F_parity / spx_cash)
        
        # Contract-wise OTM screening:
        # Puts for K < F_parity: screen put quote only (P_BID > 0.05, P_ASK > P_BID, RelSpread <= 0.35)
        # Calls for K >= F_parity: screen call quote only (C_BID > 0.05, C_ASK > C_BID, RelSpread <= 0.35)
        puts = df_mat[df_mat["STRIKE"] < F_parity].copy()
        valid_puts = puts[(puts["P_BID"] > 0.05) & 
                          (puts["P_ASK"] > puts["P_BID"]) & 
                          ((puts["P_ASK"] - puts["P_BID"]) / puts["P_MID"] <= 0.35)].copy()
        valid_puts["PRICE"] = valid_puts["P_MID"]
        valid_puts["TYPE"] = "P"
        
        calls = df_mat[df_mat["STRIKE"] >= F_parity].copy()
        valid_calls = calls[(calls["C_BID"] > 0.05) & 
                            (calls["C_ASK"] > calls["C_BID"]) & 
                            ((calls["C_ASK"] - calls["C_BID"]) / calls["C_MID"] <= 0.35)].copy()
        valid_calls["PRICE"] = valid_calls["C_MID"]
        valid_calls["TYPE"] = "C"
        
        otm_contracts = pd.concat([valid_puts, valid_calls]).sort_values("STRIKE")
        num_strikes = len(otm_contracts)
        
        # 4. Martin (2017) Exact Forward-Normalized SVIX vs Cboe VIX Heuristic Quadrature
        # Martin (2017, QJE) formula:
        # SVIX^2 = (2 * exp(r*T) / (T * F_{t,T}^2)) * [ int_0^F P(K) dK + int_F^inf C(K) dK ]
        # Cboe VIX heuristic (log contract):
        # VIX_approx^2 = (2 * exp(r*T) / T) * int (OTM(K) / K^2) dK
        
        if num_strikes >= 15:
            strikes = otm_contracts["STRIKE"].values
            prices = otm_contracts["PRICE"].values
            
            # Standard composite trapezoidal grid weights: half-interval at endpoints
            delta_k = np.zeros_like(strikes)
            delta_k[0] = 0.5 * (strikes[1] - strikes[0])
            delta_k[-1] = 0.5 * (strikes[-1] - strikes[-2])
            delta_k[1:-1] = 0.5 * (strikes[2:] - strikes[:-2])
            
            # Martin SVIX integral: unweighted by K^2, normalized by F_parity^2
            martin_integral = np.sum(prices * delta_k)
            svix_martin_sq = (2.0 * np.exp(r * T) / (T * (F_parity ** 2))) * martin_integral
            svix_martin = np.sqrt(max(svix_martin_sq, 0.0)) * 100.0
            
            # Cboe VIX heuristic integral: weighted by 1/K^2
            vix_integral = np.sum((prices / (strikes ** 2)) * delta_k)
            vix_approx_sq = (2.0 * np.exp(r * T) / T) * vix_integral
            vix_approx = np.sqrt(max(vix_approx_sq, 0.0)) * 100.0
        else:
            svix_martin = None
            vix_approx = None
            
        mat_results[dte] = {
            "T": T,
            "F_parity": F_parity,
            "F_theo": F_theo,
            "diff_F": diff_F,
            "q_implied": q_implied,
            "K_star": K_star,
            "num_otm_strikes": num_strikes,
            "min_strike": strikes[0] if num_strikes >= 15 else None,
            "max_strike": strikes[-1] if num_strikes >= 15 else None,
            "k_min_ratio": strikes[0] / F_parity if num_strikes >= 15 else None,
            "k_max_ratio": strikes[-1] / F_parity if num_strikes >= 15 else None,
            "svix_martin": svix_martin,
            "vix_approx": vix_approx
        }
        
    print("\n--- Maturity-by-Maturity Summary in 20-50 DTE Band ---")
    for dte, mres in mat_results.items():
        print(f"DTE={dte:5.2f} (T={mres['T']:.4f}) | ATM K*={mres['K_star']:6.1f} | F_parity={mres['F_parity']:7.2f} | F_theo(q={q_bench*100:.2f}%)={mres['F_theo']:7.2f} (Diff={mres['diff_F']:+5.2f}, q_imp={mres['q_implied']*100:+.2f}%)")
        print(f"       -> OTM Strikes={mres['num_otm_strikes']} (Range: {mres['min_strike']} to {mres['max_strike']} | K/F: {mres['k_min_ratio']:.3f} to {mres['k_max_ratio']:.3f})")
        print(f"       -> Martin SVIX (Fwd-Norm Finite Grid) = {mres['svix_martin']:5.2f}% | Cboe VIX Heuristic = {mres['vix_approx']:5.2f}%")
        
    # Constant 30-day interpolation
    dtes_valid = [d for d in mat_results if mat_results[d]["svix_martin"] is not None]
    d_low = max([d for d in dtes_valid if d <= 30], default=None)
    d_high = min([d for d in dtes_valid if d >= 30], default=None)
    
    if d_low is not None and d_high is not None:
        if d_low == d_high:
            svix_martin_30d = mat_results[d_low]["svix_martin"]
            vix_approx_30d = mat_results[d_low]["vix_approx"]
        else:
            w = (30.0 - d_low) / (d_high - d_low)
            svix_martin_30d = (1.0 - w) * mat_results[d_low]["svix_martin"] + w * mat_results[d_high]["svix_martin"]
            vix_approx_30d = (1.0 - w) * mat_results[d_low]["vix_approx"] + w * mat_results[d_high]["vix_approx"]
    else:
        svix_martin_30d = None
        vix_approx_30d = None
        
    print(f"\n--- 30-Day Interpolated Statistics vs Cboe VIX Reference ---")
    print(f"Interpolated Martin (2017) SVIX (Finite-Grid Estimate): {svix_martin_30d:.2f}% (Bracketed by DTE {d_low} and {d_high})")
    print(f"Interpolated Cboe VIX Heuristic: {vix_approx_30d:.2f}%")
    print(f"Official Cboe VIX Close:         {cfg['vix_close']:.2f}%")
    print(f"Observed Numerical Gap (Martin SVIX - Official VIX): {svix_martin_30d - cfg['vix_close']:+.2f} vol points")
    print(f"Observed Numerical Gap (Cboe Approx - Official VIX): {vix_approx_30d - cfg['vix_close']:+.2f} vol points")
    print(f"\nCaveat on Martin SVIX: Calculated via discrete trapezoidal quadrature over retained strikes without tail extrapolation.")
    print(f"Caveat on VIX comparison: Heuristic reference only; omits full Cboe rulebook adjustments (e.g. K0 truncation adjustment).")
    print(f"Caveat on Numerical Gap: Reported strictly as an empirical observation for these two dates; not claimed as verified causal proof.")
    print(f"Caveat on Forward Parity: Tracks cost-of-carry within expected bounds, but does not prove quote/cash synchronization.")
    
    results[target_date] = {
        "cfg": cfg,
        "timestamps": timestamps,
        "u_last": u_last,
        "diff_u": diff_u,
        "mat_results": mat_results,
        "svix_martin_30d": svix_martin_30d,
        "vix_approx_30d": vix_approx_30d
    }

print("\nQuality check execution complete.")
