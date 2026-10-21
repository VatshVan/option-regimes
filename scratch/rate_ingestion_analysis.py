"""
rate_ingestion_analysis.py
==========================
Documents and evaluates reproducible point-in-time risk-free rate sources
for SPX option feature construction (Martin SVIX, BKM moments, Black-76 ATM IV).

Compares:
1. Cboe / Yahoo Finance ^IRX (13-Week Treasury Bill Discount Yield)
2. FRED Continuous CMT Rates (1M, 3M, 6M, 1Y)
3. Mathematical conversions from Bank Discount Yield to Continuously Compounded Zero Rate:
   - Bank discount price: P = 100 * (1 - d/100 * D_bill / 360)
   - Bond equivalent yield: y_BEY = (100 - P)/P * (365 / D_bill)
   - Continuously compounded rate: r_cont = - (365 / D_bill) * ln(1 - d/100 * D_bill / 360)
"""

import math
import pandas as pd
import numpy as np


def convert_discount_to_continuous(d_pct: float, d_bill: float = 91.0) -> dict:
    """
    Converts annualized bank discount yield d_pct (e.g. 1.508 for 1.508%)
    on a D_bill-day Treasury paper (actual/360) to:
    1. Purchase price P per $100 face value
    2. Bond Equivalent Yield (BEY, actual/365 simple yield)
    3. Continuously compounded annualized zero rate r_cont (actual/365)
    """
    d = d_pct / 100.0
    price = 100.0 * (1.0 - d * (d_bill / 360.0))
    if price <= 0:
        return {"error": "Invalid price <= 0"}
        
    bey = ((100.0 - price) / price) * (365.0 / d_bill)
    r_cont = - (365.0 / d_bill) * math.log(price / 100.0)
    
    wedge_bp = (r_cont - d) * 10000.0
    
    return {
        "quoted_discount_pct": d_pct,
        "discount_decimal": d,
        "bill_tenor_days": d_bill,
        "bill_price": price,
        "bond_equivalent_yield": bey,
        "continuously_compounded_rate": r_cont,
        "wedge_vs_discount_bps": wedge_bp
    }


if __name__ == "__main__":
    # Demonstration rates from Stage 4
    calm_res = convert_discount_to_continuous(1.508, 91.0)
    stress_res = convert_discount_to_continuous(0.918, 91.0)
    
    print("--- 2020-01-15 (Calm): Quoted IRX = 1.508% ---")
    for k, v in calm_res.items():
        print(f"  {k}: {v}")
        
    print("\n--- 2020-03-03 (Stress): Quoted IRX = 0.918% ---")
    for k, v in stress_res.items():
        print(f"  {k}: {v}")
