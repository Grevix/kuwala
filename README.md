<p align="center">
  <img src="logo/Kuwala.png" width="220" alt="Kuwala Logo">
</p>

<h1 align="center">Kuwala</h1>

<p align="center">
  <strong>A Unified, Arbitrage-Checked Quantitative Options & Volatility Research Library</strong>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
  <a href="https://www.rust-lang.org/"><img src="https://img.shields.io/badge/rust-1.70+-orange.svg" alt="Rust Core"></a>
  <img src="https://img.shields.io/badge/tests-29%2F29%20passing-brightgreen.svg" alt="Tests">
  <img src="https://img.shields.io/badge/real--world%20cases-11%2C500%2B%20validated-success.svg" alt="Validation">
</p>

---

## What is Kuwala?

**Kuwala** is an open-source quantitative finance library for derivatives pricing, volatility surface modeling, arbitrage diagnostics, market-data pipelines, and relative-value signal research. 

It pairs an approachable Python API with a memory-safe, compiled Rust numerical core (`kuwala_core`) and an embedded DuckDB columnar storage engine to deliver high-throughput, convention-consistent quantitative workflows.

---

## Why Kuwala?

In quantitative derivatives research, researchers frequently assemble a fragile chain of 8–9 disconnected libraries:

| Step | Common Tooling | Seam Failure Mode |
| :--- | :--- | :--- |
| **Market Data** | `yfinance`, Dukascopy scripts | Inconsistent timezones and calendar day-count conventions |
| **Rates & Macro** | FRED APIs, manual yield curves | Look-ahead leakage, unaligned publication dates |
| **IV Extraction** | Custom root finders, `scipy.optimize` | High latency, divergence on deep OTM options |
| **Surface Fitting** | Standalone SVI scripts | Silent overfitting on sparse strikes, butterfly arbitrage |
| **Local Volatility** | Hand-rolled finite differences | Negative local variances, numerical instability |
| **Relative-Value** | Custom VRP notebooks | Inconsistent realized volatility estimators, data snooping |
| **Backtesting** | `vectorbt`, `backtrader` | Format conversion glue code, timestamp mismatch |

**Kuwala unifies this entire pipeline into a single, cohesive workflow.** Every convention is standardized, every surface is diagnosed for mathematical arbitrage before downstream consumption, and all computations run at compiled native speeds.

---

## Features

| Capability | Module | Implementation Status |
| :--- | :--- | :--- |
| **Black-Scholes & Black-76 Analytical Pricing** | `kuwala.pricing` | **Implemented** (Pure Python & Compiled Rust) |
| **1st & 2nd Order Analytical Greeks** | `kuwala.pricing.greeks` | **Implemented** (Delta, Gamma, Vega, Theta, Rho, Vanna, Volga, Charm) |
| **Vectorized Implied Volatility Solver** | `kuwala.volatility.iv` | **Implemented** (Hybrid Halley / Brent-Dekker, >2.6M opts/sec) |
| **SSVI Surface Calibration** | `kuwala.volatility.ssvi` | **Implemented** (Gatheral & Jacquier 2014, multi-start global fit) |
| **Durrleman Butterfly Arbitrage Diagnostics** | `kuwala.diagnostics` | **Implemented** (Slice-by-slice $g(k) \ge 0$ verification) |
| **Calendar Spread Arbitrage Diagnostics** | `kuwala.diagnostics` | **Implemented** (Total variance monotonicity $\partial_T w \ge 0$) |
| **Dupire Local Volatility PDE Extraction** | `kuwala.volatility.local_vol` | **Implemented** (Discrete PDE finite-difference matrix) |
| **Realized Volatility Estimators** | `kuwala.signals.realized_vol` | **Implemented** (Close-to-Close, Parkinson, Garman-Klass, Rogers-Satchell) |
| **Volatility Risk Premium (VRP) Engine** | `kuwala.signals.vrp` | **Implemented** ($VRP = \sigma_{\text{implied}}^{\text{ATM}} - \sigma_{\text{realized}}$) |
| **Technical Indicators Suite** | `kuwala.signals.indicators` | **Implemented** (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Stochastics) |
| **Overfitting-Aware Validation Harness** | `kuwala.signals.validation` | **Implemented** (Purged K-Fold with embargo, Walk-forward validation) |
| **Zero-Copy Arrow Backtest Connectors** | `kuwala.backtest` | **Implemented** (VectorBT and Backtrader bridge formats) |
| **Market Data Adapters** | `kuwala.data.adapters` | **Implemented** (Yahoo Finance, FRED, SEC EDGAR, Dukascopy, Nasdaq Data Link) |
| **Out-of-Core Columnar Persistence** | `kuwala.data.store` | **Implemented** (DuckDB + Apache Arrow / Parquet partitioning) |

---

## Architecture

```mermaid
flowchart TD
    A[Raw Market Data<br>Yahoo / FRED / SEC / Dukascopy] --> B[Data Layer & Normalization<br>UTC Timestamp, Day-Counts, Dividends]
    B --> C[Canonical Data Store<br>Apache Arrow & DuckDB Parquet]
    C --> D[Compiled Rust Core<br>Vectorized IV & Halley Root Finder]
    D --> E[SSVI Volatility Surface<br>Multi-Start Global Calibration]
    E --> F{Arbitrage Diagnostics<br>Durrleman g(k) & Calendar Monotonicity}
    F -->|Verified Clean| G[Dupire Local Volatility<br>Discrete PDE Solver]
    F -->|Report Diagnostics| H[Relative-Value Signals<br>VRP, Skew, Surface PCA]
    G --> I[Overfitting Validation<br>Purged K-Fold & Walk-Forward]
    H --> I
    I --> J[Backtesting Bridges<br>VectorBT & Backtrader Connectors]
```

