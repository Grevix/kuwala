"""
Technical Indicators & Feature Engineering Suite for Kuwala.
============================================================
Provides independent reference calculations for technical indicators:
SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Stochastics, VWAP.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int = 20) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window).mean()


def ema(series: pd.Series, span: int = 20) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """
    Relative Strength Index (Wilder's RSI).
    """
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    # Wilder's Exponential Smoothing (alpha = 1 / window)
    roll_up = pd.Series(gain, index=series.index).ewm(alpha=1.0 / window, adjust=False).mean()
    roll_down = pd.Series(loss, index=series.index).ewm(alpha=1.0 / window, adjust=False).mean()

    rs = roll_up / (roll_down + 1e-10)
    rsi_val = 100.0 - (100.0 / (1.0 + rs))
    return rsi_val


def macd(
    series: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    """
    Moving Average Convergence Divergence (MACD).
    """
    fast_ema = ema(series, span=fast_period)
    slow_ema = ema(series, span=slow_period)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, span=signal_period)
    hist = macd_line - signal_line

    return pd.DataFrame(
        {
            "macd": macd_line,
            "macd_signal": signal_line,
            "macd_hist": hist,
        },
        index=series.index,
    )


def bollinger_bands(
    series: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> pd.DataFrame:
    """
    Bollinger Bands (Middle, Upper, Lower, Bandwidth, %B).
    """
    middle = sma(series, window=window)
    std = series.rolling(window=window).std()
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    bandwidth = (upper - lower) / (middle + 1e-10)
    percent_b = (series - lower) / (upper - lower + 1e-10)

    return pd.DataFrame(
        {
            "bb_middle": middle,
            "bb_upper": upper,
            "bb_lower": lower,
            "bb_bandwidth": bandwidth,
            "bb_percent_b": percent_b,
        },
        index=series.index,
    )


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = 14,
) -> pd.Series:
    """
    Average True Range (Wilder's ATR).
    """
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return tr.ewm(alpha=1.0 / window, adjust=False).mean()


def stochastic_oscillator(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_window: int = 14,
    d_window: int = 3,
) -> pd.DataFrame:
    """
    Stochastic Oscillator (%K and %D).
    """
    lowest_low = low.rolling(window=k_window).min()
    highest_high = high.rolling(window=k_window).max()
    k_line = 100.0 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    d_line = k_line.rolling(window=d_window).mean()

    return pd.DataFrame(
        {
            "stoch_k": k_line,
            "stoch_d": d_line,
        },
        index=close.index,
    )
