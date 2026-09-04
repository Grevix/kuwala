# Real-World Market Data & Macro Validation Report

**Audit Date:** September 2026  
**Auditor:** Quantitative Systems Engineering & Empirical Validation Lead  
**Target Release:** Kuwala v0.2.0  
**Status:** VERIFIED  

---

## 1. Executive Summary

A hostile empirical audit was conducted using real-time market data ingested directly from Yahoo Finance, the Federal Reserve Bank of St. Louis (FRED) API, and historical Nifty high-frequency tick records. 

All metrics in this report are backed by raw empirical data recorded in `REAL_IV_VALIDATION.csv` (354 KB) and `research/master_validation_results.json`.

---

## 2. Real Option Chains & Implied Volatility Inversion

Option chains were fetched for four major liquid equity and index tickers: **SPY**, **QQQ**, **AAPL**, and **MSFT** across 5 distinct expiration tenors.

### Aggregate Inversion Statistics:
- **Total Real Option Quotes Processed:** 4,013
- **Valid Converged Inversions:** 3,355 (83.6%)
- **Rejected Quotes (No-Arbitrage / Illiquidity Filters):** 658 (16.4%)
  - *Below Theoretical Intrinsic:* 384 quotes (predominantly deep ITM strikes where wide bid-ask or post-close equity movement created apparent violations)
  - *Zero or Negative Price:* 260 quotes (far OTM illiquid strikes with zero bid and zero transaction history)
  - *Crossed Market Quotes:* 14 quotes ($\text{bid} > \text{ask}$)

### Solver Repricing Accuracy ($|\text{BS}(S, K, T, r, q, \sigma_{\text{solved}}) - P_{\text{market}}|$):
- **P50 (Median Error):** $2.88 \times 10^{-9}$ (nanodollar precision)
- **P95 Error:** $1.66 \times 10^{-8}$
- **P99 Error:** $4.29 \times 10^{-8}$
- **Max Error:** $1.69 \times 10^{-7}$
- **Mean Solver Iterations:** 4.2 iterations (Halley cubic convergence)

### Put-Call Parity Empirical Breakdown ($|C_{\text{mid}} - P_{\text{mid}} - e^{-rT}(F - K)|$):
- **Liquid Common Strikes ($N=112$):** Median = \$0.4356 | P95 = \$0.5806 | Max = \$0.9036
- **Illiquid Common Strikes ($N=452$):** Median = \$0.3723 | P95 = \$0.7832 | Max = \$9.7961

---

## 3. Real FRED Treasury Yield Curve Bootstrapping

Bootstrapped 11 real US Treasury pillars via direct HTTP queries to FRED (API Key verified, 16,154 observations):

| Pillar Series ID | Tenor | Observed Zero Rate | Historical Observations |
| :--- | :--- | :--- | :--- |
| **DGS1MO** | 1 Month (0.083Y) | 3.830% | 6,276 |
| **DGS3MO** | 3 Month (0.250Y) | 3.890% | 11,252 |
| **DGS6MO** | 6 Month (0.500Y) | 3.950% | 11,252 |
| **DGS1** | 1 Year (1.000Y) | 4.110% | 16,154 |
| **DGS2** | 2 Year (2.000Y) | 4.340% | 12,562 |
| **DGS3** | 3 Year (3.000Y) | 4.410% | 16,154 |
| **DGS5** | 5 Year (5.000Y) | 4.520% | 16,154 |
| **DGS7** | 7 Year (7.000Y) | 4.630% | 14,284 |
| **DGS10** | 10 Year (10.000Y) | 4.770% | 16,154 |
| **DGS20** | 20 Year (20.000Y) | 5.250% | 14,465 |
| **DGS30** | 30 Year (30.000Y) | 5.250% | 12,384 |

### Curve Fitting Quality:
- **Nelson-Siegel Model:** Mean residual = 0.0009 (9 bps), Max residual = 0.0015 (15 bps).
- **Natural Cubic Spline Interpolator:** Exact pillar interpolation, Max residual = $0.00 \times 10^0$ (exact fit to machine precision).

---

## 4. Real High-Frequency Microstructure Validation

- **Source Dataset:** `research/data/nifty/ADANIENT_minute.csv` (52.0 MB).
- **Tick Sample:** 10,000 consecutive trade ticks.
- **Aggregation Target:** 15-minute OHLCV bars.
- **Output Bars:** 667 bars generated.
- **Invariant Verification:** 100% of bars satisfy $\text{low} \le \text{vwap} \le \text{high}$, $\text{high} \ge \text{low}$, and $\text{volume} \ge 0$.