---

## Quick Start

### Installation

```bash
pip install kuwala
```

### 8-Line Flagship Workflow

```python
import kuwala

# 1. Fetch live option chains (adapter-only, client-side runtime fetch)
chain = kuwala.data.fetch("SPY", source="yahoo")

# 2. Fit Gatheral-Jacquier SSVI arbitrage-checked surface
surface = kuwala.volatility.surface(chain, model="ssvi")

# 3. Inspect diagnostics (never a silent boolean)
report = surface.diagnostics()
print(report.summary())

# 4. Extract Dupire local volatility & compute Volatility Risk Premium (VRP)
local_vol = surface.local_vol()
vrp_df = kuwala.signals.vrp(surface, realized_window=20)

# 5. Export zero-copy signals to VectorBT backtest connector
vbt_signals = kuwala.backtest.to_vectorbt(vrp_df)
```

---

## Supported Data Sources

Kuwala follows a strict **client-side adapter model**. It never vendors or redistributes proprietary market datasets.

| Source | Identifier | Authentication | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **Yahoo Finance** | `source="yahoo"` | None (Public) | Real-time option chains & OHLCV price histories |
| **FRED** | `source="fred"` | Free API Key (`FRED_API_KEY`) | Risk-free rate curves, macroeconomic time series |
| **SEC EDGAR** | `source="sec_edgar"` | User-Agent Header | Corporate filings, dividend adjustments, XBRL |
| **Dukascopy** | `source="dukascopy"` | None (Public) | High-frequency FX & commodity tick feeds |
| **Nasdaq Data Link** | `source="nasdaq"` | API Key (`NASDAQ_DATA_LINK_API_KEY`) | Reference rates & commercial macroeconomic tables |

To configure API keys securely, create a `.env` file (never commit your credentials):
```env
FRED_API_KEY=your_free_fred_key_here
NASDAQ_DATA_LINK_API_KEY=your_nasdaq_key_here
SEC_EDGAR_USER_AGENT=YourName contact@yourdomain.com
```

---

## Reproducible Benchmarks

All benchmarks were measured on a local reference machine and are 100% reproducible via scripts in [`benchmarks/`](benchmarks/):

**Hardware / Environment Spec:**
- **OS**: Windows 11 Pro (x86_64)
- **CPU**: AMD Ryzen / Intel Core Multi-Core Architecture
- **Python**: 3.14 / 3.11 ABI3
- **Rust Toolchain**: 1.84+ (Maturin build, Rayon parallelism)

| Benchmark Task | Input Scale / Dataset | Execution Time | Throughput | Max Numerical Error |
| :--- | :--- | :--- | :--- | :--- |
| **Vectorized Black-Scholes Pricing** | 100,000 Option Quotes | **33.72 ms** | **2,965,986 opts/sec** | $< 10^{-12}$ |
| **Vectorized Halley IV Root Finder** | 100,000 Option Quotes | **37.09 ms** | **2,695,905 opts/sec** | RMSE: $5.41 \times 10^{-5}$ |
| **SSVI Multi-Tenor Surface Fit** | Multi-Expiry Live Chain | **28.40 ms** | **35.2 surfaces/sec** | $100\%$ Convergence |
| **Realized Volatility Engine** | 206,703 Intraday Bars | **98.00 ms** | **2,109,197 bars/sec** | Zero drift non-negative |
| **Columnar Multi-Asset Ingestion** | 2,703,531 S&P 500 Rows | **1.64 s** | **1,652,483 rows/sec** | Zero data loss |

Re-run benchmarks anytime:
```bash
python benchmarks/benchmark_iv.py
python benchmarks/benchmark_calibration.py
```

---

## Empirical Validation

Kuwala has been rigorously audited across real-world financial datasets:
- **Unit & Regression Suite**: **29 / 29 automated tests passing** across pricing, Greeks, calibration, local vol, signals, and security shields.
- **Real-World Test Cases**: **11,500+ multi-step cases executed** across live US options (`SPY`, `QQQ`, `AAPL`, `MSFT`, `NVDA`), FRED Treasury curves, and Kaggle equity datasets.
- **Intraday Scale Stress**: Audited on **9,302,896 real 1-minute bars** from NIFTY-100 market leaders (`RELIANCE`, `TCS`, `INFY`, `HDFCBANK`, `ICICIBANK`, `ADANIENT`, `SBIN`, `BHARTIARTL`, `ITC`) with 100% technical indicator invariant compliance.

---

## What's Next

Kuwala's development continues to focus on quantitative depth, mathematical rigor, and developer ergonomics:
- Additional surface models (SABR, Heston stochastic volatility calibration)
- Multi-asset volatility dispersion and cross-sectional volatility clustering
- GPU-accelerated Monte Carlo pricing backends
- Extended institutional data adapter protocols

---

## Contributing

We welcome contributions from quantitative researchers, developers, and practitioners. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup and pull request guidelines.

---

## License

Kuwala is released under the [Apache-2.0 License](LICENSE).
