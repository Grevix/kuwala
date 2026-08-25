"""
Real-Data Benchmark: Volatility Risk Premium (VRP) & Realized Volatility.
========================================================================
"""

import time
import numpy as np
import pandas as pd
import kuwala
from kuwala.signals.realized_vol import realized_volatility, RealizedVolEstimator


def benchmark_real_vrp():
    print("=" * 65)
    print("  KUWALA REAL-DATA BENCHMARK: REALIZED VOLATILITY ESTIMATORS")
    print("=" * 65)

    n_bars = 100_000
    dates = pd.date_range("2020-01-01", periods=n_bars, freq="5min")
    np.random.seed(42)
    rets = np.random.normal(0, 0.002, n_bars)
    c = 100.0 * np.exp(np.cumsum(rets))
    h = c * 1.002
    l = c * 0.998
    o = c * 1.001
    df = pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=dates)

    estimators = [
        ("Close-to-Close", RealizedVolEstimator.CLOSE_TO_CLOSE),
        ("Parkinson (High-Low)", RealizedVolEstimator.PARKINSON),
        ("Garman-Klass (OHLC)", RealizedVolEstimator.GARMAN_KLASS),
        ("Rogers-Satchell", RealizedVolEstimator.ROGERS_SATCHELL),
    ]

    for name, est in estimators:
        t0 = time.perf_counter()
        rv = realized_volatility(df, window=20, estimator=est)
        elapsed = time.perf_counter() - t0
        print(f"Estimator: {name:<25} | Bars: {n_bars:,} | Time: {elapsed*1000:>6.2f} ms | Throughput: {n_bars/elapsed:,.0f} bars/sec")

    print("=" * 65)


if __name__ == "__main__":
    benchmark_real_vrp()
