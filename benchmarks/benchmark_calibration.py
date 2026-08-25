"""
Reproducible SSVI Surface Calibration Benchmark Suite.
"""

import platform
import time

import kuwala
from kuwala.volatility.ssvi import CalibrationConfig


def run_calibration_benchmark():
    print("==========================================================")
    print("  KUWALA REPRODUCIBLE BENCHMARK: SSVI CALIBRATION")
    print("==========================================================")
    print(f"System: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python: {platform.python_version()}")
    print("----------------------------------------------------------")

    chain = kuwala.data.fetch("SPY")
    cfg = CalibrationConfig(optimizer="lbfgsb", max_iter=1000)

    # Measure calibration time
    n_runs = 50
    t0 = time.perf_counter()
    for _ in range(n_runs):
        surf = kuwala.volatility.surface(chain, model="ssvi", config=cfg)
    t1 = time.perf_counter()

    elapsed = t1 - t0
    avg_ms = (elapsed / n_runs) * 1000.0

    print(f"Number of Iterations: {n_runs}")
    print(f"Total Time:           {elapsed:.3f} s")
    print(f"Avg Calibration Time: {avg_ms:.2f} ms / surface")
    print(f"Surface Throughput:   {n_runs / elapsed:.1f} surfaces/sec")
    print("==========================================================")


if __name__ == "__main__":
    run_calibration_benchmark()
