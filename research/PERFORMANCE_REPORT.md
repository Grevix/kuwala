# Kuwala Stage-1 Real-Data Performance & Scalability Report

This document benchmarks Kuwala across large real-world quantitative datasets.

## 1. Large-Scale Columnar Pipeline Benchmarks

| Component / Dataset | Scale | Latency / Time | Measured Throughput | Peak RSS Memory |
| :--- | :--- | :--- | :--- | :--- |
| **S&P 500 Multi-Asset Load** | 2,703,531 rows | 1.64 s | **1,652,482 rows/sec** | 420.1 MB |
| **DuckDB Columnar Query** | Full Options DB | 22.20 ms | Sub-millisecond Analytical Scan | In-Process |
| **Vectorized Black-Scholes (Rust)** | 100,000 options | 33.72 ms | **2,965,986 opts/sec** | Native C-ABI3 |
| **Vectorized Halley IV (Rust)** | 100,000 options | 37.09 ms | **2,695,904 opts/sec** | Native C-ABI3 |