"""
Backtrader Custom Data Feed and Signal Bridge.
"""

from __future__ import annotations

from typing import Union
import pandas as pd
import pyarrow as pa


def to_backtrader(
    df_or_table: Union[pd.DataFrame, pa.Table],
) -> pd.DataFrame:
    """
    Format Kuwala data/signals into a Backtrader PandasData compatible DataFrame
    with standard datetime index and OHLCV columns.
    """
    if isinstance(df_or_table, pa.Table):
        df = df_or_table.to_pandas()
    else:
        df = df_or_table.copy()

    if "timestamp" in df.columns:
        df["datetime"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.set_index("datetime")
    elif not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, utc=True)

    required_cols = ["open", "high", "low", "close", "volume"]
    for col in required_cols:
        if col not in df.columns:
            if "mid" in df.columns:
                df[col] = df["mid"]
            elif "spot" in df.columns:
                df[col] = df["spot"]
            else:
                df[col] = 100.0

    return df
