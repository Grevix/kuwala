# Data Reconciliation Report: External Sources → DuckDB / Parquet

This report documents the exact end-to-end data reconciliation path for all external data sources integrated into Kuwala.

---

## 1. Complete Reconciliation Lifecycle

Every external data feed follows the immutable pipeline architecture:

```
EXTERNAL VENDOR SOURCE (Yahoo / FRED / SEC / Dukascopy / Nasdaq)
                           ↓ [Client-Side HTTP API Request]
                RAW VENDOR PAYLOAD (JSON / CSV / TSV)
                           ↓ [Adapter Parsing & Field Extraction]
              KUWALA CANONICAL MODELS (OptionChain / OptionQuote)
                           ↓ [Data Cleaning & Invariant Filtering]
                CLEANED & ENRICHED ARROW COLUMNAR TABLE
                           ↓ [Zero-Copy Partitioned Out-of-Core Serialization]
              PARQUET FILE PARTITION + DUCKDB ANALYTICAL STORE
                           ↓ [SQL Query / VectorBT Export]
                 VERIFIED MEMORY DATAFRAME RECONCILIATION
```

---

## 2. Invariant Reconciliation by Field

| Dimension | Raw Vendor Format | Kuwala Normalized Format | Arrow / DuckDB Storage | Reconciliation Status |
| :--- | :--- | :--- | :--- | :--- |
| **Timestamps** | Integer epoch seconds (Yahoo), UTC string (FRED, SEC), Millisecond epoch (Dukascopy) | Python `datetime.datetime` with `tz=timezone.utc` | `TIMESTAMPTZ` (Microsecond precision UTC) | **RECONCILED (0 Drift)** |
| **Strikes & Spots** | Float (Currency) | Standard IEEE 754 float64 | `DOUBLE` | **RECONCILED (Exact)** |
| **Moneyness / Log-Moneyness** | Not provided by vendor | $\ln(K / F)$ where $F = S e^{(r-q)T}$ | `DOUBLE` | **RECONCILED** |
| **Day-Count Fraction (TTM)** | Implicit / Calendar days | Standardized `ACT/365`, `ACT/360`, `30/360` | `DOUBLE` | **RECONCILED** |
| **Bid / Ask / Mid / Last** | Non-standard, crossed markets, missing bids | Filtered: $\text{bid} \le \text{ask}$, $\text{mid} = \frac{\text{bid} + \text{ask}}{2}$ | `DOUBLE` | **RECONCILED** |
| **Option Type** | String ("call", "put", "CALL", "C") | Typed Enum `OptionType.CALL` / `OptionType.PUT` | `VARCHAR` ("call" / "put") | **RECONCILED** |
| **Volume & Open Interest** | Nullable integer / missing | Int64 or `None` | `BIGINT` (Nullable) | **RECONCILED** |

---

## 3. Storage Roundtrip Verification

For every ticker chain tested across the platform:
- Row counts in memory match rows persisted in Parquet partitions exactly ($N_{\text{in}} = N_{\text{out}}$).
- Schema hashes match across Arrow, Parquet, and DuckDB tables.
- Zero silent mutation or type truncation detected.
