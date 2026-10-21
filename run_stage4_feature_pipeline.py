"""
run_stage4_feature_pipeline.py
==============================
Bounded execution runner for the Stage 4 Feature Construction Pipeline.
Processes the two authorized Stage 3 demonstration dates (2020-01-15 and 2020-03-03),
executes focused numerical and boundary edge-case tests, and writes outputs to
output/stage4_features/.
"""

import os
import json
import datetime
import numpy as np
import pandas as pd

from src.features.pipeline import FeaturePipeline
from src.features.historical_state import fetch_historical_spx_closes
from src.features.options_cleaning import invert_synthetic_forward, screen_otm_quotes
from src.features.options_moments import invert_black76_iv, compute_martin_svix, compute_bkm_moments


def run_edge_case_tests():
    """Runs focused unit checks for numerical edge cases and leakage boundaries."""
    print("=" * 60)
    print("RUNNING STAGE 4 FOCUSED EDGE-CASE & UNIT CHECKS")
    print("=" * 60)
    
    # Test 1: Sparse strike grid (< 15 strikes)
    strikes_sparse = np.array([3000.0, 3100.0, 3200.0])
    prices_sparse = np.array([20.0, 10.0, 5.0])
    svix, svix_sq, diag_svix = compute_martin_svix(strikes_sparse, prices_sparse, 3100.0, 0.01, 30/365)
    assert svix is None, "Sparse grid should fail SVIX check"
    print(" [PASS] Test 1: Sparse strike grid rejected (< 15 strikes).")
    
    # Test 2: Inverted/Crossed quotes and subpenny bid rejection
    dummy_tenor = pd.DataFrame([
        {"STRIKE": 3000.0, "DTE": 30.0, "P_BID": 0.00, "P_ASK": 1.00, "C_BID": 1.00, "C_ASK": 1.50},  # Zero bid
        {"STRIKE": 3100.0, "DTE": 30.0, "P_BID": 5.00, "P_ASK": 4.00, "C_BID": 1.00, "C_ASK": 1.50},  # Crossed put
        {"STRIKE": 3200.0, "DTE": 30.0, "P_BID": 1.00, "P_ASK": 3.00, "C_BID": 2.00, "C_ASK": 1.00},  # Crossed call
        {"STRIKE": 3300.0, "DTE": 30.0, "P_BID": 1.00, "P_ASK": 1.10, "C_BID": 1.00, "C_ASK": 3.00}, # Wide spread on Call (100% > 35%)
    ])
    df_otm, diag_screen = screen_otm_quotes(dummy_tenor, F_parity=3150.0, min_bid=0.05, max_rel_spread=0.35)
    assert len(df_otm) == 0, f"All invalid quotes should be rejected, got {len(df_otm)}"
    print(" [PASS] Test 2: Zero-bid, crossed, and wide-spread quotes cleanly rejected.")
    
    # Test 3: Black-76 IV Inversion at Intrinsic Boundary
    # Call price exactly at or below intrinsic should return None, not crash or produce negative vol
    iv_below_intrinsic = invert_black76_iv(price=9.0, F=3100.0, K=3000.0, r=0.01, T=0.1, is_call=True)
    assert iv_below_intrinsic is None, "Call price below intrinsic must return None"
    print(" [PASS] Test 3: Black-76 IV inversion handles intrinsic boundary correctly.")
    
    # Test 4: Strictly Trailing Window Leakage Guard
    # Ensure that close series indexing only takes s <= t
    test_dates = pd.date_range("2020-01-01", periods=30, freq="B").strftime("%Y-%m-%d").tolist()
    dummy_closes = pd.DataFrame({"date": test_dates, "close": np.linspace(3000, 3100, 30)})
    from src.features.historical_state import compute_historical_features
    feats, diag_h = compute_historical_features(dummy_closes, target_date=test_dates[25], window=20)
    assert diag_h["available_history_end"] == test_dates[25], "Historical window must terminate at target date"
    assert test_dates[26] not in diag_h.values(), "No forward dates allowed in historical feature computation"
    print(" [PASS] Test 4: Historical feature lookback strictly point-in-time (no future leakage).")
    print("=" * 60)
    print("ALL 4 UNIT TESTS PASSED SUCCESSFULLY.\n")


