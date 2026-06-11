"""
volatility_targeting.py
=======================
Reusable utilities for the Volatility Targeting strategy.
"""

import numpy as np
import pandas as pd
import yfinance as yf


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def fetch_prices(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download OHLCV from yfinance and return a clean daily returns DataFrame."""
    raw = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    raw.columns = [c.lower() for c in raw.columns]
    df = pd.DataFrame()
    df['close']  = raw['close']
    df['return'] = df['close'].pct_change()
    return df.dropna()


# ---------------------------------------------------------------------------
# Signal & Strategy
# ---------------------------------------------------------------------------

def momentum_signal(prices: pd.Series, lookback: int) -> pd.Series:
    """Return +1 (long) or 0 (flat) based on lookback-day return sign."""
    sig = np.sign(prices.pct_change(lookback))
    return sig.replace(0, np.nan).ffill().fillna(0)


def vol_targeting_returns(
    returns: pd.Series,
    signal: pd.Series,
    target_vol: float = 0.15,
    vol_window: int = 20,
    vol_cap: float = 2.0,
) -> pd.DataFrame:
    """
    Apply volatility targeting overlay on top of a position signal.

    Parameters
    ----------
    returns     : daily return series
    signal      : position signal (+1 / 0 / -1)
    target_vol  : annualised target volatility
    vol_window  : rolling window for realised vol estimate
    vol_cap     : maximum allowed vol scalar (leverage cap)

    Returns
    -------
    DataFrame with columns: realised_vol, vol_scalar, vt_position,
                             mom_return, vt_return
    """
    df = pd.DataFrame({'return': returns, 'signal': signal})
    df['realised_vol'] = df['return'].rolling(vol_window).std() * np.sqrt(252)
    df['vol_scalar']   = (target_vol / df['realised_vol']).clip(upper=vol_cap)
    df['vt_position']  = df['signal'] * df['vol_scalar']
    df['mom_return']   = df['signal'].shift(1) * df['return']
    df['vt_return']    = df['vt_position'].shift(1) * df['return']
    return df.dropna()


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def performance_metrics(returns: pd.Series) -> dict:
    """Return dict of annualised return, vol, Sharpe, max drawdown, Calmar."""
    ann_ret = returns.mean() * 252
    ann_vol = returns.std() * np.sqrt(252)
    sharpe  = ann_ret / ann_vol if ann_vol > 0 else np.nan
    cum     = (1 + returns).cumprod()
    max_dd  = ((cum - cum.cummax()) / cum.cummax()).min()
    calmar  = ann_ret / abs(max_dd) if max_dd != 0 else np.nan
    return {
        'ann_return': ann_ret,
        'ann_vol':    ann_vol,
        'sharpe':     sharpe,
        'max_dd':     max_dd,
        'calmar':     calmar,
    }


def lookback_sensitivity(
    prices: pd.Series,
    returns: pd.Series,
    windows: list = [10, 20, 60],
    target_vol: float = 0.15,
    vol_cap: float = 2.0,
) -> pd.DataFrame:
    """
    Run vol targeting across multiple lookback windows and return a
    summary DataFrame.
    """
    rows = []
    for w in windows:
        sig = momentum_signal(prices, w)
        df  = vol_targeting_returns(returns, sig, target_vol, w, vol_cap)
        m   = performance_metrics(df['vt_return'])
        rows.append({'window': f'{w}-day', **m})
    return pd.DataFrame(rows)
