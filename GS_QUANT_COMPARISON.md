# Technical Comparison: Kuwala vs. Goldman Sachs GS-Quant

This document provides an objective, side-by-side technical comparison between **Kuwala** and **Goldman Sachs `gs-quant`** across all architectural, quantitative, and developer-experience dimensions.

---

## 1. Executive Comparison Matrix

| Dimension | Kuwala | GS-Quant (`goldmansachs/gs-quant`) |
| :--- | :--- | :--- |
| **Primary Focus** | Unified open-source quantitative research stack owning the data $\to$ surface $\to$ signal $\to$ backtest pipeline. | Institutional client gateway into Goldman Sachs Marquee analytics, structured products, and proprietary pricing engines. |
| **Authentication & Entitlements** | **Zero credentials required** for flagship pipeline. Fully functional out-of-the-box on open market data. | Requires Goldman Sachs Marquee Client ID & Secret for almost all meaningful pricing, risk, and historical data functions. |
| **Execution Core** | **Compiled Rust (`kuwala_core`)** via PyO3 C-ABI3 with Rayon multithreading for sub-microsecond pricing and IV. | Remote REST API calls to GS Marquee cloud servers for institutional instruments; pure Python wrappers locally. |
| **Data Persistence** | **Embedded DuckDB + Apache Arrow / Parquet** out-of-core columnar engine. | In-memory pandas DataFrames + remote server-side caching. |
| **Surface Calibration** | **Gatheral & Jacquier (2014) SSVI** with power-law parameterization and global multi-start optimization. | Server-side proprietary interpolation; client-side timeseries measures (`ts.implied_volatility`). |
| **Arbitrage Diagnostics** | **Explicit, inspectable Durrleman butterfly** ($g(k) \ge 0$) and calendar monotonicity ($\partial_T w \ge 0$) diagnostics with exact strike/tenor coordinates. | Server-side risk measures; does not expose granular client-side arbitrage verification diagnostics. |
| **Signal Layer & Backtesting** | `signals.vrp()`, skew metrics, term-structure analytics, Purged K-Fold CV, and zero-copy `vectorbt` / `backtrader` bridges. | Proprietary `gs_quant.backtests` event-driven framework coupled to Marquee market data and instrument definitions. |
| **License** | **Apache-2.0** (Completely open source). | Apache-2.0, but gates live compute behind proprietary commercial API agreements. |

---

## 2. Feature-by-Feature Technical Breakdown

### 2.1 Pricing & Greeks
* **Kuwala**: Analytical Black-Scholes (1973), Black-76 (1976), and full 1st/2nd order Greeks (Delta, Gamma, Vega, Theta, Rho, Vanna, Volga, Charm) executed locally in compiled Rust or pure Python.
* **GS-Quant**: Rich declarative instrument definitions (`EQOption`, `IRSwap`, `Swaption`, `FXOption`), but pricing delegates over HTTP to Goldman Sachs Marquee cloud servers (`instrument.price()`, `instrument.calc(RiskMeasure)`).
* **Comparison**: Kuwala provides instant, offline, deterministic local pricing with zero network latency. GS-Quant provides institutional multi-asset instrument coverage but is unusable offline.

### 2.2 Volatility Surfaces & Calibration
* **Kuwala**: Calibrates full Gatheral-Jacquier SSVI parametric surface across multi-tenors with explicit vega weighting and global optimization.
* **GS-Quant**: Exposes timeseries vol functions (`ts.implied_volatility`, `ts.realized_volatility`) and structured surface queries against GS Marquee database.
* **Comparison**: Kuwala allows quants to calibrate and diagnose surfaces directly from raw options data; GS-Quant consumes pre-computed institutional surfaces from Goldman Sachs.

### 2.3 Arbitrage Diagnostics
* **Kuwala**: Inspectable `surface.diagnostics()` checking Durrleman's second-derivative condition slice-by-slice and calendar monotonicity across tenor pairs.
* **GS-Quant**: Assumes institutional surfaces are pre-cleaned on Goldman Sachs servers; no client-side diagnostic report available.
* **Comparison**: Kuwala gives independent researchers full inspectability over arbitrage violations in free/noisy market data.

### 2.4 Timeseries & Signal Ergonomics
* **Kuwala**: Adopted GS-Quant's clean verb-first timeseries convention (`signals.vrp(surface, realized_window=20)`, `signals.realized_volatility(df, estimator="garman_klass")`).
* **GS-Quant**: Pioneer of the `ts.*` timeseries grammar (`ts.returns`, `ts.volatility`, `ts.zscores`).
* **Comparison**: Kuwala adopted GS-Quant's best ergonomic insights while backing them with local Arrow memory and Rust computation.

---

## 3. Decisions & Strategic Takeaways

1. **Keep Zero-Credential First-Class Experience**: Never gate core quantitative functionality behind logins.
2. **Preserve Declarative Instruments**: Maintain typed, immutable dataclasses (`OptionQuote`, `OptionChain`, `VolatilityObservation`) modeled after GS-Quant's declarative design.
3. **Bridge, Don't Compete**: Rather than building a closed proprietary backtest loop like Marquee, bridge cleanly via zero-copy Arrow to established open ecosystems (`vectorbt`, `backtrader`).
