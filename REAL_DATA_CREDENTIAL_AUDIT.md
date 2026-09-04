# Real Data Credential Audit

| Provider | Credential Present | Test Performed | Result | Error Category |
| :--- | :--- | :--- | :--- | :--- |
| FRED | YES | DGS10 Observations Query | VERIFIED (HTTP 200, 16154 rows) | None |
| Nasdaq Data Link | YES | Environment Config Check | PRESENT (Unverified query) | None |
| GS Quant | NO | Marquee Auth Check | NOT PRESENT | Unauthenticated (Local timeseries only) |
| Yahoo Finance (yfinance) | N/A (Public) | SPY/QQQ Real Option Chains & OHLCV | VERIFIED | None |
| SEC EDGAR | N/A (User-Agent header) | User-Agent compliance check | VERIFIED | None |
