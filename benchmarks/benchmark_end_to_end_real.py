"""
End-to-End Real Pipeline Benchmark: Data -> Clean -> IV -> SSVI -> Dupire -> VRP -> VectorBT.
=============================================================================================
"""

import time
import psutil
import os
import kuwala
from kuwala.data.adapters import YahooAdapter
from kuwala.data.pipeline import clean_chain
from kuwala.volatility.surface import SsviSurface
from kuwala.signals.vrp import vrp
from kuwala.backtest.vectorbt import to_vectorbt
from kuwala.data.store import get_store


def benchmark_end_to_end_real():
    print("=" * 70)
    print("  KUWALA END-TO-END REAL-DATA BENCHMARK (STAGE LATENCY BREAKDOWN)")
    print("=" * 70)

    process = psutil.Process(os.getpid())
    yahoo = YahooAdapter()
    store = get_store()

    t_total_start = time.perf_counter()

    # Stage 1: Data Ingestion
    t0 = time.perf_counter()
    raw_chain = yahoo.fetch("SPY")
    t_fetch = (time.perf_counter() - t0) * 1000

    # Stage 2: Data Cleaning & Normalization
    t0 = time.perf_counter()
    cleaned_chain = clean_chain(raw_chain)
    t_clean = (time.perf_counter() - t0) * 1000

    # Stage 3: SSVI Arbitrage-Free Calibration & Diagnostics
    t0 = time.perf_counter()
    surf = SsviSurface.calibrate(cleaned_chain)
    report = surf.diagnostics()
    t_calibrate = (time.perf_counter() - t0) * 1000

    # Stage 4: Dupire Local Volatility PDE Extraction
    t0 = time.perf_counter()
    loc_vol = surf.local_vol()
    t_dupire = (time.perf_counter() - t0) * 1000

    # Stage 5: Relative-Value Signal Generation (VRP)
    t0 = time.perf_counter()
    hist_df = yahoo.fetch_history("SPY")
    vrp_df = vrp(surf, hist_prices=hist_df, realized_window=20)
    t_signal = (time.perf_counter() - t0) * 1000

    # Stage 6: VectorBT Backtest Export
    t0 = time.perf_counter()
    vbt_out = to_vectorbt(vrp_df)
    t_backtest = (time.perf_counter() - t0) * 1000

    # Stage 7: Columnar Parquet + DuckDB Storage
    t0 = time.perf_counter()
    store.write_chain(cleaned_chain.to_dataframe())
    t_storage = (time.perf_counter() - t0) * 1000

    t_total = (time.perf_counter() - t_total_start) * 1000
    peak_mem = process.memory_info().rss / (1024 * 1024)

    print(f"Stage 1: Fetch Raw Options Data:          {t_fetch:>8.2f} ms")
    print(f"Stage 2: Clean & Microstructure Filter:   {t_clean:>8.2f} ms")
    print(f"Stage 3: SSVI Calibration & Diagnostics:  {t_calibrate:>8.2f} ms")
    print(f"Stage 4: Dupire Local Volatility PDE:     {t_dupire:>8.2f} ms")
    print(f"Stage 5: VRP Signal Computation:          {t_signal:>8.2f} ms")
    print(f"Stage 6: VectorBT Bridge Handoff:         {t_backtest:>8.2f} ms")
    print(f"Stage 7: DuckDB + Parquet Persistence:    {t_storage:>8.2f} ms")
    print("-" * 70)
    print(f"TOTAL END-TO-END PIPELINE LATENCY:       {t_total:>8.2f} ms")
    print(f"PEAK MEMORY FOOTPRINT:                   {peak_mem:>8.2f} MB")
    print("=" * 70)


if __name__ == "__main__":
    benchmark_end_to_end_real()
