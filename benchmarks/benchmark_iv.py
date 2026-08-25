"""
Reproducible Implied Volatility Benchmark Suite.
"""

import time
import platform
import numpy as np
import kuwala

def run_benchmark():
    print("==========================================================")
    print("  KUWALA REPRODUCIBLE BENCHMARK: IMPLIED VOLATILITY")
    print("==========================================================")
    print(f"System: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python: {platform.python_version()}")
    print("----------------------------------------------------------")

    N = 10_000
    np.random.seed(42)
    spots = np.full(N, 100.0)
    strikes = np.random.uniform(80.0, 120.0, N)
    ttms = np.random.uniform(0.1, 2.0, N)
    vols = np.random.uniform(0.10, 0.60, N)
    r = 0.04
    q = 0.01

    prices = kuwala.black_scholes(spots, strikes, ttms, r, q, vols, is_call=True)

    # Measure Kuwala IV solver throughput
    t0 = time.perf_counter()
    recovered_ivs = kuwala.implied_volatility(prices, spots, strikes, ttms, r, q, is_call=True)
    t1 = time.perf_counter()

    elapsed = t1 - t0
    throughput = N / elapsed
    rmse = np.sqrt(np.nanmean((recovered_ivs - vols) ** 2))

    print(f"Processed:          {N:,} option quotes")
    print(f"Total Time:         {elapsed*1000:.2f} ms")
    print(f"Throughput:         {throughput:,.0f} options/sec")
    print(f"Accuracy (RMSE):    {rmse:.2e}")
    print("==========================================================")

if __name__ == "__main__":
    run_benchmark()
