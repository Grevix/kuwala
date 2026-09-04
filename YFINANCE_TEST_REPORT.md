# yfinance Market Data & Live Pipeline Test Report

**Audit Date:** September 2026  
**Auditor:** Quantitative Systems Architect  
**Live Equities & Indices Audited:** `SPY`, `QQQ`, `AAPL`, `MSFT`  

---

## 1. Empirical Live Market Data Results

```json
{
  "SPY": {
    "status": "PASSED",
    "underlying_price": 770.26,
    "expirations_available": 27,
    "expirations_audited": 4,
    "total_contracts_fetched": 994,
    "valid_contracts": 696,
    "rejected_contracts": 298,
    "rejection_rate_pct": 29.98,
    "forward_extraction": "Forward curve built with 3 expiry tenors"
  },
  "QQQ": {
    "status": "PASSED",
    "underlying_price": 718.23,
    "expirations_available": 27,
    "expirations_audited": 4,
    "total_contracts_fetched": 979,
    "valid_contracts": 660,
    "rejected_contracts": 319,
    "rejection_rate_pct": 32.58,
    "forward_extraction": "Forward curve built with 3 expiry tenors"
  },
  "AAPL": {
    "status": "PASSED",
    "underlying_price": 321.67,
    "expirations_available": 20,
    "expirations_audited": 4,
    "total_contracts_fetched": 508,
    "valid_contracts": 369,
    "rejected_contracts": 139,
    "rejection_rate_pct": 27.36,
    "forward_extraction": "Forward curve built with 3 expiry tenors"
  },
  "MSFT": {
    "status": "PASSED",
    "underlying_price": 500.74,
    "expirations_available": 19,
    "expirations_audited": 4,
    "total_contracts_fetched": 609,
    "valid_contracts": 447,
    "rejected_contracts": 162,
    "rejection_rate_pct": 26.60,
    "forward_extraction": "Forward curve built with 3 expiry tenors"
  }
}
```

---

## 2. Market Data Irregularities Caught & Filtered

- **Total Live Contracts Processed:** **3,090 contracts**.
- **Valid Quotes Kept:** **2,172 contracts** (70.3%).
- **Rejection Breakdown:**
  - Zero bids on deep OTM options: ~28.5%
  - Crossed market bids ($\text{Bid} > \text{Ask}$): ~0.3%
  - Missing volume/open interest: Safely parsed as `0` without casting errors.
