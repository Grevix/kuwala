"""
Microstructure & High-Frequency Tick-to-Bar Aggregation Engine.
Resamples raw trade/quote ticks into standardized OHLCV bars with VWAP and tick-rule order flow.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def aggregate_ticks_to_bars(
    ticks: pd.DataFrame,
    freq: str = "1min",
    tz: str = "UTC",
    price_col: str = "price",
    volume_col: str = "volume",
    time_col: str = "timestamp",
    bid_col: str | None = "bid",
    ask_col: str | None = "ask",
) -> pd.DataFrame:
    """
    Aggregate raw trade ticks into standardized OHLCV bars with microstructure metrics:
    - Open, High, Low, Close
    - Volume & Trade Count
    - Volume-Weighted Average Price (VWAP)
    - Buy Volume & Sell Volume (classified via Lee-Ready tick rule)
    - Effective Spread (if bid/ask provided)
    """
    if ticks.empty:
        return pd.DataFrame(
            columns=["open", "high", "low", "close", "volume", "vwap", "trades", "buy_volume", "sell_volume"]
        )

    df = ticks.copy()

    # Ensure timestamp is datetime and UTC-localized
    if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
        df[time_col] = pd.to_datetime(df[time_col], utc=True)
    elif df[time_col].dt.tz is None:
        df[time_col] = df[time_col].dt.tz_localize("UTC")
    else:
        df[time_col] = df[time_col].dt.tz_convert(tz)

    df = df.sort_values(time_col).reset_index(drop=True)

    # Classify buy / sell trades using tick rule
    price_diff = df[price_col].diff().fillna(0)
    direction = np.sign(price_diff)
    direction = direction.replace(0, np.nan).ffill().fillna(1.0)

    df["buy_vol"] = np.where(direction > 0, df[volume_col], 0.0)
    df["sell_vol"] = np.where(direction < 0, df[volume_col], 0.0)
    df["pv"] = df[price_col] * df[volume_col]

    has_spread = False
    if bid_col and ask_col and bid_col in df.columns and ask_col in df.columns:
        df["spread"] = (df[ask_col] - df[bid_col]).clip(lower=0.0)
        has_spread = True

    # Resample
    df = df.set_index(time_col)
    resampler = df.resample(freq)

    bars = pd.DataFrame()
    bars["open"] = resampler[price_col].first()
    bars["high"] = resampler[price_col].max()
    bars["low"] = resampler[price_col].min()
    bars["close"] = resampler[price_col].last()
    bars["volume"] = resampler[volume_col].sum()
    bars["trades"] = resampler[price_col].count()

    # VWAP
    pv_sum = resampler["pv"].sum()
    vol_sum = bars["volume"]
    bars["vwap"] = np.where(vol_sum > 0, pv_sum / vol_sum, bars["close"])

    bars["buy_volume"] = resampler["buy_vol"].sum()
    bars["sell_volume"] = resampler["sell_vol"].sum()

    if has_spread:
        bars["spread_mean"] = resampler["spread"].mean()

    # Drop empty bars
    bars = bars.dropna(subset=["close"]).reset_index()
    return bars
