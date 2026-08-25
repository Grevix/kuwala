# End-to-End Real-World Benchmarks Report

This document records the official, reproducible real-data benchmark measurements for Kuwala 0.1.0.

---

## 1. Benchmark Execution Environment

- **Operating System:** Windows 11 Pro (64-bit AMD64)
- **Python Version:** 3.14.3
- **Rust Core:** `kuwala_core` v0.1.0 (Release Build, PyO3 ABI3, Rayon)
- **Data Source:** Live Market Options & History via Yahoo Finance & FRED Rate Curves

---

## 2. Benchmark Throughput & Latency Summary

| Benchmark Component | Input Dataset Size | Execution Time | Measured Throughput | Accuracy / Convergence | Memory (RSS) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Vectorized IV Solver (10K)** | 10,000 Quotes | 3.47 ms | **2,882,924 opts/sec** | $\text{RMSE} = 1.60 \times 10^{-3}$ | 165.1 MB |
| **Vectorized IV Solver (100K)** | 100,000 Quotes | 41.70 ms | **2,397,823 opts/sec** | $\text{RMSE} = 1.42 \times 10^{-3}$ | 173.8 MB |
| **Vectorized IV Solver (1M)** | 1,000,000 Quotes | 471.06 ms | **2,122,859 opts/sec** | $\text{RMSE} = 1.38 \times 10^{-3}$ | 235.3 MB |
| **SSVI Multi-Tenor Calibration** | 20 Multi-Tenor Surfaces | 4.15 s | **4.8 surfaces/sec** | **100.0% Convergence** | 185.0 MB |
| **Dupire Local Volatility PDE** | 100 Evaluations ($6 \times 100$ Grid) | 0.303 s | **330 surfaces/sec** (3.03 ms/eval) | 100.0% Strict Positivity | 178.2 MB |
| **Realized Vol: Close-to-Close** | 100,000 OHLCV Bars | 5.49 ms | **18,224,231 bars/sec** | Exact | 175.0 MB |
| **Realized Vol: Parkinson** | 100,000 OHLCV Bars | 4.74 ms | **21,078,814 bars/sec** | Exact | 175.0 MB |
| **Realized Vol: Garman-Klass** | 100,000 OHLCV Bars | 5.99 ms | **16,686,691 bars/sec** | Exact | 175.0 MB |
| **Realized Vol: Rogers-Satchell** | 100,000 OHLCV Bars | 6.72 ms | **14,875,197 bars/sec** | Exact | 175.0 MB |

---

## 3. End-to-End Pipeline Stage Latency Breakdown

Measured via `benchmarks/benchmark_end_to_end_real.py`:

```text
======================================================================
  KUWALA END-TO-END REAL-DATA BENCHMARK (STAGE LATENCY BREAKDOWN)
======================================================================
Stage 1: Fetch Raw Options Data (HTTP):     1721.08 ms  (43.1%)
Stage 2: Clean & Microstructure Filter:        0.07 ms  (<0.1%)
Stage 3: SSVI Calibration & Diagnostics:     370.18 ms   (9.3%)
Stage 4: Dupire Local Volatility PDE:          2.56 ms   (0.1%)
Stage 5: VRP Signal & History Computation:  1823.54 ms  (45.7%)
Stage 6: VectorBT Bridge Handoff:              4.23 ms   (0.1%)
Stage 7: DuckDB + Parquet Persistence:        70.52 ms   (1.8%)
----------------------------------------------------------------------
TOTAL END-TO-END PIPELINE LATENCY:          3992.19 ms
PEAK MEMORY FOOTPRINT:                       180.93 MB
======================================================================
```
