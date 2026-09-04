"""
Embedded DuckDB + Apache Arrow / Parquet Storage Engine for Kuwala.
Supports Hive-partitioned out-of-core columnar storage and high-throughput analytical queries.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Union

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from kuwala.config import get_config


class DataStore:
    """
    Embedded columnar data store providing out-of-core persistence and querying
    via DuckDB and Apache Arrow / Parquet.
    """

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        if db_path is None:
            config = get_config()
            self.base_dir = config.data_dir
            self.db_file = self.base_dir / "kuwala_analytics.duckdb"
        else:
            self.db_file = Path(db_path)
            self.base_dir = self.db_file.parent

        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.parquet_dir = self.base_dir / "partitioned"
        self.parquet_dir.mkdir(parents=True, exist_ok=True)

        self.conn = duckdb.connect(str(self.db_file))
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS options_chains (
                underlying VARCHAR,
                expiry TIMESTAMPTZ,
                strike DOUBLE,
                option_type VARCHAR,
                bid DOUBLE,
                ask DOUBLE,
                mid DOUBLE,
                last DOUBLE,
                volume BIGINT,
                open_interest BIGINT,
                implied_volatility DOUBLE,
                timestamp TIMESTAMPTZ,
                spot DOUBLE,
                rate DOUBLE,
                dividend_yield DOUBLE,
                ttm DOUBLE,
                moneyness DOUBLE,
                log_moneyness DOUBLE
            );
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS macro_series (
                series_id VARCHAR,
                date DATE,
                value DOUBLE,
                source VARCHAR,
                last_updated TIMESTAMPTZ
            );
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bars (
                underlying VARCHAR,
                timestamp TIMESTAMPTZ,
                freq VARCHAR,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume DOUBLE,
                vwap DOUBLE,
                trades BIGINT
            );
        """)

    def write_chain(self, df_or_table: Union[pd.DataFrame, pa.Table]) -> int:
        """Append an option chain dataset into DuckDB."""
        if isinstance(df_or_table, pd.DataFrame):
            df = df_or_table.copy()
        else:
            df = df_or_table.to_pandas()

        if df.empty:
            return 0

        self.conn.register("df_chain_view", df)
        self.conn.execute("INSERT INTO options_chains BY NAME SELECT * FROM df_chain_view;")
        self.conn.unregister("df_chain_view")
        return len(df)

    def write_partitioned_bars(self, df: pd.DataFrame, underlying: str, freq: str = "1d") -> int:
        """
        Write bars into Hive-partitioned Parquet files:
        storage/partitioned/bars/underlying={underlying}/year={YYYY}/month={MM}/data.parquet
        """
        if df.empty:
            return 0

        df_copy = df.copy()
        if "timestamp" in df_copy.columns:
            ts_col = "timestamp"
        elif "date" in df_copy.columns:
            ts_col = "date"
        else:
            ts_col = df_copy.columns[0]

        df_copy[ts_col] = pd.to_datetime(df_copy[ts_col], utc=True)
        df_copy["underlying"] = underlying
        df_copy["freq"] = freq
        df_copy["year"] = df_copy[ts_col].dt.year
        df_copy["month"] = df_copy[ts_col].dt.month

        table = pa.Table.from_pandas(df_copy)
        pq.write_to_dataset(
            table,
            root_path=str(self.parquet_dir / "bars"),
            partition_cols=["underlying", "year", "month"],
            use_dictionary=True,
            compression="zstd",
        )
        return len(df)

    def write_partitioned_chains(self, df_or_table: Union[pd.DataFrame, pa.Table], underlying: str) -> int:
        """
        Write option contract quotes into Hive-partitioned Parquet hierarchy.
        """
        if isinstance(df_or_table, pd.DataFrame):
            df = df_or_table.copy()
        else:
            df = df_or_table.to_pandas()

        if df.empty:
            return 0

        if "timestamp" in df.columns:
            ts = pd.to_datetime(df["timestamp"], utc=True)
        else:
            ts = pd.Timestamp.now(tz="UTC")
            df["timestamp"] = ts

        df["underlying"] = underlying
        df["year"] = ts.dt.year if isinstance(ts, pd.Series) else ts.year
        df["month"] = ts.dt.month if isinstance(ts, pd.Series) else ts.month

        table = pa.Table.from_pandas(df)
        pq.write_to_dataset(
            table,
            root_path=str(self.parquet_dir / "options"),
            partition_cols=["underlying", "year", "month"],
            use_dictionary=True,
            compression="zstd",
        )
        return len(df)

    def query(self, sql: str, params: Optional[List[Any]] = None) -> pd.DataFrame:
        """Execute parameterized SQL query in DuckDB."""
        if params is not None:
            return self.conn.execute(sql, params).df()
        return self.conn.execute(sql).df()

    def get_latest_chain(self, underlying: str) -> pd.DataFrame:
        """Fetch latest option chain safely using parameterized query."""
        sql = """
            SELECT * FROM options_chains
            WHERE underlying = ?
            ORDER BY timestamp DESC, expiry ASC, strike ASC;
        """
        return self.conn.execute(sql, [underlying]).df()

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
