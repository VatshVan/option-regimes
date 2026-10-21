"""
correct_feature_datasets.py
===========================
Applies the required corrections to the Stage 6 feature datasets:
1. Enforces strict boundary isolation:
   - Sets 2021-12-31 target_r_next to NaN in validation dataset to prevent test close leakage.
   - Sets 2019-12-31 target_r_next to NaN in development dataset to prevent validation close leakage.
   - Truncates spx_daily_closes_2009_2021.csv to strictly <= 2021-12-31.
2. Exposes rate fallbacks and eliminates silent imputation:
   - On 2010-10-11 and 2016-11-11 (bond market holiday closures), applies causal carryforward
     from prior session with explicit rate_source, rate_is_fallback=True, and rate_fallback_note.
   - Replaces 2016-11-11 option moments with values recomputed at exact causal rate (0.004652).
3. Standardizes feature completeness diagnostics:
   - Evaluates all five Q_t features (valid_Q_all5) and distinguishes from 30d-only moments (valid_Q_30d).
   - Updates status_Q column to reflect SUCCESS_ALL_5, PARTIAL_30D_ONLY, FAILED_30D, ERR_MISSING_OPTION_FILE_OR_DATE.
4. Recomputes cryptographic SHA-256 hashes and updates metadata with complete disclosures.
"""

import os
import sys
import json
import math
import hashlib
import numpy as np
import pandas as pd

# Load existing feature datasets
dev_path = "output/stage6_features/spx_features_development_2010_2019.csv"
val_path = "output/stage6_features/spx_features_validation_2020_2021.csv"
meta_path = "output/stage6_features/feature_datasets_metadata.json"
closes_path = "output/stage6_features/spx_daily_closes_2009_2021.csv"

df_dev = pd.read_csv(dev_path)
df_val = pd.read_csv(val_path)

# --- 1. Correct Development Dataset ---
print("Correcting Development Dataset (2010-2019)...")

# Rate audit fields
df_dev['rate_source'] = "CBOE_IRX_ACTUAL"
df_dev['rate_is_fallback'] = False
df_dev['rate_fallback_note'] = "Direct actual close from ^IRX"

# Columbus Day 2010 (2010-10-11): Bond market closed; carried forward from 2010-10-08 (0.115% discount -> 0.001166 continuous)
idx_columbus = df_dev[df_dev['date'] == '2010-10-11'].index[0]
df_dev.loc[idx_columbus, 'quoted_irx_pct'] = 0.115
df_dev.loc[idx_columbus, 'risk_free_rate_cont'] = 0.001166
df_dev.loc[idx_columbus, 'rate_source'] = "CAUSAL_PRIOR_SESSION_CARRYFORWARD"
df_dev.loc[idx_columbus, 'rate_is_fallback'] = True
df_dev.loc[idx_columbus, 'rate_fallback_note'] = "US bond market closed for Columbus Day; causally carried forward from 2010-10-08"

# Veterans Day 2016 (2016-11-11): Bond market closed; carried forward from 2016-11-10 (0.458% discount -> 0.004652 continuous)
idx_veterans = df_dev[df_dev['date'] == '2016-11-11'].index[0]
df_dev.loc[idx_veterans, 'quoted_irx_pct'] = 0.458
df_dev.loc[idx_veterans, 'risk_free_rate_cont'] = 0.004652
df_dev.loc[idx_veterans, 'rate_source'] = "CAUSAL_PRIOR_SESSION_CARRYFORWARD"
df_dev.loc[idx_veterans, 'rate_is_fallback'] = True
df_dev.loc[idx_veterans, 'rate_fallback_note'] = "US bond market closed for Veterans Day; causally carried forward from 2016-11-10"

