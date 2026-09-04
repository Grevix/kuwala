"""
Unit Tests for High-Frequency Tick-to-OHLCV Aggregator.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from kuwala.data.microstructure import aggregate_ticks_to_bars


def test_aggregate_ticks_to_bars_basic():
    timestamps = pd.date_range("2024-01-02 09:30:00", periods=60, freq="1s", tz="UTC")
    prices = 100.0 + np.cumsum(np.random.choice([-0.01, 0.0, 0.01], size=60))
    volumes = np.random.randint(10, 100, size=60)
    bids = prices - 0.01
    asks = prices + 0.01

    df_ticks = pd.DataFrame(
        {
            "timestamp": timestamps,
            "price": prices,
            "volume": volumes,
            "bid": bids,
            "ask": asks,
        }
    )

    bars = aggregate_ticks_to_bars(df_ticks, freq="1min", tz="UTC")
    assert len(bars) == 1

    bar = bars.iloc[0]
    assert bar["open"] == prices[0]
    assert bar["close"] == prices[-1]
    assert bar["high"] == np.max(prices)
    assert bar["low"] == np.min(prices)
    assert bar["volume"] == np.sum(volumes)
    assert bar["trades"] == 60
    assert bar["low"] <= bar["vwap"] <= bar["high"]
    assert bar["buy_volume"] + bar["sell_volume"] <= bar["volume"]


def test_aggregate_ticks_empty():
    empty_df = pd.DataFrame(columns=["timestamp", "price", "volume"])
    bars = aggregate_ticks_to_bars(empty_df, freq="1min")
    assert bars.empty
