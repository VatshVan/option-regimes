"""
options_cleaning.py
===================
Contract-wise screening, synthetic forward inversion, and quote-level quality filtering
for SPX option chains according to the frozen research protocol.
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd


def clean_options_chain(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw OptionsDX option chain columns, strips whitespace, and enforces numeric types.
    
    Parameters
    ----------
    df_raw : pd.DataFrame
        Raw dataframe loaded from OptionsDX EOD text file.
        
    Returns
    -------
    df : pd.DataFrame
        Cleaned dataframe with standardized column names and numeric conversions.
    diagnostics : Dict[str, Any]
        Metadata diagnostics including row count, columns count, and observed timestamps.
    """
    df = df_raw.copy()
    
    # Strip whitespace and brackets from column headers
    df.columns = df.columns.str.strip().str.replace('[', '', regex=False).str.replace(']', '', regex=False)
    
    # Capture timestamp metadata
    observed_timestamps = []
    if 'QUOTE_READTIME' in df.columns:
        observed_timestamps = df['QUOTE_READTIME'].astype(str).str.strip().unique().tolist()
    
    observed_dates = []
    if 'QUOTE_DATE' in df.columns:
        observed_dates = df['QUOTE_DATE'].astype(str).str.strip().unique().tolist()
        
    # Convert numeric fields
    numeric_cols = [
        'DTE', 'STRIKE', 'UNDERLYING_LAST',
        'C_BID', 'C_ASK', 'C_VOLUME', 'C_IV',
        'P_BID', 'P_ASK', 'P_VOLUME', 'P_IV'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Normalize string columns
    for str_col in ['QUOTE_DATE', 'QUOTE_READTIME', 'EXPIRE_DATE']:
        if str_col in df.columns:
            df[str_col] = df[str_col].astype(str).str.strip()
            
    diagnostics = {
        "raw_row_count": len(df),
        "columns_count": len(df.columns),
        "observed_dates": observed_dates,
        "observed_timestamps": observed_timestamps,
        "has_open_interest": "OPEN_INTEREST" in df.columns,
        "has_volume": "C_VOLUME" in df.columns and "P_VOLUME" in df.columns
    }
    
    return df, diagnostics


def invert_synthetic_forward(
    df_tenor: pd.DataFrame,
    r: float,
    min_bid: float = 0.05
) -> Tuple[Optional[float], Optional[float], Dict[str, Any]]:
    """
    Inverts the synthetic forward price F_{t,tau} at the ATM strike K* where
    |C_mid - P_mid| is minimized, enforcing quote liquidity on both call and put sides.
    
    Parameters
    ----------
    df_tenor : pd.DataFrame
        Cleaned option chain records for a single maturity tenor.
    r : float
        Annualized continuously compounded risk-free rate.
    min_bid : float
        Minimum bid threshold for call and put quotes at ATM.
        
    Returns
    -------
    F_parity : float or None
        Synthetic forward price inverted from put-call parity.
    K_star : float or None
        Chosen ATM strike.
    diagnostics : Dict[str, Any]
        Details of the inversion, including ATM call/put midpoints and quote status.
    """
    diag: Dict[str, Any] = {
        "status": "FAILED",
        "K_star": None,
        "F_parity": None,
        "C_mid": None,
        "P_mid": None,
        "diff_mid": None,
        "valid_pairs_count": 0,
        "failure_reason": None
    }
    
    if df_tenor.empty:
        diag["failure_reason"] = "Empty maturity dataframe"
        return None, None, diag
        
    # Check DTE
    dtes = df_tenor['DTE'].dropna().unique()
    if len(dtes) == 0:
        diag["failure_reason"] = "No valid DTE values"
        return None, None, diag
    dte = float(dtes[0])
    T = dte / 365.0
    
    # Filter valid call and put quote pairs
    mask_valid = (
        (df_tenor['C_BID'] > min_bid) &
        (df_tenor['P_BID'] > min_bid) &
        (df_tenor['C_ASK'] > df_tenor['C_BID']) &
        (df_tenor['P_ASK'] > df_tenor['P_BID']) &
        (df_tenor['STRIKE'] > 0)
    )
    df_valid = df_tenor[mask_valid].copy()
    diag["valid_pairs_count"] = len(df_valid)
    
    if df_valid.empty:
        diag["failure_reason"] = "No strike has simultaneously valid Call and Put quotes satisfying bid and positivity constraints"
        return None, None, diag
        
    df_valid['C_MID'] = 0.5 * (df_valid['C_BID'] + df_valid['C_ASK'])
    df_valid['P_MID'] = 0.5 * (df_valid['P_BID'] + df_valid['P_ASK'])
    df_valid['diff'] = (df_valid['C_MID'] - df_valid['P_MID']).abs()
    
    best_row = df_valid.loc[df_valid['diff'].idxmin()]
    K_star = float(best_row['STRIKE'])
    c_mid = float(best_row['C_MID'])
    p_mid = float(best_row['P_MID'])
    
    F_parity = float(K_star + np.exp(r * T) * (c_mid - p_mid))
    
    diag.update({
        "status": "SUCCESS",
        "K_star": K_star,
        "F_parity": F_parity,
        "C_mid": c_mid,
        "P_mid": p_mid,
        "diff_mid": float(best_row['diff']),
        "DTE": dte,
        "T": T,
        "r": r
    })
    
    return F_parity, K_star, diag


def screen_otm_quotes(
    df_tenor: pd.DataFrame,
    F_parity: float,
    min_bid: float = 0.05,
    max_rel_spread: float = 0.35
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Applies contract-wise screening to isolate liquid out-of-the-money (OTM) quotes.
    For K < F: screens the put quote only.
    For K >= F: screens the call quote only.
    
    Parameters
    ----------
    df_tenor : pd.DataFrame
        Option chain records for a single maturity.
    F_parity : float
        Synthetic forward price for this maturity.
    min_bid : float
        Minimum own-side bid threshold (default: $0.05).
    max_rel_spread : float
        Maximum relative bid-ask spread threshold (Ask - Bid) / Mid <= 0.35.
        
    Returns
    -------
    df_otm : pd.DataFrame
        Sorted dataframe of retained liquid OTM contracts:
        ['strike', 'price', 'type', 'bid', 'ask', 'rel_spread']
    diagnostics : Dict[str, Any]
        Counts of evaluated, rejected, and retained contracts by reason.
    """
    diag: Dict[str, Any] = {
        "total_rows_evaluated": len(df_tenor),
        "retained_strikes": 0,
        "retained_puts": 0,
        "retained_calls": 0,
        "dropped_zero_or_subpenny_bid": 0,
        "dropped_crossed_or_zero_ask": 0,
        "dropped_excessive_spread": 0,
        "k_min": None,
        "k_max": None,
        "k_min_ratio": None,
        "k_max_ratio": None
    }
    
    retained_records = []
    
    for _, row in df_tenor.iterrows():
        K = row['STRIKE']
        if pd.isna(K) or K <= 0:
            continue
            
        if K < F_parity:
            # Out-of-the-money Put
            bid = row.get('P_BID', np.nan)
            ask = row.get('P_ASK', np.nan)
            opt_type = 'P'
        else:
            # Out-of-the-money Call
            bid = row.get('C_BID', np.nan)
            ask = row.get('C_ASK', np.nan)
            opt_type = 'C'
            
        if pd.isna(bid) or bid <= min_bid:
            diag["dropped_zero_or_subpenny_bid"] += 1
            continue
            
        if pd.isna(ask) or ask <= bid:
            diag["dropped_crossed_or_zero_ask"] += 1
            continue
            
        mid = 0.5 * (bid + ask)
        rel_spread = (ask - bid) / mid
        
        if rel_spread > max_rel_spread:
            diag["dropped_excessive_spread"] += 1
            continue
            
        retained_records.append({
            "strike": float(K),
            "price": float(mid),
            "type": opt_type,
            "bid": float(bid),
            "ask": float(ask),
            "rel_spread": float(rel_spread)
        })
        
    if not retained_records:
        return pd.DataFrame(columns=['strike', 'price', 'type', 'bid', 'ask', 'rel_spread']), diag
        
    df_otm = pd.DataFrame(retained_records).drop_duplicates(subset=['strike']).sort_values('strike').reset_index(drop=True)
    
    diag["retained_strikes"] = len(df_otm)
    diag["retained_puts"] = int((df_otm['type'] == 'P').sum())
    diag["retained_calls"] = int((df_otm['type'] == 'C').sum())
    diag["k_min"] = float(df_otm['strike'].iloc[0])
    diag["k_max"] = float(df_otm['strike'].iloc[-1])
    diag["k_min_ratio"] = float(diag["k_min"] / F_parity)
    diag["k_max_ratio"] = float(diag["k_max"] / F_parity)
    
    return df_otm, diag
