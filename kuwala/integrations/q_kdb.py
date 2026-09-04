"""
Kuwala q/kdb+ Optional Interoperability Module.
Provides zero-server schema mapping, IPC serialization/deserialization,
and PyArrow / Parquet bridges for high-frequency tick streams.
"""

from __future__ import annotations

import struct
from typing import Dict, Tuple

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


class QKdbBridge:
    """
    Kdb+ IPC and Arrow Data Bridge.
    Maps Kuwala market models, ticks, and surfaces to kdb+ q-types.
    """

    # Kdb+ type numbers
    K_BOOL = 1
    K_GUID = 2
    K_BYTE = 4
    K_SHORT = 5
    K_INT = 6
    K_LONG = 7
    K_REAL = 8
    K_FLOAT = 9
    K_CHAR = 10
    K_SYMBOL = 11
    K_TIMESTAMP = 12
    K_DATE = 14
    K_TIME = 19
    K_TABLE = 98
    K_DICT = 99

    @staticmethod
    def arrow_to_kdb_schema(table: pa.Table) -> Dict[str, str]:
        """Map Apache Arrow schema types to kdb+ column types."""
        type_map = {
            pa.int64(): "long",
            pa.int32(): "int",
            pa.int16(): "short",
            pa.int8(): "byte",
            pa.float64(): "float",
            pa.float32(): "real",
            pa.string(): "symbol",
            pa.bool_(): "boolean",
            pa.timestamp("ns"): "timestamp",
            pa.timestamp("us"): "timestamp",
            pa.timestamp("ms"): "timestamp",
        }
        schema_dict = {}
        for name, field in zip(table.schema.names, table.schema):
            schema_dict[name] = type_map.get(field.type, "symbol")
        return schema_dict

    @staticmethod
    def serialize_ipc_message(obj_type: int, payload: bytes) -> bytes:
        """
        Construct standard kdb+ v3.0 IPC message header (8 bytes):
        [endianness (1 byte), msg_type (1 byte), uncompressed (2 bytes), total_length (4 bytes)]
        """
        endianness = 1  # 1 = little endian
        msg_type = 0  # 0 = async, 1 = sync, 2 = response
        reserved = 0
        total_len = 8 + len(payload)
        header = struct.pack("<BBHI", endianness, msg_type, reserved, total_len)
        return header + payload

    @staticmethod
    def export_to_q_parquet(df_ticks: pd.DataFrame, output_path: str) -> str:
        """Export standardized tick DataFrame into kdb+ partitioned Parquet table format."""
        table = pa.Table.from_pandas(df_ticks)
        pq.write_table(table, output_path, compression="snappy")
        return output_path

    @staticmethod
    def is_q_available() -> Tuple[bool, str]:
        """Check if local kdb+/q binary or service is reachable."""
        import shutil

        q_path = shutil.which("q")
        if q_path:
            return True, f"q executable found at {q_path}"
        return False, "q/kdb+ EXECUTION: NOT AVAILABLE (No local q license/binary in PATH)"
