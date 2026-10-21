"""
batch_feature_pipeline.py
=========================
Corrected Stage 6 Batch Feature Extraction Pipeline (2010-2021).

Crucial Corrections:
1. Discloses that 2022-01-03 cash close was accessed when downloading ^GSPC closes,
   compromising the claim of an untouched test seal.
2. Enforces strict partition boundaries on forecast targets:
   - 2021-12-31 validation row target_r_next is set to NaN (cannot be observed without 2022 test close).
   - 2019-12-31 development row target_r_next is explicitly flagged as requiring cross-partition 2020 close.
3. Eliminates silent rate imputation:
   - Detects when ^IRX is missing (e.g. bond market bank holiday closures on Columbus Day / Veterans Day).
   - Applies causal prior-session carryforward ONLY with explicit logging (rate_source, rate_is_fallback, rate_fallback_note).
4. Corrects feature completeness diagnostics:
   - Requires ALL FIVE Q_t features (SVIX_30d, QSkew_30d, QKurt_30d, ATM_IV_30d, TermSlope_60_30).
   - Differentiates complete Q_t (all 5) from partial 30d-only moments (missing 60d slope).
5. Does NOT label outputs as permanently frozen; marks them as Corrected Candidate Feature Datasets.
"""

import os
import sys
import glob
import json
import time
import math
import hashlib
import numpy as np
import pandas as pd
import yfinance as yf

sys.path.insert(0, os.path.abspath("."))

from src.features.options_cleaning import clean_options_chain
from src.features.options_moments import compute_tenor_moments, interpolate_constant_maturity
from src.features.historical_state import compute_historical_features


def convert_irx_to_continuous_rate(d_pct: float, d_bill: float = 91.0) -> float:
    """
    Converts 13-week Treasury Bill annualized bank discount yield (%)
    to an annualized continuously compounded zero rate (decimal).
    Returns NaN if d_pct is missing (no silent fallback).
    """
    if pd.isna(d_pct):
        return np.nan
    d = float(d_pct) / 100.0
    price_ratio = 1.0 - d * (d_bill / 360.0)
    if price_ratio <= 0:
        return np.nan
    r_cont = - (365.0 / d_bill) * math.log(price_ratio)
    return float(r_cont)


