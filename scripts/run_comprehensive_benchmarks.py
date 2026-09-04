"""
Comprehensive Cross-Language Benchmark Harness: Python vs Rust vs C++.
Evaluates Black-Scholes, Greeks, Implied Volatility, and Microstructure Aggregation.
Outputs raw JSON metrics and benchmark tables.
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd

from kuwala.data.microstructure import aggregate_ticks_to_bars
from kuwala.pricing import black_scholes, greeks
from kuwala.volatility import implied_volatility


def benchmark_python_and_rust():
    np.random.seed(42)
    sizes = [10000, 100000, 1000000]

    results = {
        "hardware": {
            "os": "Windows 11 (x86_64)",
            "python": sys.version.split()[0],
            "rustc": "1.85.0+",
            "msvc": "19.44 (Visual Studio 2022)",
        },
        "benchmarks": {},
    }

    print("=== [BENCHMARK] Python / Rust Benchmarks ===")

    # 1. Black-Scholes
    bs_bench = {}
    for n in sizes:
        spots = np.random.uniform(50.0, 300.0, n)
        strikes = np.random.uniform(50.0, 300.0, n)
        ttms = np.random.uniform(0.05, 3.0, n)
        rates = np.random.uniform(0.01, 0.06, n)
        divs = np.random.uniform(0.0, 0.03, n)
        vols = np.random.uniform(0.10, 0.90, n)

        # Warmup
        _ = black_scholes(spots[0], strikes[0], ttms[0], rates[0], divs[0], vols[0], True)

        t0 = time.perf_counter()
        for i in range(n):
            _ = black_scholes(spots[i], strikes[i], ttms[i], rates[i], divs[i], vols[i], True)
        t1 = time.perf_counter()
        dur = t1 - t0
        ops = n / dur
        bs_bench[str(n)] = {"duration_sec": dur, "throughput_ops_sec": ops}
        print(f"  BS N={n:7d} | Time: {dur:6.4f}s | Throughput: {ops:10.0f} ops/s")
    results["benchmarks"]["black_scholes_rust"] = bs_bench

    # 2. Greeks
    gk_bench = {}
    for n in [10000, 100000, 1000000]:
        spots = np.random.uniform(50.0, 300.0, n)
        strikes = np.random.uniform(50.0, 300.0, n)
        ttms = np.random.uniform(0.05, 3.0, n)
        rates = np.random.uniform(0.01, 0.06, n)
        divs = np.random.uniform(0.0, 0.03, n)
        vols = np.random.uniform(0.10, 0.90, n)

        t0 = time.perf_counter()
        for i in range(n):
            _ = greeks(spots[i], strikes[i], ttms[i], rates[i], divs[i], vols[i], True)
        t1 = time.perf_counter()
        dur = t1 - t0
        ops = n / dur
        gk_bench[str(n)] = {"duration_sec": dur, "throughput_ops_sec": ops}
        print(f"  Greeks N={n:7d} | Time: {dur:6.4f}s | Throughput: {ops:10.0f} ops/s")
    results["benchmarks"]["greeks_rust"] = gk_bench

    # 3. Implied Volatility
    iv_bench = {}
    for n in [10000, 100000, 500000]:
        spots = np.random.uniform(50.0, 300.0, n)
        strikes = np.random.uniform(50.0, 300.0, n)
        ttms = np.random.uniform(0.05, 3.0, n)
        rates = np.random.uniform(0.01, 0.06, n)
        divs = np.random.uniform(0.0, 0.03, n)
        vols = np.random.uniform(0.10, 0.90, n)
        prices = [black_scholes(spots[i], strikes[i], ttms[i], rates[i], divs[i], vols[i], True) for i in range(n)]

        t0 = time.perf_counter()
        for i in range(n):
            _ = implied_volatility(prices[i], spots[i], strikes[i], ttms[i], rates[i], divs[i], True)
        t1 = time.perf_counter()
        dur = t1 - t0
        ops = n / dur
        iv_bench[str(n)] = {"duration_sec": dur, "throughput_ops_sec": ops}
        print(f"  IV N={n:7d} | Time: {dur:6.4f}s | Throughput: {ops:10.0f} ops/s")
    results["benchmarks"]["iv_solver_rust"] = iv_bench

    # 4. Microstructure Tick Aggregation
    tick_bench = {}
    for n in [100000, 1000000]:
        t0_ts = pd.Timestamp("2026-09-01 09:30:00", tz="UTC")
        timestamps = [t0_ts + pd.Timedelta(milliseconds=i * 10) for i in range(n)]
        prices = 150.0 + np.cumsum(np.random.normal(0, 0.02, n))
        volumes = np.random.randint(10, 500, n)
        bids = prices - 0.01
        asks = prices + 0.01

        df_ticks = pd.DataFrame({"timestamp": timestamps, "price": prices, "volume": volumes, "bid": bids, "ask": asks})

        t_start = time.perf_counter()
        bars = aggregate_ticks_to_bars(df_ticks, freq="1m")
        t_end = time.perf_counter()
        dur = t_end - t_start
        ops = n / dur
        tick_bench[str(n)] = {"duration_sec": dur, "bars_generated": len(bars), "throughput_ticks_sec": ops}
        print(f"  Ticks N={n:7d} | Time: {dur:6.4f}s | Throughput: {ops:10.0f} ticks/s")
    results["benchmarks"]["microstructure_python_arrow"] = tick_bench

    os.makedirs("benchmarks/results/raw", exist_ok=True)
    with open("benchmarks/results/raw/python_rust_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Saved benchmark metrics to benchmarks/results/raw/python_rust_benchmark_results.json")


if __name__ == "__main__":
    benchmark_python_and_rust()
