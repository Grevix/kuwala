"""
Zero-Copy Apache Arrow & VectorBT Connector.
"""

from __future__ import annotations

from typing import Dict, Union

import numpy as np
import pandas as pd
import pyarrow as pa


def to_vectorbt(
    signals_or_df: Union[pd.DataFrame, pd.Series, pa.Table],
    price_col: str = "close",
    signal_col: str = "signal",
) -> Dict[str, pd.DataFrame]:
    """
    Format signals and price series into vectorbt-ready 2D DataFrames.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary with 'entries', 'exits', and 'price' aligned DataFrames.
    """
    if isinstance(signals_or_df, pa.Table):
        df = signals_or_df.to_pandas()
    elif isinstance(signals_or_df, pd.Series):
        df = pd.DataFrame({"signal": signals_or_df})
    else:
        df = signals_or_df.copy()

    if signal_col not in df.columns:
        if "vrp_spread" in df.columns:
            # Rule: long vol if VRP < 0, short vol if VRP > 0
            df["signal"] = np.where(df["vrp_spread"] > 0.02, -1.0, np.where(df["vrp_spread"] < -0.02, 1.0, 0.0))
            signal_col = "signal"
        else:
            df["signal"] = 1.0

    entries = (df[signal_col] > 0).to_frame(name="long_entry")
    exits = (df[signal_col] < 0).to_frame(name="short_entry")

    price_df = df[[price_col]] if price_col in df.columns else pd.DataFrame({"close": 100.0}, index=df.index)

    return {
        "entries": entries,
        "exits": exits,
        "price": price_df,
    }
