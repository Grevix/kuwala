# Kuwala Multi-Language Capability & Ecosystem Matrix

**Audit Date:** September 2026  
**Auditor:** Quantitative Systems Architect  

---

## 1. Capability & Fitness Matrix

| Quantitative Domain | Python | Rust (`kuwala_core`) | Native C++20 (`kuwala_cpp`) | Julia (`Kuwala.jl`) | R (`kuwalaR`) | Scala (`kuwala-scala`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Research & Prototyping** | **Excellent (Primary)** | Moderate | Low | **Excellent (Scientific)** | **Excellent (Stats)** | Moderate |
| **Analytical Option Pricing** | Moderate (~85K ops/s) | **Fast (~555K ops/s)** | **Fastest (>14M ops/s)** | **Fast (~600K ops/s)** | Moderate | **Fast (~1.2M ops/s)** |
| **1st & 2nd Order Greeks** | Moderate (~42K ops/s) | **Fast (~273K ops/s)** | **Fastest (>7.3M ops/s)**| **Fast (~300K ops/s)** | Moderate | **Fast (~800K ops/s)** |
| **Implied Volatility Solver** | Moderate (~31K ops/s) | **Fast (~350K ops/s)** | **Fastest (>1.3M ops/s)**| **Fast (~400K ops/s)** | Moderate | **Fast (~500K ops/s)** |
| **SSVI Calibration** | Excellent (Scipy) | **Fast (Rayon)** | High | **Fast (Optim.jl)** | High | Moderate |
| **Data Engineering & Storage**| **Excellent (DuckDB)**| High | High | High (Arrow.jl) | High (Arrow R) | **Fastest (Spark/JVM)** |
| **Tick Aggregation** | High (2.1M ticks/s) | **Fast (2.1M ticks/s)**| **Fastest (>87M ticks/s)**| High | Moderate | **Fastest (Flink/JVM)** |
| **Statistical Visualization** | High (Matplotlib) | Low | Low | High (Plots.jl) | **Best (ggplot2)** | Moderate |
| **Production Serving / HFT** | Low | **Best (Memory-safe)**| **Best (Zero alloc)** | Moderate (JIT risk) | Low | Moderate (GC risk) |

---

## 2. Definitive Language Roles in Kuwala

1. **Python:** Primary user API, interactive notebook research, CLI, and integration testing.
2. **Rust (`kuwala_core`):** Memory-safe compiled numerical core powering the Python library via PyO3 C-ABI.
3. **C++20 (`kuwala_cpp`):** Optional zero-allocation, ultra-low-latency SIMD hot paths for microsecond execution.
4. **Julia (`Kuwala.jl`):** Scientific volatility modeling, automatic differentiation, and mathematical experimentation.
5. **R (`examples/r/`):** Publication-quality ggplot2 visualization and econometric time-series research.
6. **Scala (`scala/`):** Enterprise JVM data engineering, Apache Spark pipelines, and zero-boxing batch ingestion.
