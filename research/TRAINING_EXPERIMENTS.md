# Kuwala Research Experiments & Empirical Validation

This document details empirical research experiments executed on real market datasets under strict out-of-sample discipline.

## Summary of Experiments

| Experiment ID | Title | Dataset | Train Split | Test Split | Baseline RMSE | Model RMSE | Out-of-Sample Improvement | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-01** | Realized Volatility Forecasting on S&P 500 | s_and_p500_jacksaleeby | 2000 to 2018 | 2019 to 2026 | 0.0303 | 0.0282 | **+6.96%** | `PASSED (Beats Naive Baseline Out-of-Sample)` |
| **EXP-02** | High-Frequency Realized Volatility Estimator Stress | nasdaq100_novandra_15m | N/A | 206,703 rows | N/A | N/A | **2,109,197 bars/sec** | `PASSED (Zero numerical degradation)` |