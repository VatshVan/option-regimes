"""
pipeline.py
===========
Orchestrator for the Stage 4 Feature Construction Pipeline.
Constructs the option-implied feature vector Q_t and historical state vector X_t
for the primary SPX MVP, with point-in-time enforcement and comprehensive diagnostics.
"""

from typing import Dict, Any, Tuple, Optional, List
import os
import json
import numpy as np
import pandas as pd

from .options_cleaning import clean_options_chain
from .options_moments import compute_tenor_moments, interpolate_constant_maturity
from .historical_state import compute_historical_features, fetch_historical_spx_closes


class FeaturePipeline:
    """
    Feature construction pipeline for SPX option-implied (Q_t) and historical (X_t) features.
    """
    def __init__(
        self,
        min_bid: float = 0.05,
        max_rel_spread: float = 0.35,
        target_dte_primary: float = 30.0,
        target_dte_secondary: float = 60.0
    ):
        self.min_bid = min_bid
        self.max_rel_spread = max_rel_spread
        self.target_dte_primary = target_dte_primary
        self.target_dte_secondary = target_dte_secondary

    def process_date(
        self,
        date_str: str,
        options_filepath: str,
        risk_free_rate: float,
        df_closes: pd.DataFrame,
        cash_close_expected: Optional[float] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Processes a single observation date to construct [Q_t, X_t] features and diagnostic audit.
        
        Parameters
        ----------
        date_str : str
            Date in 'YYYY-MM-DD' format.
        options_filepath : str
            Path to monthly raw text file containing the date.
        risk_free_rate : float
            Annualized risk-free rate for the date (e.g. 13-week T-Bill).
        df_closes : pd.DataFrame
            Daily S&P 500 closing index series up to and including date_str.
        cash_close_expected : float, optional
            Expected cash index close for cross-checking underlying synchronization.
            
        Returns
        -------
        features : Dict[str, Any]
            Dictionary of extracted Q_t and X_t feature values.
        diagnostics : Dict[str, Any]
            Detailed audit log of schema, filtering, tenors, and finite-grid bounds.
        """
        diagnostics: Dict[str, Any] = {
            "date": date_str,
            "options_file": options_filepath,
            "risk_free_rate": risk_free_rate,
            "status": "FAILED",
            "schema_diagnostics": {},
            "tenor_diagnostics": {},
            "interpolation_30d": {},
            "interpolation_60d": {},
            "historical_diagnostics": {},
            "warnings": [],
            "failure_reason": None
        }
        
        # 1. Stream option rows for target date only (keeping raw inputs immutable)
        chunks = []
        try:
            for chunk in pd.read_csv(options_filepath, sep=',', chunksize=10000, low_memory=False):
                chunk.columns = chunk.columns.str.strip().str.replace('[', '', regex=False).str.replace(']', '', regex=False)
                c = chunk[chunk['QUOTE_DATE'].astype(str).str.strip() == date_str]
                if not c.empty:
                    chunks.append(c)
        except Exception as e:
            diagnostics["failure_reason"] = f"Failed to read options file: {str(e)}"
            return {}, diagnostics
            
        if not chunks:
            diagnostics["failure_reason"] = f"No option records found for date {date_str} in {options_filepath}"
            return {}, diagnostics
            
        df_raw = pd.concat(chunks, ignore_index=True)
        df_clean, diag_schema = clean_options_chain(df_raw)
        diagnostics["schema_diagnostics"] = diag_schema
        
        # Check timestamp
        timestamps = diag_schema.get("observed_timestamps", [])
        diagnostics["quote_readtime"] = timestamps[0] if timestamps else "UNKNOWN"
        if any("16:15" in ts for ts in timestamps):
            diagnostics["warnings"].append("Potential 16:15 ET option close timestamp observed (look-ahead risk vs 16:00 cash close)")
            
        # 2. Iterate across all available tenors to compute moments
        all_dtes = sorted(df_clean['DTE'].dropna().unique().tolist())
        diagnostics["available_dtes"] = all_dtes
        
        tenor_results: Dict[float, Dict[str, Any]] = {}
        for dte in all_dtes:
            # We evaluate tenors between 15 and 90 DTE to support 30d and 60d interpolation
            if 15.0 <= dte <= 90.0:
                df_tenor = df_clean[df_clean['DTE'] == dte].copy()
                t_res = compute_tenor_moments(
                    df_tenor,
                    r=risk_free_rate,
                    min_bid=self.min_bid,
                    max_rel_spread=self.max_rel_spread
                )
                tenor_results[dte] = t_res
                
        diagnostics["tenor_diagnostics"] = tenor_results
        
        # 3. Constant 30-Day Interpolation for Q_t
        interp_30, diag_interp_30 = interpolate_constant_maturity(
            tenor_results, target_dte=self.target_dte_primary
        )
        diagnostics["interpolation_30d"] = diag_interp_30
        
        # 4. Constant 60-Day Interpolation for ATM_IV (Term Structure Slope)
        interp_60, diag_interp_60 = interpolate_constant_maturity(
            tenor_results, target_dte=self.target_dte_secondary
        )
        diagnostics["interpolation_60d"] = diag_interp_60
        
        # 5. Compute Historical State Features X_t
        hist_feats, diag_hist = compute_historical_features(df_closes, date_str, window=20)
        diagnostics["historical_diagnostics"] = diag_hist
        
        # Assemble feature outputs
        features: Dict[str, Any] = {
            "date": date_str,
            "quote_timestamp": diagnostics["quote_readtime"],
            "risk_free_rate": risk_free_rate
        }
        
        if interp_30 is not None:
            features["SVIX_30d"] = interp_30.get("SVIX")
            features["QSkew_30d"] = interp_30.get("QSkew")
            features["QKurt_30d"] = interp_30.get("QKurt")
            features["ATM_IV_30d"] = interp_30.get("ATM_IV")
        else:
            features["SVIX_30d"] = np.nan
            features["QSkew_30d"] = np.nan
            features["QKurt_30d"] = np.nan
            features["ATM_IV_30d"] = np.nan
            
        if interp_60 is not None and interp_30 is not None:
            features["ATM_IV_60d"] = interp_60.get("ATM_IV")
            if features["ATM_IV_60d"] is not None and features["ATM_IV_30d"] is not None:
                features["TermSlope_60_30"] = features["ATM_IV_60d"] - features["ATM_IV_30d"]
            else:
                features["TermSlope_60_30"] = np.nan
        else:
            features["ATM_IV_60d"] = np.nan
            features["TermSlope_60_30"] = np.nan
            
        if hist_feats is not None:
            features["S_t"] = hist_feats.get("S_t")
            features["r_1d"] = hist_feats.get("r_1d")
            features["r_5d"] = hist_feats.get("r_5d")
            features["rv_5d"] = hist_feats.get("rv_5d")
            features["rv_20d"] = hist_feats.get("rv_20d")
            features["dsemi_20d"] = hist_feats.get("dsemi_20d")
            features["dd_20d"] = hist_feats.get("dd_20d")
        else:
            features["S_t"] = np.nan
            features["r_1d"] = np.nan
            features["r_5d"] = np.nan
            features["rv_5d"] = np.nan
            features["rv_20d"] = np.nan
            features["dsemi_20d"] = np.nan
            features["dd_20d"] = np.nan
            
        if cash_close_expected is not None and "S_t" in features:
            features["cash_close_diff"] = features["S_t"] - cash_close_expected
            
        if not np.isnan(features.get("SVIX_30d", np.nan)) and not np.isnan(features.get("r_1d", np.nan)):
            diagnostics["status"] = "SUCCESS"
        else:
            diagnostics["status"] = "PARTIAL"
            
        return features, diagnostics
