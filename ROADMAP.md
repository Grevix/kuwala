# Kuwala Technical Roadmap

This roadmap outlines the phased development and vision for the Kuwala quantitative library.

---

## Current Release: Foundation (v0.1.0)
- Analytical Black-Scholes / Black-76, analytical 1st & 2nd order Greeks.
- High-throughput compiled Rust core (`kuwala_core`) with hybrid Halley/Brent IV solver.
- Unified data adapters (Yahoo Finance, FRED, SEC EDGAR, Dukascopy, Nasdaq Data Link).
- Embedded DuckDB + Apache Arrow / Parquet out-of-core persistence.
- Gatheral-Jacquier SSVI multi-tenor calibration with Durrleman butterfly and calendar arbitrage diagnostics.
- Discrete Dupire local volatility extraction.
- Relative-value signal engine (VRP, Skew, Term Structure, Surface PCA).
- Overfitting-aware validation harness (Purged K-Fold with embargo, Walk-forward analysis).
- Zero-copy VectorBT and Backtrader backtesting bridges.

---

## Next Horizon: Hardening & Ecosystem Expansion
- **Advanced Diagnostics**: Surface residual PCA clustering and volatility regime shifts.
- **Surface Extensions**: SABR and Heston stochastic volatility parameterizations.
- **Cross-Sectional RV**: Multi-asset volatility dispersion and index relative-value analytics.
- **Packaging & CI**: Multi-OS binary wheel distribution (manylinux, macOS universal2, Windows MSVC).
- **v1.0 Flagship**: Stable release with formal community governance and expanded benchmark matrices.

---

## Long-Term Horizon (Demand-Gated)
- Optional GPU-accelerated Monte Carlo pricing backends.
- External language FFI bridges (Julia / R).
- Read-only institutional socket adapters (e.g. q/kdb+ IPC) upon user demand.
