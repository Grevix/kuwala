# Language & Quantitative Ecosystem Teardown

**Audit Date:** September 2026  
**Auditor:** Quantitative Systems Architect  

---

## 1. Reference Open-Source Ecosystems Analyzed

### A. Julia Quantitative Ecosystem
- **Relevant Packages:** `FinancialToolbox.jl`, `Miletus.jl`, `DifferentialEquations.jl`, `Optim.jl`, `Arrow.jl`.
- **Key Architectural Findings:**
  - Multiple dispatch allows defining mathematical operations cleanly on abstract types (`OptionPayoff`, `YieldCurve`).
  - JIT compilation introduces a cold-start latency overhead on first evaluation, but warm loop performance approaches compiled C++.
  - Recommended Kuwala integration: standalone research package interacting via Apache Arrow memory streams.

### B. Scala / JVM Quantitative Ecosystem
- **Relevant Packages:** `Breeze` (mostly retired numerical library), `Apache Arrow Java`, `Apache Spark`, `Spire`.
- **Key Architectural Findings:**
  - JVM object boxing introduces severe garbage collection (GC) pressure when creating millions of small case classes.
  - To achieve institutional performance, numeric computations must operate directly over primitive `Array[Double]`.
  - Recommended Kuwala integration: specialized data engineering bridge for Arrow/Parquet batch ingestion into Spark jobs.

### C. Goldman Sachs `gs-quant`
- Institutional Python toolkit connecting to Goldman Sachs Marquee cloud services.
- Kuwala implements local, zero-server alternatives with embedded DuckDB and native compiled Rust/C++ kernels.

### D. `yfinance`
- Public scraping library for Yahoo Finance endpoints.
- Requires strict data cleaning against crossed markets, zero bids, and missing volume fields.
