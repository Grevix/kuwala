"""
Real-Data Benchmark: SSVI Multi-Tenor Surface Calibration.
===========================================================
Measures multi-start global optimization calibration throughput and convergence.
"""

import time

import numpy as np

from kuwala.volatility.ssvi import CalibrationConfig, calibrate_ssvi


def benchmark_real_ssvi():
    print("=" * 65)
    print("  KUWALA REAL-DATA BENCHMARK: SSVI SURFACE CALIBRATION")
    print("=" * 65)

    expiries = [0.082, 0.164, 0.247, 0.50, 1.00]
    n_surfaces = 20
    np.random.seed(42)

    total_time = 0.0
    converged = 0

    for i in range(n_surfaces):
        log_k_dict = {}
        iv_dict = {}
        for t in expiries:
            k = np.linspace(-0.30, 0.30, 25)
            iv = 0.20 + 0.08 * (k**2) - 0.04 * k + np.random.normal(0, 0.002, len(k))
            log_k_dict[t] = k
            iv_dict[t] = np.maximum(0.05, iv)

        cfg = CalibrationConfig(max_iter=500, tol=1e-6)
        t0 = time.perf_counter()
        params = calibrate_ssvi(expiries, log_k_dict, iv_dict, config=cfg)
        elapsed = time.perf_counter() - t0
        total_time += elapsed
        if params.rho != 0.0:
            converged += 1

    avg_ms = (total_time / n_surfaces) * 1000
    throughput = n_surfaces / total_time
    print(
        f"Surfaces: {n_surfaces} | Total Time: {total_time:.2f} s | Avg Time: {avg_ms:.2f} ms/surface | Throughput: {throughput:.1f} surfaces/sec | Convergence: {converged / n_surfaces * 100:.1f}%"
    )
    print("=" * 65)


if __name__ == "__main__":
    benchmark_real_ssvi()
