# Kuwala v0.2.0 Known Limitations & Technical Constraints

**Audit Date:** September 2026  
**Auditor:** Quantitative Systems Architect & Hostile Red Team  
**Status:** ACTIVE SPECIFICATION  

---

## 1. Asset Class & Scope Boundaries

1. **Equity & Index Exclusivity:**
   Kuwala's analytical and surface engines are designed strictly for European and American equity/index options. Unlike enterprise institutional toolkits such as Goldman Sachs `gs-quant`, Kuwala does **not** support:
   - FX Vanilla/Barrier Options
   - Credit Default Swaps (CDS)
   - Interest Rate Swaptions & Multi-Currency CMS Spreads
   - Physical Commodity Derivatives
2. **q/kdb+ Proprietary License Requirement:**
   Due to commercial licensing restrictions from KX Systems, native `q.exe` execution is unavailable on standard development environments. While Arrow IPC schemas are compatible, direct IPC streaming is blocked without external proprietary licenses.

---

## 2. Numerical & Algorithmic Boundaries

1. **Dupire Local Volatility on Raw Discrete Quotes:**
   The Dupire PDE requires twice-differentiable total implied variance with respect to log-moneyness ($\partial^2 w / \partial k^2$) and once with respect to maturity ($\partial w / \partial T$). Evaluating Dupire directly on noisy, raw market quotes produces negative local variances. Dupire **must** always be evaluated on a smooth, arbitrage-free parametric surface (such as Kuwala's calibrated `SsviSurface`).
2. **Nelson-Siegel Extrapolation:**
   The Nelson-Siegel 4-parameter model fits well between 1 month and 30 years (residuals $< 15\text{ bps}$), but asymptotically levels off beyond 30 years and should not be used for ultra-long extrapolation ($T > 30\text{Y}$).
3. **Zero-Copy Boundary Inefficiencies:**
   Vectorized Rust calls currently clone Python NumPy arrays into heap `Vec<f64>` and return boxed `PyList` objects. DuckDB ingestion in `DataStore.write_chain` converts Arrow tables via `.to_pandas()`.

---

## 3. Market Data Ingestion Constraints

1. **Yahoo Finance Post-Close Drift:**
   Free quotes from Yahoo Finance exhibit 15-minute delayed timestamps and timing mismatches between equity closing auctions (16:00 ET) and options market maker quotes (16:15 ET). Users must run Kuwala's no-arbitrage filters to reject crossed or below-intrinsic contracts.
2. **FRED Rate Limiting:**
   Direct FRED queries require an API key and are subject to public request throttling. Kuwala caches fetched series in local Parquet tables to avoid redundant queries.
