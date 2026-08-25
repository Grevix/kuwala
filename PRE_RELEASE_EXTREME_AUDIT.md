# Kuwala: Pre-Release Extreme Audit Baseline

**Date:** 2026-08-25  
**Version:** Kuwala 0.1.0 Umbrella Milestone (0.1.0 → 0.5.0)  
**Objective:** Record exact repository baseline state prior to executing the 1,000,000+ quantitative cases and live market data stress campaign.

---

## 1. Repository Inventory Baseline

- **Package Name:** `kuwala` (v0.1.0)
- **Rust Core Crate:** `kuwala_core` (v0.1.0, PyO3 ABI3, Rayon parallelization)
- **Storage Layer:** Embedded DuckDB + Apache Arrow / Parquet
- **Core Modules:**
  - `kuwala.pricing`: Black-Scholes (1973), Black-76 (1976), Analytic Greeks (Delta, Gamma, Vega, Theta, Rho, Vanna, Volga, Charm)
  - `kuwala.data`: Canonical models (`OptionQuote`, `OptionChain`, `VolatilityObservation`), Day-count conventions (`ACT/365`, `ACT/360`, `30/360`), Store (`DataStore`), Adapters (`YahooAdapter`, `FredAdapter`, `SecEdgarAdapter`, `DukascopyAdapter`, `NasdaqDataLinkAdapter`)
  - `kuwala.volatility`: Implied volatility solver (Halley / Brent), Gatheral-Jacquier SSVI calibration, Discrete Dupire local volatility PDE solver, First-class `VolatilitySurface` / `SsviSurface`
  - `kuwala.diagnostics`: Durrleman butterfly arbitrage ($g(k) \ge 0$), Calendar arbitrage ($\partial_T w \ge 0$), Structured `DiagnosticReport`
  - `kuwala.signals`: Volatility Risk Premium (VRP), Realized Volatility estimators (Close-to-Close, Parkinson, Garman-Klass, Rogers-Satchell), Skew metrics, Term structure metrics, Surface PCA, Purged K-Fold with embargo, Walk-forward validation harness
  - `kuwala.backtest`: Zero-copy bridges for VectorBT and Backtrader
  - `kuwala.cli`: Typer / Rich CLI commands (`version`, `fetch`, `fit`, `vrp`)
- **Baseline Test Suite:** 28 passing unit & integration tests (`tests/`)
- **Baseline Benchmarks:** Synthetic IV solver (1.36M opts/sec), Synthetic SSVI calibration (30.49 ms/surface)
- **CI/CD:** `.github/workflows/ci.yml` multi-OS matrix (Ubuntu, macOS, Windows; Python 3.9–3.14)
- **Security:** `.env` gitignored, `.env.example` placeholder template, license `Apache-2.0`

---

## 2. Identified Vulnerabilities & Audit Mandates

1. **Synthetic vs. Real Data Gap**: Baseline benchmarks used synthetic option chains; real-world option chains exhibit microstructure noise, missing strikes, wide spreads, crossed quotes, and varying liquidity that must be tested live.
2. **Dynamic Risk-Free Yield Curve**: Risk-free rates must be pulled live from FRED (`DGS3MO`, `DGS10`, etc.) and dynamically bootstrapped rather than assuming static 4% rate.
3. **Live Yahoo API Resilience**: Live Yahoo Finance calls must handle user-agents, crumb/cookie sessions, and non-standard JSON schemas across international equity/ETF tickers without failing silently.
4. **Scale & Concurrency Invariance**: The numerical solvers must be tested up to 1,000,000+ randomized and real cases, checking for memory leaks, Rayon thread race conditions, and precision degradation.
5. **Leakage & Lookahead Auditing**: Signal validation harnesses must be aggressively stress-tested against lookahead leakage.
