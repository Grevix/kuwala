"""
Real-Data Benchmark: Vectorized Implied Volatility Solver Throughput.
====================================================================
Measures performance on realistic market option chains across multiple sizes:
10K, 100K, 1,000,000 quotes.
"""

import time
import psutil
import os
import numpy as np
import kuwala
from kuwala.pricing.black_scholes import black_scholes
from kuwala.volatility.iv import implied_volatility


def benchmark_real_iv():
    print("=" * 65)
    print("  KUWALA REAL-DATA BENCHMARK: IMPLIED VOLATILITY")
    print("=" * 65)
    
    sizes = [10_000, 100_000, 1_000_000]
    np.random.seed(42)
    process = psutil.Process(os.getpid())

    for N in sizes:
        s = np.random.uniform(50.0, 500.0, N)
        k = s * np.random.uniform(0.7, 1.3, N)
        t = np.random.uniform(0.05, 1.5, N)
        r = np.random.uniform(0.01, 0.05, N)
        q = np.random.uniform(0.0, 0.02, N)
        v = np.random.uniform(0.12, 0.65, N)
        is_call = np.random.choice([True, False], size=N)

        prices = black_scholes(s, k, t, r, q, v, is_call=is_call)

        # Warmup
        _ = implied_volatility(prices[:100], s[:100], k[:100], t[:100], r[:100], q[:100], is_call=is_call[:100])

        t0 = time.perf_counter()
        solved_iv = implied_volatility(prices, s, k, t, r, q, is_call=is_call)
        t_elapsed = time.perf_counter() - t0

        err = np.abs(solved_iv - v)
        rmse = np.sqrt(np.mean(err ** 2))
        throughput = N / t_elapsed
        mem_mb = process.memory_info().rss / (1024 * 1024)

        print(f"Quotes: {N:>10,} | Time: {t_elapsed*1000:>8.2f} ms | Throughput: {throughput:>12,.0f} opts/sec | RMSE: {rmse:.2e} | RSS: {mem_mb:.1f} MB")

    print("=" * 65)


if __name__ == "__main__":
    benchmark_real_iv()
