# Kuwala Data Quality Audit Report

Detailed examination of missing values, duplicates, extreme jumps, and financial anomalies.

## 1. Summary of Identified Data Anomalies

1. **S&P 500 Constituent Data (jacksaleeby)**: Contains historical price jumps corresponding to corporate stock splits and spin-offs. Requires corporate-action adjustment prior to signal computation.
2. **Nasdaq-100 Constituent Data (jacksaleeby)**: Verified zero non-positive prices across 100 constituent assets.
3. **Nasdaq-100 Intraday Bars (novandra)**: Intraday 1-minute, 15-minute, and 1-hour bars for `NAS100` are continuous during US trading sessions with zero missing values.
4. **FRED Yield Series**: Daily Treasury yield series (`DGS3MO`, `DGS10`, `VIXCLS`) have weekend and federal holiday gaps as expected in standard fixed income calendars.
5. **Hugging Face Text Datasets**: Classified as Category B (Financial NLP/Research), kept distinct from core numerical pricing engines.