# Kuwala Roadmap Umbrellas & Versioning Architecture

To maintain clear separation between semantic release versions (`v0.1.0`, `v0.2.0`, etc.) and multi-phase engineering objectives, Kuwala organizes development across two overarching **Roadmap Umbrellas**.

---

## 1. Roadmap Umbrellas Architecture

```
KUWALA FOUNDATION 0.1 UMBRELLA (v0.1.0 → v0.5.0)
│
├── v0.1.0: Mathematical & Numerical Primitives (Analytical BS/76, Greeks, Rust IV Solver, Typed Models)
├── v0.2.0: Data Pipelines, Multi-Tenor Yield Curves, Forwards, Microstructure & Partitioned Storage
├── v0.3.0: Arbitrage-Free SSVI Calibration & Coordinate-Level Durrleman Diagnostics
├── v0.4.0: Dupire Local Volatility PDE Extraction & Surface Analytics
└── v0.5.0: Relative-Value Signal Engine, Purged K-Fold Cross Validation & Backtest Connectors
│
▼ [TRANSITION BOUNDARY: v0.5.0]
│
KUWALA QUANT ENGINE 0.2 UMBRELLA (v0.5.0 → v1.5.0)
│
├── v0.6.0: Low-Latency C++ Engine & SIMD Microstructure Processing
├── v0.7.0: R Quantitative Interface (kuwalaR) & Gradient Visualizations
├── v0.8.0: Optional q/kdb+ Streaming IPC Adapter & As-Of Temporal Joins
├── v1.0.0: Institutional Multi-Asset Volatility Surface Framework & Distributed Rayon/C++ Scaling
└── v1.5.0: Production-Grade Cross-Asset Relative Value Backtest & Execution Simulation Engine
```

---

## 2. Umbrella Specifications

### Foundation 0.1 Umbrella (v0.1.0 → v0.5.0)
- **Primary Goal:** Establish rock-solid mathematical correctness, numerical stability, zero-server analytical storage, and high-performance Rust kernels.
- **Key Modules:**
  - Double-precision analytical pricing & 8 complete Greeks.
  - Sub-microsecond IV solver in Rust (>2.12M opts/sec).
  - Nelson-Siegel & Natural Cubic Spline discount yield curve bootstrapping.
  - Put-call parity synthetic forward curves and discrete dividend schedules.
  - High-frequency tick-to-bar microstructure aggregation with Lee-Ready trade direction.
  - Embedded DuckDB + Apache Arrow / Hive-partitioned Parquet storage.
  - Gatheral & Jacquier (2014) SSVI calibration with coordinate-level butterfly and calendar arbitrage reporting.
  - Dupire local volatility PDE extraction.
  - Realized volatility suite (Close-to-Close, Parkinson, Garman-Klass, Rogers-Satchell) and VRP signals.
  - Purged K-Fold time-series cross-validation with embargo buffers to eliminate lookahead bias.

### Quant Engine 0.2 Umbrella (v0.5.0 → v1.5.0)
- **Primary Goal:** Institutional performance, multi-language interoperability (C++, R, q/kdb+), and production low-latency execution pipelines.
- **Key Modules:**
  - `kuwala_cpp`: Direct C++20 zero-allocation numerical engine with SIMD vectorization.
  - `kuwalaR`: Lightweight R research and analytics package providing ggplot2 gradient smiles and surfaces.
  - `kuwala.integrations.q_kdb`: Non-blocking q/kdb+ IPC streaming adapter and PyArrow interop.
  - Out-of-core scaling benchmarks over 10M–100M+ row market datasets.
  - Multi-asset volatility arbitrage signals with institutional trade simulation.

---

## 3. Transition Boundary (v0.5.0)

Version `v0.5.0` represents the stabilization of all core Python and Rust analytical APIs. All higher versions build on top of these verified numerical contracts without breaking API backwards compatibility.
