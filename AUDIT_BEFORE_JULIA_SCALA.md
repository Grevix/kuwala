# Audit Before Julia & Scala Integration

**Audit Date:** September 2026  
**Auditor:** Quantitative Systems Architect & Red Team  
**Scope:** Architectural capabilities, existing language roles, and justified contributions for Julia and Scala.

---

## 1. Existing Component Status & Capability Matrix

| Component | Current Implementation | Language | Test Coverage | Known Limitations / Gaps | Potential Julia Contribution | Potential Scala Contribution |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Analytical Pricing** | Black-Scholes & Black-76 | Python / Rust / C++ | 42 unit & property tests | Python loop overhead; C++/Rust require compiled binaries. | **Native multiple dispatch, scientific syntax, JIT compilation for research.** | **JVM primitive array batch pricing for Java/Scala data feeds.** |
| **Analytical Greeks** | 8 1st/2nd Order Greeks | Python / Rust / C++ | Finite difference parity $< 10^{-6}$ | None in Rust/C++. | **Automatic differentiation and fast matrix sensitivity calculation.** | **Risk aggregation across enterprise JVM portfolio services.** |
| **IV Solver** | Halley (Cubic) + Brent | Python / Rust / C++ | >1.3M IV/s in C++, >350K in Rust | Ill-conditioned on deep OTM zero-bids. | **Fast scalar/vectorized root finding in scientific workflows.** | **JVM batch volatility extraction on streaming tick feeds.** |
| **Yield Curves** | Nelson-Siegel & Cubic Splines | Python (SciPy) | 8-pillar FRED tests | Python curve fitting overhead. | **High-dimensional multi-factor term structure optimization.** | **Integration with enterprise Treasury / OIS feeds.** |
| **Synthetic Forwards** | Put-Call Parity OLS | Python (NumPy) | 4 equity tickers verified | Requires paired calls and puts. | **Robust regression and statistical outlier rejection.** | **Distributed forward curve construction across big data.** |
| **Microstructure** | Tick-to-Bar, VWAP, Lee-Ready | Python / C++ | 87M ticks/s in C++ | Pandas resample memory overhead. | **High-dimensional tick econometric modeling.** | **High-throughput Spark / Flink streaming tick aggregation.** |
| **Storage Layer** | DuckDB + Parquet Hive | Embedded C++ (DuckDB) | Direct out-of-core scans | Local storage focus. | **Direct Arrow memory tables into Julia DataFrames.** | **Direct Apache Spark / Hadoop Parquet reading & writing.** |
| **Surface Calibration** | SSVI Multi-Start DE + L-BFGS-B | Python (SciPy) / Rust | Durrleman butterfly check | Python optimizer overhead. | **Global optimization with DifferentialEvolution / Optim.jl.** | **Distributed surface calibration over massive options databases.** |
| **Local Volatility** | Discrete Dupire PDE | Python / Rust | 50,000 grid points | Numerical gradient sensitivity. | **High-order PDE solvers and finite-difference stencils.** | **Grid-based local vol surface caching on the JVM.** |

---

## 2. Core Architectural Decisions for Julia & Scala

1. **Avoid Blind Algorithm Duplication:**
   - Neither Julia nor Scala will attempt to replace Rust or C++ for low-latency production execution hot paths.
   - Rust and C++ remain the primary compiled numerical execution engine for production microsecond serving.
2. **Julia's Specific Role (Scientific & Research Compute):**
   - Julia excels at interactive mathematical exploration, rapid prototyping of exotic models, automated differentiation, and vectorized matrix algorithms with mathematical syntax.
   - Kuwala provides `julia/Kuwala.jl` with native mathematical implementations and zero-copy Arrow ingestion.
3. **Scala's Specific Role (Enterprise & Big Data Engineering):**
   - Scala is the premier language for big data ecosystems (Apache Spark, Apache Flink, Akka/Pekko).
   - Kuwala provides `scala/kuwala-scala` focused on high-throughput Arrow/Parquet batch ingestion, typed immutable option domain models, and zero-boxing primitive array pricing.
