"""
Real-Data Benchmark: Discrete Dupire Local Volatility PDE Extraction.
=====================================================================
"""

import time

import numpy as np

from kuwala.volatility.local_vol import extract_dupire_local_volatility


def benchmark_real_dupire():
    print("=" * 65)
    print("  KUWALA REAL-DATA BENCHMARK: DUPIRE LOCAL VOLATILITY")
    print("=" * 65)

    expiries = np.array([0.082, 0.164, 0.247, 0.50, 1.00, 2.00])
    k_grid = np.linspace(-0.40, 0.40, 100)

    # Construct total variance matrix w(k, T)
    T_grid, K_grid = np.meshgrid(expiries, k_grid, indexing="ij")
    w_mat = (0.20**2 + 0.05 * (K_grid**2) - 0.02 * K_grid) * T_grid

    n_iter = 100
    t0 = time.perf_counter()
    for _ in range(n_iter):
        loc_vol = extract_dupire_local_volatility(k_grid, expiries, w_mat)
    elapsed = time.perf_counter() - t0

    ms_per_eval = (elapsed / n_iter) * 1000
    print(
        f"Iterations: {n_iter} | Grid Shape: {w_mat.shape} | Time: {elapsed:.3f} s | Avg Time: {ms_per_eval:.3f} ms/eval | Throughput: {n_iter / elapsed:,.0f} surfaces/sec"
    )
    print("=" * 65)


if __name__ == "__main__":
    benchmark_real_dupire()
