# Kuwala Changelog

All notable changes across sequential milestones are documented in this file.

---

## [0.5.0] - Relative-Value Research Layer & Backtest Bridges
### Added
- **Volatility Risk Premium (VRP)** signal engine: `signals.vrp(surface, realized_window=20)`.
- Realized Volatility Estimators: Close-to-Close, Parkinson (High-Low), Garman-Klass (OHLC), Rogers-Satchell.
- Skew Relative-Value metrics: 90/110 slope, curvature, 25-delta Risk Reversal.
- Term-structure roll-down and forward volatility curves.
- Surface PCA decomposition (Level, Slope, Curvature).
- Overfitting safeguards: Purged K-Fold Cross Validation with time-series embargo and expanding-window walk-forward validation harness.
- Zero-copy backtest bridges to `vectorbt` and `backtrader`.

---

## [0.4.0] - Dupire Local Volatility & Surface Analytics
### Added
- Discrete Dupire Local Volatility PDE extraction in total variance / log-moneyness coordinates.
- Mathematical guard rails linking Durrleman butterfly arbitrage directly to local variance non-negativity.
- Rich `VolatilitySurface` research object with `surface.shock()` scenario analysis and `surface.greeks()`.

---

## [0.3.0] - SSVI Arbitrage-Free Surface Calibration
### Added
- Gatheral & Jacquier (2014) Surface SVI (SSVI) power-law parameterization.
- Multi-tenor global calibration with multi-start Differential Evolution and L-BFGS-B polishing.
- Explicit `surface.diagnostics()` reporting butterfly violations ($g(k) < 0$) and calendar arbitrage with specific strikes/tenors.
- 3D surface and 2D smile visualization.

---

## [0.2.0] - Unified Data Pipeline & Out-of-Core Storage
### Added
- Data Adapters: Yahoo Finance, FRED macroeconomic yields, SEC EDGAR XBRL corporate actions, Dukascopy tick downloader, and Nasdaq Data Link.
- Decoupled Tick-to-OHLCV aggregation.
- Embedded DuckDB + Apache Arrow / Parquet out-of-core persistence engine (`kuwala.data.store`).
- Data cleaning pipeline filtering crossed markets and zero bids.

---

## [0.1.0] - Quantitative & Architectural Foundation
### Added
- Analytical Black-Scholes (1973) and Black-76 (1976) option pricers.
- Complete 1st and 2nd order analytical Greeks (Delta, Gamma, Vega, Theta, Rho, Vanna, Volga/Vomma, Charm).
- High-performance compiled Rust core (`kuwala_core`) via PyO3/Maturin.
- Hybrid Halley / Brent-Dekker Implied Volatility solver reaching >1.36 million options/sec.
- Normalized data models (`OptionQuote`, `OptionChain`, `VolatilityObservation`) with strict UTC ISO-8601 timestamps and ACT/365 day-count conventions.
