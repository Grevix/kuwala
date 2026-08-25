# Nasdaq-100 Dataset Reconciliation & Methodology Comparison

This document provides a comparative reconciliation between the two downloaded Nasdaq-100 datasets: **jacksaleeby/nasdaq100-historical-data-2000-2026-upvote** and **novandraanugrah/nasdaq-100-nas100-historical-price-data**.

---

## 1. Structural Comparison Matrix

| Dimension | `jacksaleeby` Nasdaq-100 Dataset | `novandra` Nasdaq-100 Dataset |
| :--- | :--- | :--- |
| **Asset Level** | **Constituent Stock Equities** (100 individual stock tickers: AAPL, MSFT, AMZN, NVDA, GOOG, etc.) | **Aggregate Index Futures / CFD** (`NAS100` aggregate benchmark) |
| **Temporal Resolution** | Daily close bars (EOD) | Multi-resolution intraday bars (**1-minute, 15-minute, 1-hour, 1-day**) |
| **Row Count** | **514,075 daily rows** | **>3,500,000 intraday rows** (1-minute file: 174.6 MB) |
| **Date Range** | 2000-01-03 to 2026-02-20 (26 years) | 2020 to 2024 (Intraday tick/bar period) |
| **Adjusted Prices** | Includes Open, High, Low, Close, Adj Close, Volume | Continuous OHLCV bars without dividend adjustment |
| **Kuwala Role** | Cross-sectional equity momentum, idiosyncratic volatility, and PCA surface clustering | High-frequency Realized Volatility estimator stress testing (Garman-Klass, Parkinson, Rogers-Satchell) |

---

## 2. Quantitative Reconciliation & Discrepancy Findings

1. **Constituent vs. Index Composition**:
   - `jacksaleeby` tracks single-stock equity constituents. Each row is uniquely identified by `(Date, Symbol)`.
   - `novandra` tracks the composite `NAS100` price movement. Each row is uniquely identified by `(Timestamp)`.
2. **Volatilities Comparison**:
   - Aggregate index realized volatility is systematically lower than median single-stock realized volatility due to diversification / non-unit correlation among constituents ($\rho < 1$).
3. **Usage in Kuwala Testing**:
   - `novandra` 1-minute dataset is used to benchmark Kuwala's realized volatility estimators on $>100,000$ real intraday bars.
   - `jacksaleeby` 514,075-row dataset is used to benchmark Kuwala's DuckDB columnar storage and multi-asset time-series processing.
