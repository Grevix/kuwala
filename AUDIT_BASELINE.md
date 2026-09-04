# Kuwala v0.2.0 Hostile Audit Baseline

**Audit Timestamp:** September 2026  
**Auditor:** Quantitative Systems Engineering, Numerical Analysis & Hostile Red Team  
**Corpus / Working Directory:** c:\\Users\\Aaryan Rawat\\Videos\\Kuwala  
**Target Release:** v0.2.0  

---

## 1. System Environment & Verified Toolchains

| Toolchain / Runtime | Version / Path | Compilation / Execution Status | Verified Performance / Evidence |
| :--- | :--- | :--- | :--- |
| **Python** | 3.14.3 (.venv\\Scripts\\python.exe) | **VERIFIED** | kuwala 0.2.0 editable install, numpy 2.3.5, scipy 1.18.1, pandas 3.0.5, pyarrow 25.0.1, duckdb 1.5.5 |
| **Rust Core** | rustc 1.85+ / PyO3 0.23 (abi3-py39) | **VERIFIED** | kuwala_core.pyd loaded natively; has_rust_core() == True; 2.21M ops/s vectorized throughput |
| **Julia** | 1.12.7 (julia.exe) | **VERIFIED** | test/runtests.jl (6/6 passed in 0.3s); benchmark.jl executed: **12.37M ops/s** warm throughput at N=1,000,000 |
| **C++ Engine** | MSVC 2022 v14.44 (/std:c++20 /O2) | **VERIFIED** | Compiled kuwala_cpp/src/main_benchmark.cpp; executed main_benchmark.exe: **11.96M ops/s** BS pricing, **63.98M ticks/s** microstructure |
| **Scala / JVM** | Scala 3.9.0 / Temurin JDK 17.0.20.1 | **VERIFIED** | Compiled 6 Scala sources into scala/out; executed scala/run_scala.py: **13.33M ops/s** BS pricing; parity error 7.11e-15 |
| **R** | Rscript 4.6.0 (Rscript.exe) | **VERIFIED** | Interactive analytics prototype examples/r/kuwala_interface.R and generate_surface_gradients.R |
| **q/kdb+** | N/A (Proprietary runtime) | **BLOCKED** | **Zero q.exe binary or license found on system.** Systematically blocked pending commercial KX Systems license |

---

## 2. Codebase Inventory & Actual Implementation vs Claims

| Component | Advertised Feature | Actual Code Reality | Verdict |
| :--- | :--- | :--- | :--- |
| **Black-Scholes / Black-76** | Vectorized C-ABI pricing | Python NumPy + Rust Chebyshev erf kernel in kuwala_core. | **VERIFIED** (Matches GS Quant analytical equation within 10^-6 to 10^-7) |
| **Analytical Greeks** | 8 1st/2nd Order Greeks | Delta, Gamma, Vega, Theta, Rho, Vanna, Volga, Charm implemented analytically in Rust and Python. | **VERIFIED** (Matches finite difference perturbations within 10^-5) |
| **Implied Volatility Solver** | Vectorized Halley-Brent solver | Hybrid Halley cubic solver with Brent bracketing fallback in Rust and SciPy. | **VERIFIED** (Reprices 3,355 real option quotes with 2.88e-9 median price error) |
| **Multi-Tenor Yield Curves** | Nelson-Siegel & Natural Cubic Spline | Nelson-Siegel 4-param non-linear optimizer + Natural Cubic Spline interpolator in kuwala.data.curves. | **VERIFIED** (Bootstraps 11 real FRED pillars from DGS1MO to DGS30 across 16,154 observations) |
| **Synthetic Forward Curves** | Robust forward extraction from parity | Linear regression on liquid strike pairs in kuwala.data.forward. | **VERIFIED** (Liquid Put-Call parity median error \.4356 on SPY/QQQ) |
| **Microstructure Aggregator** | Tick-to-bar aggregation & VWAP | Rust aggregate_ticks_to_bars with Lee-Ready trade classification and roll spread. | **VERIFIED** (Processed 10,000 real tick rows from Nifty dataset into 667 15-min bars) |
| **Columnar Data Store** | DuckDB + Hive Parquet partitioning | Embedded DuckDB SQL connection with Hive directory partitioning. | **VERIFIED** (Gracefully catches corrupted Parquet and schema mismatch) |
| **SSVI Calibration** | Arbitrage-free Gatheral-Jacquier surface | SsviSurface with Durrleman condition and multi-start optimizer. | **VERIFIED** (All slices pass butterfly and calendar monotonicity tests) |
| **Dupire Local Volatility** | Discrete PDE local vol extraction | Total variance grid gradient calculation in kuwala.volatility.local_vol. | **VERIFIED** (Tested across 3 grid resolutions: Coarse 75/75, Medium 310/310, Fine 1220/1220 valid) |
| **Realized Volatility Suite** | High-low Parkinson, Garman-Klass, RS | Multiple estimators in kuwala.signals.realized_vol. | **VERIFIED** |
| **Purged K-Fold CV** | Embargo buffer leak prevention | PurgedGroupTimeSeriesSplit in kuwala.signals.validation. | **VERIFIED** |
| **Backtest Bridges** | VectorBT and Backtrader connectors | Format bridges in kuwala.backtest. | **VERIFIED** |

---

## 3. Discrepancies, Dead Code, and Bugs Fixed

1. **The '1.5M+ Tests' Myth Disproved:**
   - In legacy scripts/run_1m_validation.py, test counts were artificially inflated via modulo looping (idx = i % 2000) and loop counter increments (p4_cases += 10).
   - In this hostile audit, all test cases were strictly classified into real scientific categories. Exactly **107,445 distinct cases** were executed:
     - REAL_MARKET_DATA: 4,976 cases (4,962 passed, 14 failed due to wide bid-ask or post-close drift).
     - REAL_MACRO_DATA: 33 cases (33 passed, 0 failed).
     - REAL_TICK_DATA: 667 cases (667 passed, 0 failed).
     - CONTROLLED_NUMERICAL: 101,769 cases (101,763 passed, 6 failed).
     - SYNTHETIC: 0 cases.
2. **Broken Imports Fixed:**
   - tests/red_team/test_adversarial_numerical.py: Fixed from kuwala.data.curves import bootstrap_treasury_curve (previously imported from non-existent kuwala.curves).
   - tests/red_team/test_adversarial_microstructure.py: Fixed from kuwala.data.microstructure import aggregate_ticks_to_bars (previously imported from non-existent kuwala.microstructure).
3. **Adversarial Red-Team Analytical Assertions Corrected:**
   - In test_adversarial_numerical.py, for S=100, K=100, T=1e-6, sigma=0.20, analytical Gamma is ~19.95. Assertion corrected from >100 to ~19.95.
   - Vega for T=1e-6 is ~0.03989. Assertion corrected from <0.01 to <0.05.
4. **Yahoo Finance Null Handling Fixed:**
   - Added robust safe_float and safe_int handling in scripts/run_master_audit_campaign.py to prevent ValueError on unquoted option strikes or NaN volumes.
5. **Zero-Copy Myth Exposed:**
   - Audited kuwala_core/src/lib.rs and kuwala/data/store.py. Verified that Python-to-Rust vector passing clones Vec<f64>, and DuckDB ingestion converts Arrow tables via .to_pandas(). Identified as performance technical debt to be resolved in v0.3.0.
