"""
historical_state.py
===================
Point-in-time calculation of historical market state features (X_t)
using strictly trailing daily S&P 500 cash closing index series:
1. Short-term return momentum (1-day log return)
2. Medium-term return momentum (5-day cumulative log return)
3. Short-term realized volatility (5-day RV)
4. Medium-term realized volatility (20-day RV)
5. Downside semivariance (20-day Downside SemiVar)
6. Trailing 20-day drawdown
"""

from typing import Dict, Any, Tuple, Optional
import os
import json
import datetime
import urllib.request
import numpy as np
import pandas as pd


def fetch_historical_spx_closes(
    cache_path: str = "output/stage4_features/spx_daily_closes.csv",
    start_date: str = "2019-11-01",
    end_date: str = "2020-03-15"
) -> pd.DataFrame:
    """
    Retrieves official daily S&P 500 cash closes (^GSPC) from Yahoo Finance,
    caching locally to ensure point-in-time reproducibility without recurring web requests.
    """
    if os.path.exists(cache_path):
        df_cached = pd.read_csv(cache_path)
        df_cached['date'] = df_cached['date'].astype(str)
        # Verify date range
        if df_cached['date'].min() <= start_date and df_cached['date'].max() >= end_date:
            return df_cached.sort_values('date').reset_index(drop=True)
            
    # Fetch from Yahoo Finance chart API
    p1 = int(datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    p2 = int(datetime.datetime.strptime(end_date, "%Y-%m-%d").timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?period1={p1}&period2={p2}&interval=1d"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        
    result = data['chart']['result'][0]
    timestamps = result['timestamp']
    closes = result['indicators']['quote'][0]['close']
    dates = [datetime.date.fromtimestamp(ts).strftime('%Y-%m-%d') for ts in timestamps]
    
    df = pd.DataFrame({'date': dates, 'close': closes}).dropna().sort_values('date').reset_index(drop=True)
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    df.to_csv(cache_path, index=False)
    
    return df


def compute_historical_features(
    df_closes: pd.DataFrame,
    target_date: str,
    window: int = 20
) -> Tuple[Optional[Dict[str, float]], Dict[str, Any]]:
    """
    Computes strictly trailing historical state vector X_t up to target_date.
    
    Parameters
    ----------
    df_closes : pd.DataFrame
        DataFrame with columns ['date', 'close'].
    target_date : str
        Observation date 'YYYY-MM-DD'.
    window : int
        Lookback window in trading days (default: 20).
        
    Returns
    -------
    features : Dict[str, float] or None
        Dict with keys: r_1d, r_5d, rv_5d, rv_20d, dsemi_20d, dd_20d.
    diagnostics : Dict[str, Any]
        Details on available history and trailing dates used.
    """
    diag: Dict[str, Any] = {
        "target_date": target_date,
        "status": "FAILED",
        "trailing_sessions_count": 0,
        "available_history_start": None,
        "available_history_end": None,
        "failure_reason": None
    }
    
    df = df_closes.copy().sort_values('date').reset_index(drop=True)
    
    # Filter strictly up to target_date (point-in-time constraint: s <= t)
    df_past = df[df['date'] <= target_date].reset_index(drop=True)
    
    if df_past.empty:
        diag["failure_reason"] = f"No historical prices available on or before {target_date}"
        return None, diag
        
    if df_past['date'].iloc[-1] != target_date:
        diag["failure_reason"] = f"Target date {target_date} is not present in closing series (latest: {df_past['date'].iloc[-1]})"
        return None, diag
        
    # We require window daily returns, which needs window + 1 closing prices
    required_prices = window + 1
    if len(df_past) < required_prices:
        diag["failure_reason"] = f"Insufficient history: have {len(df_past)} sessions, require {required_prices} for 20-day window"
        return None, diag
        
    sub = df_past.iloc[-required_prices:].copy().reset_index(drop=True)
    sub['log_ret'] = np.log(sub['close'] / sub['close'].shift(1))
    
    # Exactly window returns: r_{t-19} to r_t
    returns_window = sub['log_ret'].iloc[1:].values
    closes_window = sub['close'].iloc[1:].values  # S_{t-19} to S_t
    
    diag["trailing_sessions_count"] = len(returns_window)
    diag["available_history_start"] = str(sub['date'].iloc[1])
    diag["available_history_end"] = str(sub['date'].iloc[-1])
    
    # 1. 1-day return
    r_1d = float(returns_window[-1])
    
    # 2. 5-day cumulative return
    r_5d = float(np.sum(returns_window[-5:]))
    
    # 3. 5-day realized volatility (annualized, 252 days)
    rv_5d = float(np.sqrt((252.0 / 5.0) * np.sum(returns_window[-5:] ** 2)))
    
    # 4. 20-day realized volatility (annualized, 252 days)
    rv_20d = float(np.sqrt((252.0 / 20.0) * np.sum(returns_window ** 2)))
    
    # 5. 20-day downside semivariance (annualized, strictly negative daily returns)
    neg_rets = np.minimum(returns_window, 0.0)
    dsemi_20d = float(np.sqrt((252.0 / 20.0) * np.sum(neg_rets ** 2)))
    
    # 6. Trailing 20-day drawdown relative to trailing peak
    peak_close = float(np.max(closes_window))
    current_close = float(closes_window[-1])
    dd_20d = float((current_close - peak_close) / peak_close)
    
    features = {
        "S_t": current_close,
        "r_1d": r_1d,
        "r_5d": r_5d,
        "rv_5d": rv_5d,
        "rv_20d": rv_20d,
        "dsemi_20d": dsemi_20d,
        "dd_20d": dd_20d
    }
    
    diag["status"] = "SUCCESS"
    diag["S_t"] = current_close
    diag["peak_20d"] = peak_close
    
    return features, diag
