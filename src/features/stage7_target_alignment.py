"""
stage7_target_alignment.py
==========================
Constructs the Stage 7 operational target datasets under user-authorized Proposal A:
    y_t = ln(S_{t+2} / S_{t+1})
where features at the end of session t predict the close-to-close physical return
over the subsequent session (from session t+1 close to session t+2 close).

This timing shift strictly resolves the 16:00 cash equity close vs. 16:15 option quote
lookahead ambiguity (Gate B Check 3 / BLK-1) because the entire return interval [t+1, t+2]
begins in the future relative to the option snapshot at date t.

Strict Partition Boundary Enforcement:
- Development (2010-01-04 to 2019-12-31):
  - Row 2019-12-30: S_{t+1} is 2019-12-31, but S_{t+2} is 2020-01-02 (validation).
    Target y_t is strictly set to NaN (UNOBSERVED_WITHOUT_VALIDATION_CLOSE).
  - Row 2019-12-31: S_{t+1} is 2020-01-02, S_{t+2} is 2020-01-03 (validation).
    Target y_t is strictly set to NaN (UNOBSERVED_WITHOUT_VALIDATION_CLOSE).
- Validation (2020-01-02 to 2021-12-31):
  - Row 2021-12-30: S_{t+1} is 2021-12-31, but S_{t+2} is 2022-01-03 (test).
    Target y_t is strictly set to NaN (UNOBSERVED_WITHOUT_TEST_CLOSE).
  - Row 2021-12-31: S_{t+1} is 2022-01-03, S_{t+2} is 2022-01-04 (test).
    Target y_t is strictly set to NaN (UNOBSERVED_WITHOUT_TEST_CLOSE).

Preserves Stage 6 CSVs as historical candidate artifacts and creates separate Stage 7 datasets.
"""

