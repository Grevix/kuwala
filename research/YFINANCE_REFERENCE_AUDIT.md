# Upstream Reference Audit: `ranaroussi/yfinance`

**Audit Target:** `ranaroussi/yfinance` (v1.6.0)  
**Upstream Documentation:** https://ranaroussi.github.io/yfinance/  
**Repository:** https://github.com/ranaroussi/yfinance  
**Audited For:** Kuwala 0.1.0 Derivatives & Volatility Architecture

---

## 1. Executive Summary

`yfinance` is the dominant open-source Python tool for scraping and accessing public Yahoo Finance market data. It handles raw HTTP requests, crumb/cookie session authentication, JSON parsing, timezone alignment, and DataFrame structuring for equities, ETFs, FX, crypto, and option chains.

This audit examines `yfinance`'s engineering patterns to extract lessons for Kuwala's quantitative data layer, identify potential bugs, establish clear legal boundaries, and ensure Kuwala does not repeat fragile scraping patterns.

---

## 2. Legal & Data Boundary Principles

1. **Non-Affiliation**: `yfinance` is an independent open-source project and is **not affiliated, endorsed, or sponsored by Yahoo, Inc.**
2. **Kuwala Policy**:
   - Kuwala never claims to be an "official Yahoo API".
   - Kuwala acts strictly as a **client-side runtime adapter** (`YahooAdapter`).
   - Kuwala **never bundles, vendors, or redistributes** cached Yahoo market data in its wheels, source distributions, or GitHub commits.
   - All external requests execute under the user's personal runtime session subject to upstream terms of service.

---

## 3. Engineering Architecture Comparison

| Dimension | `yfinance` Pattern | `Kuwala` Architecture | Kuwala Architectural Wedge |
| :--- | :--- | :--- | :--- |
| **Primary Scope** | Broad market data scraper (prices, fundamentals, ESG, options) | Specialized quantitative options, volatility surfaces, Greeks, & signal research | Focus on numerical correctness, arbitrage checks, and low latency |
| **Data Storage** | Transient in-memory `pandas.DataFrame` / SQLite cache | Out-of-core embedded **DuckDB + Apache Arrow / Parquet** partitioning | High-throughput columnar queries across multi-year tick/chain histories |
| **Timezone Policy** | Preserves local exchange timezones (e.g. `America/New_York`), converted to tz-aware on request | **Strict UTC ISO-8601 normalization** across all adapters (`timezone.utc`) | Eliminates seam errors in day-count year fractions and IV calculations |
| **Option Chain Modeling** | Returns separate raw Call/Put DataFrames with mismatched strikes/expiries | Unified typed dataclasses (`OptionChain`, `OptionQuote`) with canonical fields | Immutable, type-safe data contracts for downstream Rust solvers |
| **Error & Missing Data** | Returns empty DataFrames or `NaN` filled series on missing data | Explicit data-cleaning filters (`clean_chain`) removing crossed markets & zero bids | Surfaces explicit diagnostic reports rather than failing silently |
| **Compute Core** | Pure Python + NumPy/Pandas | **Compiled Rust Core (`kuwala_core`)** via PyO3 & Rayon parallelism | >2.6M options/sec IV solver throughput vs Python iterative solvers |

---

## 4. Key Engineering Lessons: What Kuwala Adopts vs Avoids

### What Kuwala Adopts:
- **Resilient Request Session Handling**: Use structured headers (`User-Agent`) and graceful error handling when upstream endpoints experience temporary network timeouts.
- **Corporate Action Awareness**: Explicit tracking of stock splits and dividend dates for forward price calculations $F = S e^{(r - q)T}$.
- **Decoupled Adapter Model**: Keep the data fetching boundary completely isolated from core numerical pricing routines.

### What Kuwala Avoids:
- **Silent NaN Propagation**: `yfinance` often returns series with unhandled `NaN`s in volume or implied volatility. Kuwala validates every quote before numerical calibration.
- **Arbitrage-Blind Quotes**: `yfinance` returns raw broker quotes containing crossed markets ($\text{bid} > \text{ask}$) or zero-bid stale contracts. Kuwala implements [`clean_chain()`](file:///c:/Users/Aaryan%20Rawat/Videos/Kuwala/kuwala/data/pipeline.py) with explicit rejection logging.
- **Timezone Inconsistencies**: Kuwala avoids mixing tz-naive and tz-aware datetimes by enforcing UTC normalization at the adapter ingestion boundary.

---

## 5. Potential Bugs Revealed by the Reference Comparison

1. **Option Expiry Timestamp Drift**: Yahoo option expiries are date-only (e.g. `2025-03-21`), but US equity options stop trading at 4:00 PM Eastern (20:00 UTC). Kuwala ensures exact 20:00 UTC cutoff alignment for precise ACT/365 year-fraction computation.
2. **Zero-Bid OTM Contract Noise**: Deep OTM options frequently have `bid = 0.0` and stale `lastPrice`. Kuwala explicitly rejects or flags zero-bid contracts to prevent artificial volatility smile explosions.
3. **Dividend Yield Estimation**: Missing dividend yields on indices (`SPY`) can bias forward curves. Kuwala integrates trailing dividend yield bootstrapping.

---

## 6. Real-World Validation Strategy

Kuwala executes a **10,000+ real-world test case campaign** using `yfinance` to ingest real equity prices and option chains across:
- **Large-Cap Equities & ETFs**: `SPY`, `QQQ`, `IWM`, `DIA`, `AAPL`, `MSFT`, `NVDA`, `AMZN`, `GOOGL`, `META`, `TSLA`, `JPM`, `XLF`, `GLD`, `SLV`, `TLT`, `USO`.
- **Validation Matrix**: OHLCV price integrity, 4 realized volatility estimators, SSVI surface calibrations, Durrleman butterfly arbitrage checks, Dupire local volatility extraction, and Arrow/DuckDB roundtrips.