def main():
    print("Starting Stage 4 Feature Pipeline Runner...")
    
    # Execute focused edge case checks first
    run_edge_case_tests()
    
    # Ensure output directory exists
    out_dir = "output/stage4_features"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Fetch / load SPX cash closes
    closes_cache = os.path.join(out_dir, "spx_daily_closes.csv")
    print(f"Fetching / loading daily SPX cash close series (cache: {closes_cache})...")
    df_closes = fetch_historical_spx_closes(cache_path=closes_cache, start_date="2019-11-01", end_date="2020-03-15")
    print(f"Loaded {len(df_closes)} trading sessions spanning {df_closes['date'].min()} to {df_closes['date'].max()}.\n")
    
    # 2. Define demonstration target dates with explicit provenance tracking
    target_specs = [
        {
            "date": "2020-01-15",
            "regime": "Calm / Low Volatility (Official VIX <= 20)",
            "file": "Data/SPX Options Chain/spx_eod_2020-wh6jt7/spx_eod_202001.txt",
            "r": 0.01508,
            "r_source": "Illustrative benchmark rate based on Cboe 13-week T-Bill (^IRX) close",
            "r_status": "Illustrative/unverified benchmark input (dynamic yield curve ingestion deferred)",
            "expected_cash_close": 3289.29,
            "cash_close_source": "Yahoo Finance ^GSPC daily close cache",
            "official_vix": 12.42
        },
        {
            "date": "2020-03-03",
            "regime": "Crisis / High Volatility Stress (Official VIX > 30)",
            "file": "Data/SPX Options Chain/spx_eod_2020-wh6jt7/spx_eod_202003.txt",
            "r": 0.00918,
            "r_source": "Illustrative benchmark rate based on Cboe 13-week T-Bill (^IRX) close",
            "r_status": "Illustrative/unverified benchmark input (dynamic yield curve ingestion deferred)",
            "expected_cash_close": 3003.37,
            "cash_close_source": "Yahoo Finance ^GSPC daily close cache",
            "official_vix": 36.82
        }
    ]
    
    pipeline = FeaturePipeline(
        min_bid=0.05,
        max_rel_spread=0.35,
        target_dte_primary=30.0,
        target_dte_secondary=60.0
    )
    
    all_features = []
    all_diagnostics = {}
    provenance_metadata = {
        "metadata_version": "1.1",
        "generated_at": datetime.datetime.now().isoformat(),
        "notes": "Stage 4 demonstration inputs and provenance record. Preserves two-date scope.",
        "cash_close_series": {
            "source": "Yahoo Finance API chart endpoint",
            "symbol": "^GSPC",
            "field": "close",
            "units": "Index points",
            "cache_file": closes_cache,
            "span_start": "2019-10-31",
            "span_end": "2020-03-13",
            "status": "Illustrative market close aggregator series matching Cboe closing levels"
        },
        "target_dates": {}
    }
    
    for spec in target_specs:
        dt = spec["date"]
        print("=" * 70)
        print(f"PROCESSING TARGET DATE: {dt} ({spec['regime']})")
        print("=" * 70)
        
        feats, diag = pipeline.process_date(
            date_str=dt,
            options_filepath=spec["file"],
            risk_free_rate=spec["r"],
            df_closes=df_closes,
            cash_close_expected=spec["expected_cash_close"]
        )
        
        feats["regime_label"] = spec["regime"]
        feats["official_vix_close"] = spec["official_vix"]
        feats["risk_free_rate_status"] = spec["r_status"]
        
        # Inject provenance into diagnostics
        diag["input_provenance"] = {
            "cash_close": {
                "source": spec["cash_close_source"],
                "value": feats.get("S_t"),
                "expected": spec["expected_cash_close"],
                "diff": feats.get("cash_close_diff", 0.0),
                "units": "Index points"
            },
            "risk_free_rate": {
                "source": spec["r_source"],
                "value": spec["r"],
                "units": "Annualized decimal",
                "convention": "Continuously compounded (Act/365)",
                "status": spec["r_status"]
            },
            "options_chain": {
                "file": spec["file"],
                "quote_readtime": diag.get("quote_readtime"),
                "timestamp_note": "Parity ensures internal surface consistency but does not prove quote/cash synchronization or eliminate 16:00/16:15 ET look-ahead risk"
            }
        }
        
        all_features.append(feats)
        all_diagnostics[dt] = diag
        provenance_metadata["target_dates"][dt] = diag["input_provenance"]
        
        print(f"Status: {diag['status']}")
        print(f"Quote Readtime: {diag.get('quote_readtime')}")
        print(f"Cash Close S_t: {feats.get('S_t'):.2f} (Expected: {spec['expected_cash_close']:.2f}, Diff: {feats.get('cash_close_diff', 0):+.2f})")
        print(f"Risk-Free Rate: {spec['r']*100:.3f}% ({spec['r_status']})")
        print("\n--- Option-Implied Features (Q_t, Finite-Grid Estimates without Tail Extrapolation) ---")
        print(f"  Martin SVIX (30d)               : {feats.get('SVIX_30d', np.nan)*100:6.2f}% (Variance: {feats.get('SVIX_30d', 0)**2:.6f})")
        print(f"  BKM Risk-Neutral Skewness       : {feats.get('QSkew_30d', np.nan):6.4f} (Centered, Standardized)")
        print(f"  BKM Risk-Neutral Kurtosis       : {feats.get('QKurt_30d', np.nan):6.4f} (Centered, Standardized, Non-Excess; Normal = 3.0)")
        print(f"  ATM Implied Vol (30d)           : {feats.get('ATM_IV_30d', np.nan)*100:6.2f}% (Black-76 Inverted)")
        print(f"  ATM Implied Vol (60d)           : {feats.get('ATM_IV_60d', np.nan)*100:6.2f}% (Black-76 Inverted)")
        print(f"  Term Structure Slope (60d - 30d): {feats.get('TermSlope_60_30', np.nan)*100:+6.2f}%")
        
        print("\n--- Historical State Features (X_t, Trailing 20 Days, s <= t Point-in-Time) ---")
        print(f"  1-Day Return (r_1d)             : {feats.get('r_1d', np.nan)*100:+6.2f}%")
        print(f"  5-Day Return (r_5d)             : {feats.get('r_5d', np.nan)*100:+6.2f}%")
        print(f"  5-Day Realized Vol (RV5)        : {feats.get('rv_5d', np.nan)*100:6.2f}%")
        print(f"  20-Day Realized Vol (RV20)      : {feats.get('rv_20d', np.nan)*100:6.2f}%")
        print(f"  Downside Semivariance           : {feats.get('dsemi_20d', np.nan)*100:6.2f}%")
        print(f"  Trailing 20-Day Drawdown        : {feats.get('dd_20d', np.nan)*100:+6.2f}%")
        print()
        
    # Save outputs to output/stage4_features/
    df_out = pd.DataFrame(all_features)
    out_csv = os.path.join(out_dir, "spx_features_stage4_demonstration.csv")
    df_out.to_csv(out_csv, index=False)
    print(f"Saved feature dataset to: {out_csv}")
    
    out_json = os.path.join(out_dir, "spx_features_stage4_diagnostics.json")
    # Custom serializer for numpy types
    def default_serializer(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)
        
    with open(out_json, "w") as f:
        json.dump(all_diagnostics, f, indent=2, default=default_serializer)
    print(f"Saved diagnostics log to: {out_json}")
    
    out_prov = os.path.join(out_dir, "input_provenance_metadata.json")
    with open(out_prov, "w") as f:
        json.dump(provenance_metadata, f, indent=2, default=default_serializer)
    print(f"Saved input provenance metadata to: {out_prov}")
    
    print("\nSTAGE 4 DEMONSTRATION RUN COMPLETE.")


if __name__ == "__main__":
    main()
