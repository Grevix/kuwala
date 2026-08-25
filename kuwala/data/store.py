"""
Embedded DuckDB + Apache Arrow / Parquet Storage Engine for Kuwala.
"""

from __future__ import annotations

import re
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
        self.conn = duckdb.connect(str(self.db_file))
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS options_chains (
                underlying VARCHAR,
                timestamp TIMESTAMPTZ,
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
                spot DOUBLE,
                rate DOUBLE,
                dividend_yield DOUBLE,
                ttm DOUBLE,
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

    def write_chain(self, df_or_table: Union[pd.DataFrame, pa.Table]) -> int:
        """
        Store option chain observations into DuckDB and persist to Parquet partition.
        """
        if isinstance(df_or_table, pa.Table):
            df = df_or_table.to_pandas()
        else:
            df = df_or_table.copy()

        if df.empty:
            return 0

        self.conn.register("tmp_incoming_chain", df)
        self.conn.execute("""
            INSERT INTO options_chains
            SELECT
                underlying, timestamp, expiry, strike, option_type,
                bid, ask, mid, last, volume, open_interest, implied_volatility,
                spot, rate, dividend_yield, ttm, log_moneyness
            FROM tmp_incoming_chain
        """)
        self.conn.unregister("tmp_incoming_chain")

        # Sanitize underlying for directory name
        raw_symbol = str(df["underlying"].iloc[0])
        safe_symbol = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_symbol)

        parquet_dir = self.base_dir / "parquet" / f"underlying={safe_symbol}"
        parquet_dir.mkdir(parents=True, exist_ok=True)
        date_str = pd.to_datetime(df["timestamp"].iloc[0]).strftime("%Y%m%d_%H%M%S")
        file_path = parquet_dir / f"chain_{date_str}.parquet"

        table = pa.Table.from_pandas(df)
        pq.write_table(table, file_path)
        return len(df)

    def query(self, sql: str, params: Optional[List[Any]] = None) -> pd.DataFrame:
        """
        Execute an arbitrary SQL query against the DuckDB store with optional parameters.
        """
        if params is not None:
            return self.conn.execute(sql, params).fetchdf()
        return self.conn.execute(sql).fetchdf()

    def get_latest_chain(self, underlying: str) -> pd.DataFrame:
        query = """
            SELECT * FROM options_chains
            WHERE underlying = ?
            AND timestamp = (SELECT MAX(timestamp) FROM options_chains WHERE underlying = ?)
        """
        return self.query(query, [underlying, underlying])

    def close(self) -> None:
        self.conn.close()


_DEFAULT_STORE: Optional[DataStore] = None


def get_store() -> DataStore:
    global _DEFAULT_STORE
    if _DEFAULT_STORE is None:
        _DEFAULT_STORE = DataStore()
    return _DEFAULT_STORE
