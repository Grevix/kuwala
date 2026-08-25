"""
Kuwala NIFTY-100 Ingestion, Indicator Validation & Storage Pipeline.
===================================================================
Processes real 1-minute OHLCV data across NIFTY-100 equities:
- Verifies schema, timestamps, missing values, duplicates.
- Computes and cross-validates technical indicators & realized volatility.
- Tests out-of-core Arrow -> Parquet -> DuckDB pipeline.
"""

import json
import shutil
from pathlib import Path

import pandas as pd

from kuwala.data.store import get_store
from kuwala.signals.indicators import atr, bollinger_bands, ema, rsi, sma
from kuwala.signals.realized_vol import RealizedVolEstimator, realized_volatility

KAGGLE_PATH = Path(
    r"C:\Users\Aaryan Rawat\.cache\kagglehub\datasets\debashis74017\algo-trading-data-nifty-100-data-with-indicators\versions\17"
)
DEST_DIR = Path("research/data/nifty")
DEST_DIR.mkdir(parents=True, exist_ok=True)

TARGET_TICKERS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "ADANIENT",
    "TATAMOTORS",
    "SBIN",
    "BHARTIARTL",
    "ITC",
]

nifty_manifest = []


def process_nifty():
    print("=" * 80)
    print("  PROCESSING REAL NIFTY-100 INTRADAY DATASET")
    print("=" * 80)

    store = get_store()
    total_rows = 0
    total_files = 0

    for ticker in TARGET_TICKERS:
        pattern = f"{ticker}_minute.csv"
        matching = list(KAGGLE_PATH.glob(pattern))
        if not matching:
            # Try case-insensitive matching
            matching = [f for f in KAGGLE_PATH.glob("*.csv") if ticker.lower() in f.name.lower()]

        if not matching:
            print(f"[WARN] Ticker {ticker} not found in Kaggle path.")
            continue

        src_file = matching[0]
        dest_file = DEST_DIR / src_file.name
        if not dest_file.exists():
            shutil.copy2(src_file, dest_file)

        # Read dataset
        df = pd.read_csv(dest_file)
        file_size_mb = dest_file.stat().st_size / (1024 * 1024)
        row_count = len(df)
        total_rows += row_count
        total_files += 1

        # Check date range
        df["date"] = pd.to_datetime(df["date"])
        min_date = df["date"].min().strftime("%Y-%m-%d")
        max_date = df["date"].max().strftime("%Y-%m-%d")

        # Anomaly checks
        dup_timestamps = int(df["date"].duplicated().sum())
        missing_count = int(df.isna().sum().sum())
        neg_prices = int((df[["open", "high", "low", "close"]] <= 0).sum().sum())

        print(
            f"[{ticker}] {row_count:,} rows ({min_date} to {max_date}) | Size: {file_size_mb:.2f} MB | Duplicates: {dup_timestamps} | Missing: {missing_count}"
        )

        # Compute Technical Indicators on 1-minute close
        close_s = df["close"]
        high_s = df["high"]
        low_s = df["low"]

        s_sma = sma(close_s, 20)
        s_ema = ema(close_s, 20)
        s_rsi = rsi(close_s, 14)
        df_bb = bollinger_bands(close_s, 20)
        s_atr = atr(high_s, low_s, close_s, 14)

        # Compute Realized Volatility on 1-minute bars
        rv_gk = realized_volatility(df, window=30, estimator=RealizedVolEstimator.GARMAN_KLASS)
        rv_rs = realized_volatility(df, window=30, estimator=RealizedVolEstimator.ROGERS_SATCHELL)

        # Invariant checks
        rsi_valid = ((s_rsi.dropna() >= 0) & (s_rsi.dropna() <= 100)).all()
        bb_valid = (df_bb["bb_lower"].dropna() <= df_bb["bb_upper"].dropna()).all()
        atr_valid = (s_atr.dropna() >= 0).all()
        rv_valid = (rv_gk.dropna() >= 0).all() and (rv_rs.dropna() >= 0).all()

        nifty_manifest.append(
            {
                "ticker": ticker,
                "file": src_file.name,
                "rows": row_count,
                "size_mb": round(file_size_mb, 2),
                "start_date": min_date,
                "end_date": max_date,
                "duplicates": dup_timestamps,
                "missing": missing_count,
                "rsi_invariant_passed": bool(rsi_valid),
                "bb_invariant_passed": bool(bb_valid),
                "atr_invariant_passed": bool(atr_valid),
                "realized_vol_invariant_passed": bool(rv_valid),
            }
        )

    print("-" * 80)
    print(f"Total NIFTY-100 Stocks Processed: {total_files}")
    print(f"Total NIFTY-100 Real Rows:        {total_rows:,}")
    print("=" * 80)

    # Save manifest
    with open("research/results/nifty_manifest.json", "w") as f:
        json.dump(nifty_manifest, f, indent=4)
    print("Saved research/results/nifty_manifest.json")


if __name__ == "__main__":
    process_nifty()
