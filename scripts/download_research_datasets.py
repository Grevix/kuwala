"""
Kuwala Research Datasets Downloader & Ingestion Script (Optimized Streaming & Indexing).
======================================================================================
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path("research/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

manifest = {}


def index_kaggle_datasets():
    print("--- [1/4] Indexing Kaggle Datasets ---")
    import kagglehub

    datasets_to_try = [
        ("s_and_p500_jacksaleeby", "jacksaleeby/s-and-p500-historical-data"),
        ("nasdaq100_jacksaleeby", "jacksaleeby/nasdaq100-historical-data-2000-2026-upvote"),
        ("nasdaq100_novandra", "novandraanugrah/nasdaq-100-nas100-historical-price-data"),
    ]

    for name, path_id in datasets_to_try:
        try:
            path = kagglehub.dataset_download(path_id)
            p = Path(path)
            csv_files = list(p.glob("**/*.csv")) + list(p.glob("**/*.parquet"))
            total_size = sum(f.stat().st_size for f in csv_files)
            print(f"  [SUCCESS] {name} indexed from {path} ({len(csv_files)} files, {total_size/(1024*1024):.1f} MB)")
            
            # Copy main files into research/data/
            copied_files = []
            for f in csv_files[:5]:
                dest = DATA_DIR / f"{name}_{f.name}"
                shutil.copy2(f, dest)
                copied_files.append(str(dest))

            manifest[name] = {
                "source": "Kaggle",
                "identifier": path_id,
                "status": "DOWNLOADED",
                "raw_path": str(path),
                "file_count": len(csv_files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "copied_files": copied_files,
            }
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            manifest[name] = {
                "source": "Kaggle",
                "identifier": path_id,
                "status": "UNAVAILABLE",
                "error": str(e),
            }

    # Competition
    manifest["quantcompetition"] = {
        "source": "Kaggle Competition",
        "identifier": "quantcompetition",
        "status": "RESTRICTED",
        "note": "Requires authenticated Kaggle API token with competition rules acceptance",
    }


def stream_huggingface_datasets():
    print("\n--- [2/4] Streaming & Inspecting Hugging Face Datasets ---")
    from datasets import load_dataset

    hf_datasets = [
        ("TroveLedger", "Traders-Lab/TroveLedger"),
        ("quant_finance_dataset", "mo35/quant-finance-dataset"),
        ("financial_analyst_lite", "yifishbossman/financial-analyst-data-lite"),
    ]

    for name, path_id in hf_datasets:
        print(f"Streaming Hugging Face dataset: {path_id}...")
        try:
            # Use streaming mode to fetch sample without multi-GB download
            ds_stream = load_dataset(path_id, split="train", streaming=True)
            samples = []
            for i, row in enumerate(ds_stream):
                samples.append(row)
                if i >= 500:
                    break
            
            sample_df = pd.DataFrame(samples)
            sample_file = DATA_DIR / f"{name}_sample.parquet"
            sample_df.to_parquet(sample_file)

            cols = list(sample_df.columns)
            dtypes = {c: str(sample_df[c].dtype) for c in cols}
            print(f"  [SUCCESS] {name}: Streamed {len(sample_df)} sample rows. Columns: {cols[:6]}")

            manifest[name] = {
                "source": "Hugging Face",
                "identifier": path_id,
                "status": "INDEXED",
                "sample_rows": len(sample_df),
                "columns": cols,
                "dtypes": dtypes,
                "sample_file": str(sample_file),
            }
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            manifest[name] = {
                "source": "Hugging Face",
                "identifier": path_id,
                "status": "UNAVAILABLE",
                "error": str(e),
            }


def download_fred_macro_data():
    print("\n--- [3/4] Downloading Live FRED Macro & Rate Series ---")
    from kuwala.data.adapters import FredAdapter

    fred = FredAdapter()
    series_list = [
        ("DGS3MO", "3-Month Treasury Constant Maturity Rate"),
        ("DGS1", "1-Year Treasury Constant Maturity Rate"),
        ("DGS2", "2-Year Treasury Constant Maturity Rate"),
        ("DGS5", "5-Year Treasury Constant Maturity Rate"),
        ("DGS10", "10-Year Treasury Constant Maturity Rate"),
        ("FEDFUNDS", "Effective Federal Funds Rate"),
        ("CPIAUCSL", "Consumer Price Index for All Urban Consumers"),
        ("VIXCLS", "CBOE Volatility Index (VIX)"),
        ("T10Y2Y", "10-Year Treasury Minus 2-Year Treasury Spread"),
    ]

    fred_results = {}
    for sid, desc in series_list:
        try:
            df = fred.fetch(sid, observation_start="2000-01-01")
            file_path = DATA_DIR / f"fred_{sid}.parquet"
            df.to_parquet(file_path)
            print(f"  [SUCCESS] FRED {sid} ({desc}): {len(df):,} rows from {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
            fred_results[sid] = {
                "description": desc,
                "rows": len(df),
                "start": str(df["date"].min().strftime('%Y-%m-%d')),
                "end": str(df["date"].max().strftime('%Y-%m-%d')),
                "file": str(file_path),
            }
        except Exception as e:
            print(f"  [ERROR] FRED {sid}: {e}")

    manifest["fred_macro_series"] = {
        "source": "Federal Reserve Bank of St. Louis (FRED)",
        "status": "DOWNLOADED",
        "series": fred_results,
    }


def download_nasdaq_data_link():
    print("\n--- [4/4] Testing & Downloading Nasdaq Data Link ---")
    from kuwala.data.adapters import NasdaqDataLinkAdapter

    ndl = NasdaqDataLinkAdapter()
    tables = [
        "USTREASURY/YIELD",
    ]
    ndl_results = {}
    for table in tables:
        try:
            df = ndl.fetch(table)
            file_path = DATA_DIR / f"nasdaq_{table.replace('/', '_')}.parquet"
            df.to_parquet(file_path)
            print(f"  [SUCCESS] Nasdaq Data Link {table}: {len(df):,} rows")
            ndl_results[table] = {
                "rows": len(df),
                "file": str(file_path),
            }
        except Exception as e:
            print(f"  [ERROR] Nasdaq Data Link {table}: {e}")

    manifest["nasdaq_data_link"] = {
        "source": "Nasdaq Data Link",
        "status": "DOWNLOADED",
        "tables": ndl_results,
    }


if __name__ == "__main__":
    t0 = time.perf_counter()
    index_kaggle_datasets()
    stream_huggingface_datasets()
    download_fred_macro_data()
    download_nasdaq_data_link()

    with open("research/results/raw_download_manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)
    print(f"\nDownload & Ingestion Phase completed in {time.perf_counter() - t0:.2f}s")