import os
import sys
import json
import math
import hashlib
import numpy as np
import pandas as pd

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def align_stage7_datasets(
    dev_stage6_path: str = "output/stage6_features/spx_features_development_2010_2019.csv",
    val_stage6_path: str = "output/stage6_features/spx_features_validation_2020_2021.csv",
    closes_path: str = "output/stage6_features/spx_daily_closes_2009_2021.csv",
    output_dir: str = "output/stage7_datasets"
):
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== Stage 7 Operational Target Alignment (Proposal A) ===")
    
    # 1. Load Stage 6 candidate datasets and cash closes
    df_dev = pd.read_csv(dev_stage6_path)
    df_val = pd.read_csv(val_stage6_path)
    df_closes = pd.read_csv(closes_path)
    
    # Map dates to closes
    date_to_close = dict(zip(df_closes['date'], df_closes['close']))
    close_dates = sorted(df_closes['date'].unique())
    date_to_idx = {d: i for i, d in enumerate(close_dates)}
    
    # Process Development
    print(f"Processing Development dataset ({len(df_dev)} sessions)...")
    dev_dates = sorted(df_dev['date'].unique())
    dev_max_date = df_dev['date'].max()
    
    df_dev_stage7 = df_dev.copy()
    s_next1_dev = []
    s_next2_dev = []
    target_y_dev = []
    status_y_dev = []
    
    for _, row in df_dev_stage7.iterrows():
        d = row['date']
        idx = date_to_idx.get(d)
        if idx is None or idx + 2 >= len(close_dates):
            s_next1_dev.append(np.nan)
            s_next2_dev.append(np.nan)
            target_y_dev.append(np.nan)
            status_y_dev.append("UNOBSERVED_OUT_OF_RANGE")
            continue
            
        d_next1 = close_dates[idx + 1]
        d_next2 = close_dates[idx + 2]
        
        # Check boundary: both next1 and next2 must reside in Development (<= dev_max_date)
        if d_next1 > dev_max_date or d_next2 > dev_max_date:
            s_next1_dev.append(np.nan)
            s_next2_dev.append(np.nan)
            target_y_dev.append(np.nan)
            status_y_dev.append(f"UNOBSERVED_WITHOUT_VALIDATION_CLOSE (interval [{d_next1}, {d_next2}] crosses into validation)")
        else:
            s1 = date_to_close[d_next1]
            s2 = date_to_close[d_next2]
            y = math.log(s2 / s1)
            s_next1_dev.append(s1)
            s_next2_dev.append(s2)
            target_y_dev.append(y)
            status_y_dev.append("IN_PARTITION_VALID")
            
    df_dev_stage7['S_next1'] = s_next1_dev
    df_dev_stage7['S_next2'] = s_next2_dev
    df_dev_stage7['target_y_next2'] = target_y_dev
    df_dev_stage7['target_y_status'] = status_y_dev
    df_dev_stage7['valid_target_y'] = ~df_dev_stage7['target_y_next2'].isna()
    df_dev_stage7['valid_supervised_pair_all5'] = df_dev_stage7['valid_Q_all5'] & df_dev_stage7['valid_target_y']
    
    # Process Validation
    print(f"Processing Validation dataset ({len(df_val)} sessions)...")
    val_max_date = df_val['date'].max()
    
    df_val_stage7 = df_val.copy()
    s_next1_val = []
    s_next2_val = []
    target_y_val = []
    status_y_val = []
    
    for _, row in df_val_stage7.iterrows():
        d = row['date']
        idx = date_to_idx.get(d)
        if idx is None or idx + 2 >= len(close_dates):
            # idx + 2 exceeds closes table (which ends at 2021-12-31)
            s_next1_val.append(np.nan)
            s_next2_val.append(np.nan)
            target_y_val.append(np.nan)
            status_y_val.append("UNOBSERVED_WITHOUT_TEST_CLOSE (interval crosses into 2022 test partition)")
            continue
            
        d_next1 = close_dates[idx + 1]
        d_next2 = close_dates[idx + 2]
        
        # Check boundary: both next1 and next2 must reside in Validation (<= val_max_date)
        if d_next1 > val_max_date or d_next2 > val_max_date:
            s_next1_val.append(np.nan)
            s_next2_val.append(np.nan)
            target_y_val.append(np.nan)
            status_y_val.append(f"UNOBSERVED_WITHOUT_TEST_CLOSE (interval [{d_next1}, {d_next2}] crosses into test partition)")
        else:
            s1 = date_to_close[d_next1]
            s2 = date_to_close[d_next2]
            y = math.log(s2 / s1)
            s_next1_val.append(s1)
            s_next2_val.append(s2)
            target_y_val.append(y)
            status_y_val.append("IN_PARTITION_VALID")
            
    df_val_stage7['S_next1'] = s_next1_val
    df_val_stage7['S_next2'] = s_next2_val
    df_val_stage7['target_y_next2'] = target_y_val
    df_val_stage7['target_y_status'] = status_y_val
    df_val_stage7['valid_target_y'] = ~df_val_stage7['target_y_next2'].isna()
    df_val_stage7['valid_supervised_pair_all5'] = df_val_stage7['valid_Q_all5'] & df_val_stage7['valid_target_y']
    
    # Save Stage 7 Datasets
    dev_out_path = os.path.join(output_dir, "spx_stage7_operational_development_2010_2019.csv")
    val_out_path = os.path.join(output_dir, "spx_stage7_operational_validation_2020_2021.csv")
    
    df_dev_stage7.to_csv(dev_out_path, index=False)
    df_val_stage7.to_csv(val_out_path, index=False)
    
    dev_hash = compute_sha256(dev_out_path)
    val_hash = compute_sha256(val_out_path)
    
    # Sensitivity benchmark counts (2012-07-02 to 2019-12-31)
    df_dev_2012 = df_dev_stage7[df_dev_stage7['date'] >= '2012-07-02']
    
    metadata = {
        "dataset_name": "SPX Stage 7 Operational Feature & Target Datasets",
        "creation_date": "2026-10-22",
        "governance_status": "USER_AUTHORIZED_PROJECT_DECISIONS (Stage 7 Operational Baseline)",
        "timing_alignment_protocol": "PROPOSAL_A_LAGGED_CLOSE_TO_CLOSE: Target y_t = ln(S_{t+2} / S_{t+1})",
        "timing_rationale": "Features at session t close predict the return from session t+1 close to session t+2 close, cleanly eliminating potential 16:00 cash equity vs. 16:15 option quote lookahead leakage.",
        "test_partition_status": "COMPROMISED_ACCESS_DISCLOSURE: Downloading ^GSPC cash closes through January 2022 accessed both the 2022-01-03 close (4796.56) and 2022-01-04 close (4793.54). These test-period closes were committed to the repository history in commit cee01a1 and used to compute r_{t+1} (0.0063538) on 2021-12-31. While raw 2022-2023 option bundles remained unopened, the test seal was breached and remains permanently recorded in Git history. In the working tree and candidate datasets, the 2022 cash closes have been purged and both boundary target labels (2019-12-31 in development and 2021-12-31 in validation) have been set strictly to NaN.",
        "known_return_exclusion_rule": "The known Jan 3-to-Jan 4 return (ln(4793.54 / 4796.56) = -0.0006298) is strictly excluded from any eventual test score and disclosed.",
        "partitions": {
            "development": {
                "file": os.path.basename(dev_out_path),
                "date_range": [str(df_dev_stage7['date'].min()), str(df_dev_stage7['date'].max())],
                "row_count": len(df_dev_stage7),
                "sha256": dev_hash,
                "feature_complete_q_all5_count": int(df_dev_stage7['valid_Q_all5'].sum()),
                "feature_missing_q_all5_count": int((~df_dev_stage7['valid_Q_all5']).sum()),
                "observed_in_partition_target_count": int(df_dev_stage7['valid_target_y'].sum()),
                "unobserved_boundary_target_count": int((~df_dev_stage7['valid_target_y']).sum()),
                "usable_supervised_pairs_all5_count": int(df_dev_stage7['valid_supervised_pair_all5'].sum()),
                "usable_supervised_pairs_x_only_count": int(df_dev_stage7['valid_target_y'].sum()),
                "terminal_boundary_rows": ["2019-12-30", "2019-12-31"],
                "terminal_boundary_note": "Target y_t is strictly NaN on 2019-12-30 and 2019-12-31 because S_{t+2} resides in the validation partition."
            },
            "validation": {
                "file": os.path.basename(val_out_path),
                "date_range": [str(df_val_stage7['date'].min()), str(df_val_stage7['date'].max())],
                "row_count": len(df_val_stage7),
                "sha256": val_hash,
                "feature_complete_q_all5_count": int(df_val_stage7['valid_Q_all5'].sum()),
                "feature_missing_q_all5_count": int((~df_val_stage7['valid_Q_all5']).sum()),
                "observed_in_partition_target_count": int(df_val_stage7['valid_target_y'].sum()),
                "unobserved_boundary_target_count": int((~df_val_stage7['valid_target_y']).sum()),
                "usable_validation_scoring_rows_all5_count": int(df_val_stage7['valid_supervised_pair_all5'].sum()),
                "usable_validation_scoring_rows_x_only_count": int(df_val_stage7['valid_target_y'].sum()),
                "terminal_boundary_rows": ["2021-12-30", "2021-12-31"],
                "terminal_boundary_note": "Target y_t is strictly NaN on 2021-12-30 and 2021-12-31 because S_{t+2} resides in the test partition."
            },
            "mid_2012_sensitivity_benchmark": {
                "date_range": ["2012-07-02", "2019-12-31"],
                "row_count": len(df_dev_2012),
                "feature_complete_q_all5_count": int(df_dev_2012['valid_Q_all5'].sum()),
                "observed_in_partition_target_count": int(df_dev_2012['valid_target_y'].sum()),
                "usable_supervised_pairs_all5_count": int(df_dev_2012['valid_supervised_pair_all5'].sum()),
                "usable_supervised_pairs_x_only_count": int(df_dev_2012['valid_target_y'].sum())
            }
        }
    }
    
    meta_path = os.path.join(output_dir, "stage7_dataset_metadata.json")
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print("\n=== Stage 7 Operational Dataset Summary ===")
    print(f"Development ({dev_out_path}):")
    print(f"  Total sessions: {len(df_dev_stage7)}")
    print(f"  Feature-complete rows (valid_Q_all5): {df_dev_stage7['valid_Q_all5'].sum()}")
    print(f"  Observed within-partition target (valid_target_y): {df_dev_stage7['valid_target_y'].sum()}")
    print(f"  Usable supervised training pairs (Z_t, y_t): {df_dev_stage7['valid_supervised_pair_all5'].sum()}")
    print(f"  SHA-256: {dev_hash}")
    
    print(f"\nValidation ({val_out_path}):")
    print(f"  Total sessions: {len(df_val_stage7)}")
    print(f"  Feature-complete rows (valid_Q_all5): {df_val_stage7['valid_Q_all5'].sum()}")
    print(f"  Observed within-partition target (valid_target_y): {df_val_stage7['valid_target_y'].sum()}")
    print(f"  Usable validation scoring rows (Z_t, y_t): {df_val_stage7['valid_supervised_pair_all5'].sum()}")
    print(f"  SHA-256: {val_hash}")
    
    print(f"\nMid-2012 Sensitivity Benchmark:")
    print(f"  Total sessions: {len(df_dev_2012)}")
    print(f"  Feature-complete rows: {df_dev_2012['valid_Q_all5'].sum()}")
    print(f"  Usable supervised training pairs: {df_dev_2012['valid_supervised_pair_all5'].sum()}")
    
    return metadata

if __name__ == "__main__":
    align_stage7_datasets()
