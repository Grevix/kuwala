"""
Unit Tests for Out-of-Core Partitioned Parquet Storage and DuckDB Hive Partitioning.
"""

from __future__ import annotations

import tempfile

import numpy as np
import pandas as pd

from kuwala.data.store import DataStore


def test_partitioned_bars_storage_and_query():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(db_path=f"{tmpdir}/test_store.duckdb")

        # Create multi-month bar dataset
        dates = pd.date_range("2024-01-01", "2024-04-30", freq="1D", tz="UTC")
        prices = 100.0 + np.cumsum(np.random.normal(0, 1, size=len(dates)))
        df_bars = pd.DataFrame(
            {
                "timestamp": dates,
                "open": prices,
                "high": prices + 1.0,
                "low": prices - 1.0,
                "close": prices + 0.2,
                "volume": 10000.0,
                "vwap": prices + 0.1,
                "trades": 500,
            }
        )

        n_written = store.write_partitioned_bars(df_bars, underlying="SPY", freq="1d")
        assert n_written == len(df_bars)

        # Query across partitioned Parquet via DuckDB
        parquet_glob = f"{store.parquet_dir}/bars/underlying=SPY/*/*/*.parquet".replace("\\", "/")
        queried_df = store.query(
            f"SELECT count(*) as cnt, avg(close) as avg_px FROM read_parquet('{parquet_glob}', hive_partitioning=1)"
        )
        assert queried_df["cnt"].iloc[0] == len(df_bars)
        assert queried_df["avg_px"].iloc[0] > 0.0

        store.close()
