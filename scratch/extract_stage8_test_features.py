"""
extract_stage8_test_features.py
===============================
Extracts option-implied features (Q_t in R^5), historical state (X_t in R^6),
and Proposal A physical return targets (y_t = ln(S_{t+2} / S_{t+1})) for the
held-out Test partition (2022-01-03 to 2023-12-29, 501 exchange trading sessions).

Adheres strictly to the frozen Stage 7 specifications:
- Proposal A timing: y_t = ln(S_{t+2} / S_{t+1})
- Causal prior-session forward-fill for isolated option gaps (<= 1 day)
- Explicit logging of rate source and carryforward
- Full disclosure and tracking of test breach exclusion rules
- Only retrieves cash closes through 2024-01-03 to mature 2023 year-end targets;
  no 2024 option data loaded.
"""

import os
import sys
import glob
import time
import json
import math
import hashlib
import numpy as np
import pandas as pd
import yfinance as yf

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

from src.features.options_cleaning import clean_options_chain
from src.features.options_moments import compute_tenor_moments, interpolate_constant_maturity
from src.features.historical_state import compute_historical_features

def convert_irx_to_continuous_rate(d_pct: float, d_bill: float = 91.0) -> float:
    """Converts 13-week T-Bill discount yield (%) to continuous rate."""
    if d_pct is None or np.isnan(d_pct) or d_pct <= 0.0:
        return 0.0001
    price_ratio = 1.0 - (d_pct / 100.0) * (d_bill / 360.0)
    if price_ratio <= 0.0:
        return np.nan
    return float(- (365.0 / d_bill) * math.log(price_ratio))

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest().upper()

