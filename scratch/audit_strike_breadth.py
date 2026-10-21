"""
audit_strike_breadth.py
=======================
Audits the early-sample strike breadth (2010-2012) for SPX options in the 20-50 DTE band.
Tests:
1. Forward parity inversion for each maturity in 20 <= DTE <= 50.
2. Contract-wise OTM screening:
   - For K < F: Put bid > 0.05, ask > bid, rel_spread <= 0.35
   - For K >= F: Call bid > 0.05, ask > bid, rel_spread <= 0.35
3. Strike breadth criteria:
   - Retained liquid strikes >= 30
   - Moneyness span: K_min / S <= 0.85 and K_max / S >= 1.15
4. Constant-maturity 30-day bracketing:
   - Whether valid tenors bracket target DTE = 30.0 (DTE_low <= 30 <= DTE_high)
"""

import os
import sys
import glob
import json
import time

sys.path.insert(0, os.path.abspath("."))

import numpy as np
import pandas as pd

from src.features.options_cleaning import clean_options_chain, invert_synthetic_forward, screen_otm_quotes
from src.features.options_moments import compute_martin_svix, compute_bkm_moments, invert_black76_iv


def audit_early_strike_breadth(base_dir=r"Data\SPX Options Chain", years=[2010, 2011, 2012]):
    folders = [
        ('2010', 'spx_eod_2010-hixkhi'),
        ('2011', 'spx_eod_2011-mpv77a'),
        ('2012', 'spx_eod_2012-ftrobg'),
    ]
    
    # We will record daily audit results
    daily_results = []
    
    for yr, folder_name in folders:
        fdir = os.path.join(base_dir, folder_name)
        txt_files = sorted(glob.glob(os.path.join(fdir, "*.txt")))
        print(f"Auditing Year {yr} ({len(txt_files)} monthly files)...")
        
        for fpath in txt_files:
            fname = os.path.basename(fpath)
            month_str = fname.replace("spx_eod_", "").replace(".txt", "")
            t0 = time.time()
            
            # Read all rows of the month
            df_month = pd.read_csv(fpath, low_memory=False)
            df_month_clean, _ = clean_options_chain(df_month)
            
            unique_dates = sorted(df_month_clean['QUOTE_DATE'].dropna().unique().tolist())
            print(f"  Month {month_str}: {len(unique_dates)} dates, {len(df_month_clean)} rows (loaded in {time.time()-t0:.2f}s)")
            
            for date_str in unique_dates:
                df_date = df_month_clean[df_month_clean['QUOTE_DATE'] == date_str]
                underlying_lasts = df_date['UNDERLYING_LAST'].dropna().unique()
                s_val = float(underlying_lasts[0]) if len(underlying_lasts) > 0 else np.nan
                
                # Check all tenors in 20 <= DTE <= 50
                dtes = sorted(df_date['DTE'].dropna().unique().tolist())
                tenors_20_50 = [d for d in dtes if 20.0 <= d <= 50.0]
                
                tenor_audits = []
                valid_tenors_for_interp = []
                
                for dte in tenors_20_50:
                    df_tenor = df_date[df_date['DTE'] == dte]
                    # Use standard r = 0.015 for testing parity inversion
                    r_test = 0.015
                    F_parity, K_star, diag_fwd = invert_synthetic_forward(df_tenor, r=r_test, min_bid=0.05)
                    
                    if F_parity is None:
                        tenor_audits.append({
                            "dte": dte,
                            "fwd_status": "FAILED",
                            "reason": diag_fwd.get("failure_reason")
                        })
                        continue
                        
                    df_otm, diag_otm = screen_otm_quotes(df_tenor, F_parity, min_bid=0.05, max_rel_spread=0.35)
                    num_strikes = len(df_otm)
                    
                    k_min = diag_otm.get("k_min")
                    k_max = diag_otm.get("k_max")
                    
                    # Moneyness span relative to S
                    k_min_ratio_s = (k_min / s_val) if (k_min and s_val and not np.isnan(s_val)) else None
                    k_max_ratio_s = (k_max / s_val) if (k_max and s_val and not np.isnan(s_val)) else None
                    
                    # Breadth criteria: >= 30 liquid strikes and span [0.85, 1.15]
                    has_30_strikes = num_strikes >= 30
                    spans_085_115 = (
                        k_min_ratio_s is not None and k_max_ratio_s is not None and
                        k_min_ratio_s <= 0.85 and k_max_ratio_s >= 1.15
                    )
                    tenor_pass = has_30_strikes and spans_085_115
                    
                    if num_strikes >= 15: # minimum for discrete quadrature
                        valid_tenors_for_interp.append(dte)
                        
                    tenor_audits.append({
                        "dte": dte,
                        "fwd_status": "SUCCESS",
                        "F_parity": F_parity,
                        "num_retained": num_strikes,
                        "retained_puts": diag_otm.get("retained_puts"),
                        "retained_calls": diag_otm.get("retained_calls"),
                        "k_min": k_min,
                        "k_max": k_max,
                        "k_min_ratio_s": k_min_ratio_s,
                        "k_max_ratio_s": k_max_ratio_s,
                        "has_30_strikes": has_30_strikes,
                        "spans_085_115": spans_085_115,
                        "tenor_pass": tenor_pass
                    })
                    
                # Date level summary
                any_tenor_passed = any(t.get("tenor_pass", False) for t in tenor_audits)
                # Check 30d bracketing among valid tenors
                d_low = [d for d in valid_tenors_for_interp if d <= 30.0]
                d_high = [d for d in valid_tenors_for_interp if d >= 30.0]
                can_bracket_30d = len(d_low) > 0 and len(d_high) > 0
                
                daily_results.append({
                    "year": yr,
                    "month": month_str,
                    "date": date_str,
                    "underlying_last": s_val,
                    "total_dtes_20_50": len(tenors_20_50),
                    "tenor_audits": tenor_audits,
                    "any_tenor_passed": any_tenor_passed,
                    "can_bracket_30d": can_bracket_30d,
                    "valid_tenors_count": len(valid_tenors_for_interp)
                })
                
    return daily_results


if __name__ == "__main__":
    results = audit_early_strike_breadth()
    # Save results to output
    os.makedirs("output/stage6_audit", exist_ok=True)
    with open("output/stage6_audit/early_strike_breadth_2010_2012.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Total days audited: {len(results)}")
