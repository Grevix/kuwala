"""
Real-Data Benchmark: Data Fetching, Normalization & DuckDB Out-of-Core Storage.
==============================================================================
"""

import time

from kuwala.data.adapters import YahooAdapter
from kuwala.data.pipeline import clean_chain
from kuwala.data.store import get_store


def benchmark_real_data_pipeline():
    print("=" * 65)
    print("  KUWALA REAL-DATA BENCHMARK: DATA PIPELINE & STORAGE")
    print("=" * 65)

    yahoo = YahooAdapter()
    store = get_store()
    tickers = ["SPY", "QQQ", "AAPL", "MSFT"]

    total_quotes = 0
    t0 = time.perf_counter()

    for sym in tickers:
        chain = yahoo.fetch(sym)
        cleaned = clean_chain(chain)
        store.write_chain(cleaned.to_dataframe())
        total_quotes += len(cleaned)

    elapsed = time.perf_counter() - t0
    print(
        f"Tickers Processed: {len(tickers)} | Total Quotes: {total_quotes:,} | Time: {elapsed:.2f} s | Storage Throughput: {total_quotes / elapsed:,.0f} quotes/sec"
    )
    print("=" * 65)


if __name__ == "__main__":
    benchmark_real_data_pipeline()