# Recomputed moments on 2016-11-11 with exact rate 0.004652
df_dev.loc[idx_veterans, 'SVIX_30d'] = 0.1336316369477616
df_dev.loc[idx_veterans, 'QSkew_30d'] = -2.0621571666622542
df_dev.loc[idx_veterans, 'ATM_IV_30d'] = 0.12000270458603271
# Recompute TermSlope_60_30
if not pd.isna(df_dev.loc[idx_veterans, 'ATM_IV_60d']):
    df_dev.loc[idx_veterans, 'TermSlope_60_30'] = df_dev.loc[idx_veterans, 'ATM_IV_60d'] - df_dev.loc[idx_veterans, 'ATM_IV_30d']

# Target boundary handling on 2019-12-31: strictly eliminate validation-period close
idx_dev_end = df_dev[df_dev['date'] == '2019-12-31'].index[0]
df_dev['target_status'] = "IN_PARTITION_VALID"
df_dev.loc[idx_dev_end, 'S_next'] = np.nan
df_dev.loc[idx_dev_end, 'target_r_next'] = np.nan
df_dev.loc[idx_dev_end, 'target_status'] = "UNOBSERVED_WITHOUT_VALIDATION_CLOSE (validation close 2020-01-02 omitted to protect partition purity)"

# Feature completeness flags
has_svix_dev = ~df_dev['SVIX_30d'].isna()
has_qskew_dev = ~df_dev['QSkew_30d'].isna()
has_qkurt_dev = ~df_dev['QKurt_30d'].isna()
has_atm30_dev = ~df_dev['ATM_IV_30d'].isna()
has_slope_dev = ~df_dev['TermSlope_60_30'].isna()

df_dev['valid_Q_30d'] = has_svix_dev & has_qskew_dev & has_qkurt_dev & has_atm30_dev
df_dev['valid_Q_all5'] = df_dev['valid_Q_30d'] & has_slope_dev
df_dev['valid_X_all6'] = ~df_dev['r_1d'].isna()

# Updated status_Q column
def get_status_q(row):
    if row['status_Q'] == 'ERR_MISSING_OPTION_FILE_OR_DATE':
        return 'ERR_MISSING_OPTION_FILE_OR_DATE'
    if row['valid_Q_all5']:
        return 'SUCCESS_ALL_5'
    elif row['valid_Q_30d']:
        return 'PARTIAL_30D_ONLY (missing 60d term slope)'
    else:
        return 'FAILED_30D (insufficient tenors or bracketing)'

df_dev['status_Q'] = df_dev.apply(get_status_q, axis=1)

# --- 2. Correct Validation Dataset ---
print("Correcting Validation Dataset (2020-2021)...")

df_val['rate_source'] = "CBOE_IRX_ACTUAL"
df_val['rate_is_fallback'] = False
df_val['rate_fallback_note'] = "Direct actual close from ^IRX"

# Target boundary handling on 2021-12-31: strictly eliminate test-period close
idx_val_end = df_val[df_val['date'] == '2021-12-31'].index[0]
df_val['target_status'] = "IN_PARTITION_VALID"
df_val.loc[idx_val_end, 'S_next'] = np.nan
df_val.loc[idx_val_end, 'target_r_next'] = np.nan
df_val.loc[idx_val_end, 'target_status'] = "UNOBSERVED_WITHOUT_TEST_CLOSE (test close 2022-01-03 omitted to protect partition purity)"

# Feature completeness flags
has_svix_val = ~df_val['SVIX_30d'].isna()
has_qskew_val = ~df_val['QSkew_30d'].isna()
has_qkurt_val = ~df_val['QKurt_30d'].isna()
has_atm30_val = ~df_val['ATM_IV_30d'].isna()
has_slope_val = ~df_val['TermSlope_60_30'].isna()

df_val['valid_Q_30d'] = has_svix_val & has_qskew_val & has_qkurt_val & has_atm30_val
df_val['valid_Q_all5'] = df_val['valid_Q_30d'] & has_slope_val
df_val['valid_X_all6'] = ~df_val['r_1d'].isna()

df_val['status_Q'] = df_val.apply(get_status_q, axis=1)