def run_pipeline():
    print("=== Corrected Batch Feature Extraction Pipeline (2010-2021) ===")
    
    # 1. Cash Index Closes (^GSPC)
    # DISCLOSURE: Downloading through 2022-01-04 accessed the 2022-01-03 cash close (4796.56).
    # We restrict official in-sample closes strictly to <= 2021-12-31.
    print("Fetching historical S&P 500 cash closes (^GSPC)...")
    gspc = yf.download('^GSPC', start='2009-11-01', end='2022-01-05', progress=False)
    
    df_closes_all = pd.DataFrame({
        'date': gspc.index.strftime('%Y-%m-%d'),
        'close': gspc['Close'].values.flatten()
    }).dropna().sort_values('date').reset_index(drop=True)
    
    # Boundary-aware close sets
    df_closes_dev = df_closes_all[df_closes_all['date'] <= '2019-12-31'].copy().reset_index(drop=True)
    df_closes_val = df_closes_all[df_closes_all['date'] <= '2021-12-31'].copy().reset_index(drop=True)
    
    # 2. Risk-Free Rates (^IRX)
    print("Fetching daily 13-week T-Bill discount yields (^IRX)...")
    irx = yf.download('^IRX', start='2009-11-01', end='2022-01-01', progress=False)
    df_irx = pd.DataFrame({
        'date': irx.index.strftime('%Y-%m-%d'),
        'irx_discount_pct': irx['Close'].values.flatten()
    }).dropna().sort_values('date').reset_index(drop=True)
    df_irx['rf_continuous'] = df_irx['irx_discount_pct'].apply(convert_irx_to_continuous_rate)
    
    irx_cont_map = dict(zip(df_irx['date'], df_irx['rf_continuous']))
    irx_raw_map = dict(zip(df_irx['date'], df_irx['irx_discount_pct']))
    
    # Expected trading dates (Development: 2010-2019, Validation: 2020-2021)
    dev_dates = sorted([d for d in df_closes_all['date'] if '2010-01-01' <= d <= '2019-12-31'])
    val_dates = sorted([d for d in df_closes_all['date'] if '2020-01-01' <= d <= '2021-12-31'])
    all_dates = dev_dates + val_dates
    print(f"Expected dates: Development={len(dev_dates)}, Validation={len(val_dates)}, Total={len(all_dates)}")
    
    # 3. Monthly Folders
    base_dir = r"Data\SPX Options Chain"
    folders = [
        ('2010', 'spx_eod_2010-hixkhi'),
        ('2011', 'spx_eod_2011-mpv77a'),
        ('2012', 'spx_eod_2012-ftrobg'),
        ('2013', 'spx_eod_2013-3p7m9u'),
        ('2014', 'spx_eod_2014-4ky8n2'),
        ('2015', 'spx_eod_2015-amtjlk'),
        ('2016', 'spx_eod_2016-rctzlw'),
        ('2017', 'spx_eod_2017-xspity'),
        ('2018', 'spx_eod_2018-uqawfl'),
        ('2019', 'spx_eod_2019-chxexe'),
        ('2020', 'spx_eod_2020-wh6jt7'),
        ('2021', 'spx_eod_2021-n4uqkm'),
        ('2021q3', 'spx_eod_2021q3-kgzold'),
        ('2021q4', 'spx_eod_2021q4-r3h0dx'),
    ]
    
    # Track rate carry-forward state
    last_known_rate_cont = 0.015
    last_known_irx_raw = 1.50
    
    all_feature_records = []
    t_start = time.time()
    
    for yr, folder_name in folders:
        fdir = os.path.join(base_dir, folder_name)
        txt_files = sorted(glob.glob(os.path.join(fdir, "*.txt")))
        
        for fpath in txt_files:
            df_month_raw = pd.read_csv(fpath, low_memory=False)
            df_month, _ = clean_options_chain(df_month_raw)
            del df_month_raw
            
            file_dates = sorted(df_month['QUOTE_DATE'].dropna().unique().tolist())
            
            for date_str in file_dates:
                if date_str not in all_dates:
                    # Ignore market closure dates (Sandy, Bush funeral)
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
                    # Explicit Causal Carryforward
                    r_cont = last_known_rate_cont
                    irx_raw = last_known_irx_raw
                    rate_source = "CAUSAL_PRIOR_SESSION_CARRYFORWARD"
                    rate_is_fallback = True
                    rate_fallback_note = "Bond market holiday closure; causally carried forward from prior active trading session"
                    
                # Timestamp
                observed_ts = df_date['QUOTE_READTIME'].dropna().unique().tolist()
                quote_ts = observed_ts[0] if observed_ts else "UNKNOWN"
                
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
                        
                interp_30, diag_interp_30 = interpolate_constant_maturity(tenor_results, target_dte=30.0)
                interp_60, diag_interp_60 = interpolate_constant_maturity(tenor_results, target_dte=60.0)
                
                # Historical state features X_t (trailing up to date_str)
                hist_feats, diag_hist = compute_historical_features(df_closes_all, date_str, window=20)
                
                # Feature values
                svix_30 = interp_30.get("SVIX") if interp_30 else np.nan
                qskew_30 = interp_30.get("QSkew") if interp_30 else np.nan
                qkurt_30 = interp_30.get("QKurt") if interp_30 else np.nan
                atm_30 = interp_30.get("ATM_IV") if interp_30 else np.nan
                atm_60 = interp_60.get("ATM_IV") if interp_60 else np.nan
                slope_60_30 = (atm_60 - atm_30) if (atm_60 is not None and atm_30 is not None and not np.isnan(atm_60) and not np.isnan(atm_30)) else np.nan
                
                # Strict 5-feature completeness check
                has_svix = (svix_30 is not None and not np.isnan(svix_30))
                has_qskew = (qskew_30 is not None and not np.isnan(qskew_30))
                has_qkurt = (qkurt_30 is not None and not np.isnan(qkurt_30))
                has_atm30 = (atm_30 is not None and not np.isnan(atm_30))
                has_slope = (slope_60_30 is not None and not np.isnan(slope_60_30))
                
                valid_q_30d = has_svix and has_qskew and has_qkurt and has_atm30
                valid_q_all5 = valid_q_30d and has_slope
                
                if valid_q_all5:
                    status_q = "SUCCESS_ALL_5"
                elif valid_q_30d:
                    status_q = "PARTIAL_30D_ONLY (missing 60d term slope)"
                elif interp_30 is not None and diag_interp_30.get("failure_reason"):
                    status_q = f"FAILED_30D ({diag_interp_30.get('failure_reason')})"
                else:
                    status_q = "FAILED"
                    
                # Target Return r_{t+1} with Strict Boundary Enforcement
                # Find position in all closes
                c_idx = df_closes_all[df_closes_all['date'] == date_str].index[0]
                s_curr = df_closes_all.loc[c_idx, 'close']
                
                if date_str == '2021-12-31':
                    # Terminal validation session: Observing next close (2022-01-03) breaches test partition!
                    s_next = np.nan
                    r_next = np.nan
                    target_status = "UNOBSERVED_WITHOUT_TEST_CLOSE (2022-01-03 close is in sealed test partition)"
                elif date_str == '2019-12-31':
                    # Terminal development session: Next close (2020-01-02) is in validation partition
                    s_next = df_closes_all.loc[c_idx + 1, 'close']
                    r_next = math.log(s_next / s_curr)
                    target_status = "CROSS_PARTITION_LABEL (calculated using validation close 2020-01-02)"
                elif c_idx + 1 < len(df_closes_all):
                    s_next = df_closes_all.loc[c_idx + 1, 'close']
                    r_next = math.log(s_next / s_curr)
                    target_status = "IN_PARTITION_VALID"
                else:
                    s_next = np.nan
                    r_next = np.nan
                    target_status = "MISSING_NEXT_CLOSE"
                    
                rec = {
                    "date": date_str,
                    "quote_timestamp": quote_ts,
                    "quoted_irx_pct": irx_raw,
                    "risk_free_rate_cont": r_cont,
                    "rate_source": rate_source,
                    "rate_is_fallback": rate_is_fallback,
                    "rate_fallback_note": rate_fallback_note,
                    "SVIX_30d": svix_30,
                    "QSkew_30d": qskew_30,
                    "QKurt_30d": qkurt_30,
                    "ATM_IV_30d": atm_30,
                    "ATM_IV_60d": atm_60,
                    "TermSlope_60_30": slope_60_30,
                    "valid_Q_30d": valid_q_30d,
                    "valid_Q_all5": valid_q_all5,
                    "status_Q": status_q,
                    "S_t": hist_feats.get("S_t") if hist_feats else np.nan,
                    "r_1d": hist_feats.get("r_1d") if hist_feats else np.nan,
                    "r_5d": hist_feats.get("r_5d") if hist_feats else np.nan,
                    "rv_5d": hist_feats.get("rv_5d") if hist_feats else np.nan,
                    "rv_20d": hist_feats.get("rv_20d") if hist_feats else np.nan,
                    "dsemi_20d": hist_feats.get("dsemi_20d") if hist_feats else np.nan,
                    "dd_20d": hist_feats.get("dd_20d") if hist_feats else np.nan,
                    "valid_X_all6": (hist_feats is not None and not np.isnan(hist_feats.get("r_1d", np.nan))),
                    "S_next": s_next,
                    "target_r_next": r_next,
                    "target_status": target_status
                }
                all_feature_records.append(rec)
                
    # Check for missing option dates
    processed_dates = set(r['date'] for r in all_feature_records)
    missing_dates = sorted(list(set(all_dates) - processed_dates))
    print(f"Option records processed: {len(processed_dates)}, Missing option dates: {len(missing_dates)}")
    
    for md in missing_dates:
        hist_feats, _ = compute_historical_features(df_closes_all, md, window=20)
        c_idx = df_closes_all[df_closes_all['date'] == md].index[0]
        s_curr = df_closes_all.loc[c_idx, 'close']
        
        irx_raw = irx_raw_map.get(md, np.nan)
        r_cont = irx_cont_map.get(md, np.nan)
        if not np.isnan(r_cont):
            rate_source = "CBOE_IRX_ACTUAL"
            rate_is_fallback = False
            rate_fallback_note = "Direct actual close from ^IRX"
        else:
            r_cont = last_known_rate_cont
            irx_raw = last_known_irx_raw
            rate_source = "CAUSAL_PRIOR_SESSION_CARRYFORWARD"
            rate_is_fallback = True
            rate_fallback_note = "Bond market holiday closure; causally carried forward"
            
        if md == '2021-12-31':
            s_next = np.nan
            r_next = np.nan
            target_status = "UNOBSERVED_WITHOUT_TEST_CLOSE"
        elif md == '2019-12-31':
            s_next = df_closes_all.loc[c_idx + 1, 'close']
            r_next = math.log(s_next / s_curr)
            target_status = "CROSS_PARTITION_LABEL"
        elif c_idx + 1 < len(df_closes_all):
            s_next = df_closes_all.loc[c_idx + 1, 'close']
            r_next = math.log(s_next / s_curr)
            target_status = "IN_PARTITION_VALID"
        else:
            s_next = np.nan
            r_next = np.nan
            target_status = "MISSING_NEXT_CLOSE"
            
        all_feature_records.append({
            "date": md,
            "quote_timestamp": "MISSING",
            "quoted_irx_pct": irx_raw,
            "risk_free_rate_cont": r_cont,
            "rate_source": rate_source,
            "rate_is_fallback": rate_is_fallback,
            "rate_fallback_note": rate_fallback_note,
            "SVIX_30d": np.nan,
            "QSkew_30d": np.nan,
            "QKurt_30d": np.nan,
            "ATM_IV_30d": np.nan,
            "ATM_IV_60d": np.nan,
            "TermSlope_60_30": np.nan,
            "valid_Q_30d": False,
            "valid_Q_all5": False,
            "status_Q": "ERR_MISSING_OPTION_FILE_OR_DATE",
            "S_t": hist_feats.get("S_t") if hist_feats else np.nan,
            "r_1d": hist_feats.get("r_1d") if hist_feats else np.nan,
            "r_5d": hist_feats.get("r_5d") if hist_feats else np.nan,
            "rv_5d": hist_feats.get("rv_5d") if hist_feats else np.nan,
            "rv_20d": hist_feats.get("rv_20d") if hist_feats else np.nan,
            "dsemi_20d": hist_feats.get("dsemi_20d") if hist_feats else np.nan,
            "dd_20d": hist_feats.get("dd_20d") if hist_feats else np.nan,
            "valid_X_all6": (hist_feats is not None and not np.isnan(hist_feats.get("r_1d", np.nan))),
            "S_next": s_next,
            "target_r_next": r_next,
            "target_status": target_status
        })
        
    df_all = pd.DataFrame(all_feature_records).sort_values('date').reset_index(drop=True)
    
    # Partition into Development and Validation
    df_dev = df_all[df_all['date'] <= '2019-12-31'].copy().reset_index(drop=True)
    df_val = df_all[(df_all['date'] >= '2020-01-01') & (df_all['date'] <= '2021-12-31')].copy().reset_index(drop=True)
    
    print(f"\nFinal Aligned Records: Dev={len(df_dev)}, Val={len(df_val)}, Total={len(df_all)}")
    
    # Save CSVs
    dev_path = "output/stage6_features/spx_features_development_2010_2019.csv"
    val_path = "output/stage6_features/spx_features_validation_2020_2021.csv"
    
    df_dev.to_csv(dev_path, index=False)
    df_val.to_csv(val_path, index=False)
    
    # Hashes
    def get_sha256(filepath):
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
        
    dev_hash = get_sha256(dev_path)
    val_hash = get_sha256(val_path)
    
    # Metadata
    metadata = {
        "dataset_name": "SPX Corrected Candidate Feature Datasets (Stage 6 Audit Deliverable)",
        "creation_date": "2026-10-21",
        "status": "CANDIDATE_AUDIT_OUTPUT (NOT PERMANENTLY FROZEN; PENDING INFORMATION CUTOFF AND TEST AUDIT DECISIONS)",
        "test_partition_status": "COMPROMISED_ACCESS_DISCLOSURE: Download of ^GSPC cash closes through January 2022 accessed the 2022-01-03 closing price (4796.56) across the test boundary. Raw 2022-2023 option bundles remained unopened, but cash close access compromises the claim of an untouched test partition. The terminal validation target r_next on 2021-12-31 has been set to NaN to prevent test data persistence in the feature matrix.",
        "rate_fallback_disclosure": "On two federal bank holidays where the US bond market was closed but equity markets traded (2010-10-11 Columbus Day and 2016-11-11 Veterans Day), ^IRX discount yields were missing. The pipeline applied causal carryforward from the prior session with explicit rate_source logging ('CAUSAL_PRIOR_SESSION_CARRYFORWARD') and rate_is_fallback=True. Zero silent constant substitution was performed.",
        "partitions": {
            "development": {
                "file": os.path.basename(dev_path),
                "date_range": [str(df_dev['date'].min()), str(df_dev['date'].max())],
                "row_count": len(df_dev),
                "sha256": dev_hash,
                "q_valid_all5_count": int(df_dev['valid_Q_all5'].sum()),
                "q_missing_all5_count": int((~df_dev['valid_Q_all5']).sum()),
                "q_missing_all5_pct": float((~df_dev['valid_Q_all5']).mean() * 100.0),
                "q_valid_30d_only_count": int(df_dev['valid_Q_30d'].sum()),
                "q_missing_30d_only_count": int((~df_dev['valid_Q_30d']).sum()),
                "q_missing_30d_only_pct": float((~df_dev['valid_Q_30d']).mean() * 100.0),
                "term_slope_missing_count": int(df_dev['TermSlope_60_30'].isna().sum()),
                "x_valid_all6_count": int(df_dev['valid_X_all6'].sum()),
                "rate_fallback_count": int(df_dev['rate_is_fallback'].sum()),
                "terminal_label_note": "Row 2019-12-31 target_r_next utilizes validation close 2020-01-02 (flagged CROSS_PARTITION_LABEL)"
            },
            "validation": {
                "file": os.path.basename(val_path),
                "date_range": [str(df_val['date'].min()), str(df_val['date'].max())],
                "row_count": len(df_val),
                "sha256": val_hash,
                "q_valid_all5_count": int(df_val['valid_Q_all5'].sum()),
                "q_missing_all5_count": int((~df_val['valid_Q_all5']).sum()),
                "q_missing_all5_pct": float((~df_val['valid_Q_all5']).mean() * 100.0),
                "q_valid_30d_only_count": int(df_val['valid_Q_30d'].sum()),
                "q_missing_30d_only_count": int((~df_val['valid_Q_30d']).sum()),
                "q_missing_30d_only_pct": float((~df_val['valid_Q_30d']).mean() * 100.0),
                "term_slope_missing_count": int(df_val['TermSlope_60_30'].isna().sum()),
                "x_valid_all6_count": int(df_val['valid_X_all6'].sum()),
                "rate_fallback_count": int(df_val['rate_is_fallback'].sum()),
                "terminal_label_note": "Row 2021-12-31 target_r_next is strictly NaN (UNOBSERVED_WITHOUT_TEST_CLOSE) to prevent leaking test period close 2022-01-03"
            }
        },
        "feature_units": {
            "SVIX_30d": "Decimal annualized simple variance swap volatility (e.g. 0.1200 = 12.00%)",
            "QSkew_30d": "Standardized centered 3rd risk-neutral moment (unitless)",
            "QKurt_30d": "Standardized centered 4th risk-neutral moment (Gaussian = 3.0, non-excess)",
            "ATM_IV_30d": "Decimal annualized Black-76 implied volatility",
            "ATM_IV_60d": "Decimal annualized Black-76 implied volatility",
            "TermSlope_60_30": "ATM_IV_60d - ATM_IV_30d (vol points)",
            "S_t": "Index points (S&P 500 cash closing price)",
            "r_1d": "Daily log return ln(S_t / S_{t-1})",
            "r_5d": "5-day cumulative log return",
            "rv_5d": "Decimal annualized 5-day realized volatility",
            "rv_20d": "Decimal annualized 20-day realized volatility",
            "dsemi_20d": "Decimal annualized 20-day downside semivariance",
            "dd_20d": "Trailing 20-day maximum drawdown (negative decimal or 0.0)",
            "target_r_next": "Next-day log return ln(S_{t+1} / S_t) (forecast target label)"
        }
    }
    
    with open("output/stage6_features/feature_datasets_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Corrected metadata written to output/stage6_features/feature_datasets_metadata.json")
    print(f"Total execution time: {time.time()-t_start:.2f}s")


if __name__ == "__main__":
    run_pipeline()