def main():
    print("================================================================================")
    print("STAGE 8: TEST FEATURE EXTRACTION & TARGET ALIGNMENT (2022-2023)")
    print("================================================================================")
    
    out_dir = "output/stage8_test"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Load historical closes and fetch 2022-2024 closes strictly through 2024-01-03
    # Note: 2024-01-04 through 2024-01-09 were initially retrieved during earlier data exploration
    # and are now explicitly excluded and truncated. Only 2024-01-02 and 2024-01-03 are retained
    # to mature Proposal A return targets for origins 2023-12-28 and 2023-12-29.
    print("Fetching complete S&P 500 cash closes (^GSPC) through 2024-01-03...")
    gspc_recent = yf.download('^GSPC', start='2021-12-01', end='2024-01-04', progress=False)
    
    # Historical closes through 2021
    df_closes_hist = pd.read_csv("output/stage6_features/spx_daily_closes_2009_2021.csv")
    df_recent_closes = pd.DataFrame({
        'date': gspc_recent.index.strftime('%Y-%m-%d'),
        'close': gspc_recent['Close'].values.flatten()
    }).dropna().sort_values('date').reset_index(drop=True)
    
    # Combine: keep historical <= 2021-12-31, append recent >= 2022-01-01 and <= 2024-01-03
    df_recent_sub = df_recent_closes[(df_recent_closes['date'] > '2021-12-31') & (df_recent_closes['date'] <= '2024-01-03')]
    df_closes_all = pd.concat([df_closes_hist, df_recent_sub], ignore_index=True)
    df_closes_all = df_closes_all.drop_duplicates(subset=['date']).sort_values('date').reset_index(drop=True)
    
    # Save complete close series ending strictly at 2024-01-03
    closes_path = f"{out_dir}/spx_daily_closes_2009_2024.csv"
    df_closes_all.to_csv(closes_path, index=False)
    print(f"Saved complete cash closes ({len(df_closes_all)} sessions) ending at 2024-01-03 to {closes_path}")
    print(f"  First close: {df_closes_all['date'].iloc[0]} ({df_closes_all['close'].iloc[0]:.2f})")
    print(f"  Last close:  {df_closes_all['date'].iloc[-1]} ({df_closes_all['close'].iloc[-1]:.2f})")
    
    # Verify label-maturity closes
    c_2024_01_02 = df_closes_all[df_closes_all['date'] == '2024-01-02']['close'].values[0]
    c_2024_01_03 = df_closes_all[df_closes_all['date'] == '2024-01-03']['close'].values[0]
    print(f"  Label-maturity close 2024-01-02: {c_2024_01_02:.2f}")
    print(f"  Label-maturity close 2024-01-03: {c_2024_01_03:.2f}")
    
    # Map dates to closes and indices
    date_to_close = dict(zip(df_closes_all['date'], df_closes_all['close']))
    close_dates = sorted(df_closes_all['date'].unique())
    date_to_idx = {d: i for i, d in enumerate(close_dates)}
    
    # 2. Fetch ^IRX risk-free rates
    print("Fetching 13-week T-Bill discount yields (^IRX)...")
    irx = yf.download('^IRX', start='2021-12-01', end='2024-01-04', progress=False)
    df_irx = pd.DataFrame({
        'date': irx.index.strftime('%Y-%m-%d'),
        'irx_discount_pct': irx['Close'].values.flatten()
    }).dropna().sort_values('date').reset_index(drop=True)
    df_irx = df_irx[df_irx['date'] <= '2024-01-03']
    df_irx['rf_continuous'] = df_irx['irx_discount_pct'].apply(convert_irx_to_continuous_rate)
    
    irx_cont_map = dict(zip(df_irx['date'], df_irx['rf_continuous']))
    irx_raw_map = dict(zip(df_irx['date'], df_irx['irx_discount_pct']))
    
    # 3. Test Trading Dates (2022-01-01 to 2023-12-31)
    test_dates = sorted([d for d in close_dates if '2022-01-01' <= d <= '2023-12-31'])
    print(f"Total expected Test trading sessions: {len(test_dates)} (2022: {len([d for d in test_dates if d.startswith('2022')])}, 2023: {len([d for d in test_dates if d.startswith('2023')])})")
    
    # 4. Monthly Options Folders
    base_dir = r"Data\SPX Options Chain"
    folders = [
        ('2022q1', 'spx_eod_2022q1-ff0r18'),
        ('2022q2', 'spx_eod_2022q2-bxgzw0'),
        ('2022q3', 'spx_eod_2022q3-1f2afi'),
        ('2022q4', 'spx_eod_2022q4-dmme3k'),
        ('2023q1', 'spx_eod_2023q1-cfph7w'),
        ('2023q2', 'spx_eod_2023q2-kdxt36'),
        ('2023q3', 'spx_eod_2023q3-w9b0jk'),
        ('2023q4', 'spx_eod_2023q4-ai4uc9'),
    ]
    
    # Rate state
    last_known_rate_cont = 0.0005
    last_known_irx_raw = 0.05
    
    # Option features storage by date
    q_features_by_date = {}
    
    print("\nExtracting option moments from monthly bundles...")
    t_start = time.time()
    
    for q_name, folder_name in folders:
        fdir = os.path.join(base_dir, folder_name)
        txt_files = sorted(glob.glob(os.path.join(fdir, "*.txt")))
        
        for fpath in txt_files:
            fname = os.path.basename(fpath)
            t_f0 = time.time()
            df_month_raw = pd.read_csv(fpath, low_memory=False)
            df_month, diag = clean_options_chain(df_month_raw)
            del df_month_raw
            
            file_dates = sorted(df_month['QUOTE_DATE'].dropna().unique().tolist())
            
            for date_str in file_dates:
                if date_str not in test_dates:
                    # Skip market closure/holiday dates recorded in options file
                    continue
                    
                df_date = df_month[df_month['QUOTE_DATE'] == date_str]
                
                # Rate Ingestion with Explicit Fallback Logging
                irx_raw = irx_raw_map.get(date_str, np.nan)
                r_cont = irx_cont_map.get(date_str, np.nan)
                
                if not np.isnan(r_cont):
                    rate_source = "CBOE_IRX_ACTUAL"
                    rate_is_fallback = False
                    rate_fallback_note = "Direct actual close from ^IRX"
                    last_known_rate_cont = r_cont
                    last_known_irx_raw = irx_raw
                else:
                    r_cont = last_known_rate_cont
                    irx_raw = last_known_irx_raw
                    rate_source = "CAUSAL_PRIOR_SESSION_CARRYFORWARD"
                    rate_is_fallback = True
                    rate_fallback_note = "Bond market holiday closure; causally carried forward from prior active trading session"
                    
                observed_ts = df_date['QUOTE_READTIME'].dropna().unique().tolist()
                assert len(observed_ts) == 1, f"Multiple timestamps found for {date_str}: {observed_ts}"
                assert '16:00' in observed_ts[0], f"Non-16:00 timestamp found for {date_str}: {observed_ts[0]}"
                quote_ts = observed_ts[0]
                
                # Tenor evaluations
                all_dtes = sorted(df_date['DTE'].dropna().unique().tolist())
                tenor_results = {}
                for dte in all_dtes:
                    if 15.0 <= dte <= 90.0:
                        df_tenor = df_date[df_date['DTE'] == dte]
                        t_res = compute_tenor_moments(
                            df_tenor,
                            r=r_cont,
                            min_bid=0.05,
                            max_rel_spread=0.35
                        )
                        tenor_results[dte] = t_res
                        
                interp_30, diag_30 = interpolate_constant_maturity(tenor_results, target_dte=30.0)
                interp_60, diag_60 = interpolate_constant_maturity(tenor_results, target_dte=60.0)
                
                svix_30 = interp_30.get("SVIX") if interp_30 else np.nan
                qskew_30 = interp_30.get("QSkew") if interp_30 else np.nan
                qkurt_30 = interp_30.get("QKurt") if interp_30 else np.nan
                atm_30 = interp_30.get("ATM_IV") if interp_30 else np.nan
                atm_60 = interp_60.get("ATM_IV") if interp_60 else np.nan
                slope_60_30 = (atm_60 - atm_30) if (atm_60 is not None and atm_30 is not None and not np.isnan(atm_60) and not np.isnan(atm_30)) else np.nan
                
                has_svix = (svix_30 is not None and not np.isnan(svix_30))
                has_qskew = (qskew_30 is not None and not np.isnan(qskew_30))
                has_qkurt = (qkurt_30 is not None and not np.isnan(qkurt_30))
                has_atm30 = (atm_30 is not None and not np.isnan(atm_30))
                has_slope = (slope_60_30 is not None and not np.isnan(slope_60_30))
                
                valid_q_all5 = bool(has_svix and has_qskew and has_qkurt and has_atm30 and has_slope)
                
                q_features_by_date[date_str] = {
                    'quote_timestamp': quote_ts,
                    'rf_continuous': r_cont,
                    'irx_discount_pct': irx_raw,
                    'rate_source': rate_source,
                    'rate_is_fallback': rate_is_fallback,
                    'rate_fallback_note': rate_fallback_note,
                    'svix_30d': svix_30,
                    'qskew_30d': qskew_30,
                    'qkurt_30d': qkurt_30,
                    'atm_iv_30d': atm_30,
                    'atm_iv_60d': atm_60,
                    'term_slope_60_30': slope_60_30,
                    'valid_Q_all5': valid_q_all5,
                    'q_source': "CBOE_OPTIONSDX_ACTUAL",
                    'q_is_fallback': False,
                    'q_fallback_note': "Direct options chain calculation"
                }
                
            elapsed = time.time() - t_f0
            print(f"  Processed {fname:18s} ({len(file_dates):2d} dates) in {elapsed:.1f}s")
            
    print(f"\nCompleted raw options extraction in {time.time() - t_start:.1f}s")
    print(f"Extracted option moments for {len(q_features_by_date)} of {len(test_dates)} expected trading sessions")
    
    # 5. Build Final Dataset across all 501 test sessions (with gap forward-fill)
    print("\nAligning all 501 test trading sessions, historical features, and Proposal A targets...")
    test_records = []
    prev_q_dict = None
    
    # Also load the last session of 2021 to support forward fill if 2022-01-03 were missing
    # (though 2022-01-03 is present)
    missing_dates = []
    
    for date_str in test_dates:
        # Check option features
        if date_str in q_features_by_date:
            q_info = q_features_by_date[date_str]
            prev_q_dict = q_info.copy()
        else:
            missing_dates.append(date_str)
            # Apply protocol's isolated gap forward-fill: Q_t <- Q_{t-1}
            assert prev_q_dict is not None, f"Cannot forward fill Q for first date {date_str}"
            q_info = prev_q_dict.copy()
            q_info['q_source'] = "CAUSAL_PRIOR_SESSION_FORWARD_FILL"
            q_info['q_is_fallback'] = True
            q_info['q_fallback_note'] = f"Missing in OptionsDX; causally forward-filled from prior active session"
            print(f"  [GAP LOG] Date {date_str}: Missing option file. Causally forward-filled Q from prior session.")
            
        # Historical features X_t (trailing up to date_str)
        hist_feats, _ = compute_historical_features(df_closes_all, date_str, window=20)
        
        # Proposal A Target: y_t = ln(S_{t+2} / S_{t+1})
        c_idx = date_to_idx[date_str]
        d_next1 = close_dates[c_idx + 1]
        d_next2 = close_dates[c_idx + 2]
        s_curr = date_to_close[date_str]
        s_next1 = date_to_close[d_next1]
        s_next2 = date_to_close[d_next2]
        target_y = math.log(s_next2 / s_next1)
        
        # Target status
        target_status = "VALID_MATURED_TARGET"
        target_is_valid = True
        
        # Map Test Breach Exclusions:
        # Rule 1: The Jan 3 to Jan 4 return is ln(S_2022-01-04 / S_2022-01-03).
        # Under Proposal A, that return belongs to origin 2021-12-31 (in validation dataset).
        # Rule 2: Origin 2022-01-03 has features observed at date 2022-01-03 and target ln(S_2022-01-05 / S_2022-01-04).
        # Because S_2022-01-03 and S_2022-01-04 were accessed in commit cee01a1, origin 2022-01-03 is flagged
        # so it can be evaluated both included and excluded.
        is_breach_origin = bool(date_str == '2022-01-03')
        breach_note = "TEST_BREACH_ORIGIN_2022_01_03 (features used accessed Jan 3 close; target used accessed Jan 4 close)" if is_breach_origin else "UNBREACHED_TEST_ORIGIN"
        
        # Supervised usability mask: valid complete Q (all 5), valid target, non-null historical
        valid_sup = bool(q_info['valid_Q_all5'] and not np.isnan(target_y) and not np.isnan(hist_feats['rv_20d']))
        
        rec = {
            'date': date_str,
            'S_t': s_curr,
            'd_next1': d_next1,
            'S_t1': s_next1,
            'd_next2': d_next2,
            'S_t2': s_next2,
            'target_y_next2': target_y,
            'target_status': target_status,
            'target_is_valid': target_is_valid,
            'breach_exclusion_flag': is_breach_origin,
            'breach_note': breach_note,
            # Q_t features
            'SVIX_30d': q_info['svix_30d'],
            'QSkew_30d': q_info['qskew_30d'],
            'QKurt_30d': q_info['qkurt_30d'],
            'ATM_IV_30d': q_info['atm_iv_30d'],
            'ATM_IV_60d': q_info['atm_iv_60d'],
            'TermSlope_60_30': q_info['term_slope_60_30'],
            'valid_Q_all5': q_info['valid_Q_all5'],
            'q_source': q_info['q_source'],
            'q_is_fallback': q_info['q_is_fallback'],
            'q_fallback_note': q_info['q_fallback_note'],
            'quote_timestamp': q_info['quote_timestamp'],
            'rf_continuous': q_info['rf_continuous'],
            'irx_discount_pct': q_info['irx_discount_pct'],
            'rate_source': q_info['rate_source'],
            'rate_is_fallback': q_info['rate_is_fallback'],
            'rate_fallback_note': q_info['rate_fallback_note'],
            # X_t features
            'r_1d': hist_feats['r_1d'],
            'r_5d': hist_feats['r_5d'],
            'rv_5d': hist_feats['rv_5d'],
            'rv_20d': hist_feats['rv_20d'],
            'dsemi_20d': hist_feats['dsemi_20d'],
            'dd_20d': hist_feats['dd_20d'],
            # Usable supervised pair mask
            'valid_supervised_pair_all5': valid_sup
        }
        test_records.append(rec)
        
    df_test = pd.DataFrame(test_records)
    test_csv_path = f"{out_dir}/spx_features_test_2022_2023.csv"
    df_test.to_csv(test_csv_path, index=False)
    csv_hash = compute_sha256(test_csv_path)
    
    print(f"\nSaved Test feature dataset to {test_csv_path}")
    print(f"  Rows: {len(df_test)}")
    print(f"  SHA-256: {csv_hash}")
    print(f"  Feature-complete rows (valid_Q_all5): {df_test['valid_Q_all5'].sum()}")
    print(f"  Usable supervised pairs: {df_test['valid_supervised_pair_all5'].sum()}")
    print(f"  Forward-filled Q sessions: {df_test['q_is_fallback'].sum()} ({missing_dates})")
    print(f"  Breach-flagged origin sessions: {df_test['breach_exclusion_flag'].sum()} (2022-01-03)")
    
    # Save metadata
    metadata = {
        'dataset_name': 'spx_features_test_2022_2023',
        'file_path': test_csv_path,
        'sha256_checksum': csv_hash,
        'n_total_sessions': len(df_test),
        'start_date': str(df_test['date'].iloc[0]),
        'end_date': str(df_test['date'].iloc[-1]),
        'n_feature_complete_all5': int(df_test['valid_Q_all5'].sum()),
        'n_usable_supervised_pairs': int(df_test['valid_supervised_pair_all5'].sum()),
        'n_forward_filled_q_sessions': int(df_test['q_is_fallback'].sum()),
        'forward_filled_q_dates': missing_dates,
        'n_breach_flagged_origins': int(df_test['breach_exclusion_flag'].sum()),
        'breach_flagged_dates': ['2022-01-03'],
        'label_definition': 'Proposal A: y_t = ln(S_{t+2} / S_{t+1})',
        'label_maturity_closes': {
            '2024-01-02': float(c_2024_01_02),
            '2024-01-03': float(c_2024_01_03)
        },
        'data_access_scope_disclosure': (
            'Cash closes (^GSPC) and risk-free rates (^IRX) were retrieved through 2024-01-03 strictly to mature '
            'Proposal A return targets for the final test origins (2023-12-28 and 2023-12-29). Additional closes '
            'for 2024-01-04 through 2024-01-09 were initially fetched during data exploration and have been explicitly '
            'truncated. spx_daily_closes_2009_2024.csv ends strictly at 2024-01-03. Zero 2024 forecast origins exist, '
            'zero 2024 option files were accessed, and no post-maturity closes enter any feature or label.'
        ),
        'test_partition_status_disclosure': (
            'The held-out test partition is historically compromised: S&P 500 cash closes for 2022-01-03 (4796.56) '
            'and 2022-01-04 (4793.54), and the derived return ln(4793.54/4796.56) = -0.000630, were accessed '
            'and committed in Git history commit cee01a1. The raw 2022-2023 monthly option bundles were processed '
            'for the first time during Gate D. Origin 2022-01-03 is explicitly flagged and evaluated both included '
            'and excluded to ensure transparent reporting.'
        )
    }
    
    with open(f"{out_dir}/test_dataset_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved test dataset metadata to {out_dir}/test_dataset_metadata.json")
    
    print("\n================================================================================")
    print("STAGE 8 TEST FEATURE EXTRACTION COMPLETE!")
    print("================================================================================")

if __name__ == "__main__":
    main()
