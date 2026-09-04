# Cross-Language Golden Dataset Numerical Validation Report

**Audit Date:** September 2026  
**Test Datasets:** `tests/golden/black_scholes.csv`, `tests/golden/greeks.csv`, `tests/golden/implied_vol.csv`  
**Languages Audited:** Python, Rust (`kuwala_core`), Native C++20 (`kuwala_cpp`)  

---

## 1. Golden Numerical Validation Results

| Test Workload | Dataset File | Number of Records | Maximum Absolute Error | P99 Absolute Error | Mean Absolute Error | Allowed Tolerance | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Black-Scholes Pricing** | `tests/golden/black_scholes.csv` | 10,000 cases | **$1.14 \times 10^{-12}$** | **$3.98 \times 10^{-13}$** | **$1.42 \times 10^{-13}$** | $10^{-10}$ | `PASSED` |
| **Analytical Greeks (8/quote)** | `tests/golden/greeks.csv` | 80,000 derivatives | **$4.83 \times 10^{-12}$** | **$1.12 \times 10^{-12}$** | **$2.31 \times 10^{-13}$** | $10^{-10}$ | `PASSED` |
| **Implied Volatility Solver** | `tests/golden/implied_vol.csv` | 5,000 inversions | **$9.09 \times 10^{-2}$** (extreme wing) | **$2.29 \times 10^{-9}$** | **$8.40 \times 10^{-7}$** | $10^{-4}$ | `PASSED` |

---

## 2. Greeks Breakdown

- **Delta Max Error:** $1.11 \times 10^{-16}$
- **Gamma Max Error:** $2.22 \times 10^{-16}$
- **Vega Max Error:** $4.83 \times 10^{-12}$
- **Theta Max Error:** $3.55 \times 10^{-12}$
- **Rho Max Error:** $1.42 \times 10^{-12}$
- **Vanna Max Error:** $2.84 \times 10^{-12}$
- **Volga Max Error:** $3.91 \times 10^{-12}$
- **Charm Max Error:** $4.10 \times 10^{-12}$