# --- 3. Save Corrected Datasets and Compute Hashes ---
df_dev.to_csv(dev_path, index=False)
df_val.to_csv(val_path, index=False)

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

dev_hash = get_sha256(dev_path)
val_hash = get_sha256(val_path)

# --- 4. Truncate Cached Closes to strictly <= 2021-12-31 ---
df_closes = pd.read_csv(closes_path)
df_closes_clean = df_closes[df_closes['date'] <= '2021-12-31'].copy().reset_index(drop=True)
df_closes_clean.to_csv(closes_path, index=False)
print(f"Truncated cash closes from {len(df_closes)} to {len(df_closes_clean)} (max date: {df_closes_clean['date'].max()})")

# --- 5. Update Metadata with Explicit Disclosures ---
metadata = {
    "dataset_name": "SPX Corrected Candidate Feature Datasets (Stage 6 Deliverable)",
    "creation_date": "2026-10-21",
    "dataset_status": "CANDIDATE_AUDIT_OUTPUT (NOT PERMANENTLY FROZEN; PENDING INFORMATION CUTOFF AND TEST AUDIT DECISIONS)",
    "test_partition_status": "COMPROMISED_ACCESS_DISCLOSURE: Downloading ^GSPC cash closes through January 2022 accessed both the 2022-01-03 close (4796.56) and 2022-01-04 close (4793.54). These test-period closes were committed to the repository history in commit cee01a1 and used to compute r_{t+1} (0.0063538) on 2021-12-31. While raw 2022-2023 option bundles remained unopened, the test seal was breached and remains permanently recorded in Git history. In the working tree and candidate datasets, the 2022 cash closes have been purged and both boundary target labels (2019-12-31 in development and 2021-12-31 in validation) have been set strictly to NaN.",
    "rate_fallback_disclosure": "On two federal bank holidays where bond markets were closed but equity markets traded (2010-10-11 Columbus Day and 2016-11-11 Veterans Day), ^IRX discount yields were missing. The pipeline causally carried forward rates from the prior session with explicit rate_source, rate_is_fallback=True, and rate_fallback_note logging. Zero silent constant substitution was performed.",
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
            "terminal_label_note": "Row 2019-12-31 target_r_next is strictly NaN (UNOBSERVED_WITHOUT_VALIDATION_CLOSE) to prevent partition boundary leakage"
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
            "terminal_label_note": "Row 2021-12-31 target_r_next is strictly NaN (UNOBSERVED_WITHOUT_TEST_CLOSE) to prevent leaking test close 2022-01-03"
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

with open(meta_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print("\n=== Summary of Corrected Deliverables ===")
print(f"Development CSV: {dev_path} (SHA-256: {dev_hash})")
print(f"  Valid Q (all 5): {df_dev['valid_Q_all5'].sum()} / {len(df_dev)} ({df_dev['valid_Q_all5'].mean()*100:.2f}%)")
print(f"  Missing Q (any 5): {(~df_dev['valid_Q_all5']).sum()} / {len(df_dev)} ({(~df_dev['valid_Q_all5']).mean()*100:.2f}%)")
print(f"  Rate fallbacks: {df_dev['rate_is_fallback'].sum()}")
print(f"  Terminal target status: {df_dev.loc[idx_dev_end, 'target_status']}")

print(f"\nValidation CSV: {val_path} (SHA-256: {val_hash})")
print(f"  Valid Q (all 5): {df_val['valid_Q_all5'].sum()} / {len(df_val)} ({df_val['valid_Q_all5'].mean()*100:.2f}%)")
print(f"  Missing Q (any 5): {(~df_val['valid_Q_all5']).sum()} / {len(df_val)} ({(~df_val['valid_Q_all5']).mean()*100:.2f}%)")
print(f"  Terminal target r_next: {df_val.loc[idx_val_end, 'target_r_next']}")
print(f"  Terminal target status: {df_val.loc[idx_val_end, 'target_status']}")
