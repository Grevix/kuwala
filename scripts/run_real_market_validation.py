"""
Real-World Multi-Ticker Option Chain & End-to-End Pipeline Validation.
======================================================================
Tests 11 Major US Market Tickers:
SPY, QQQ, AAPL, MSFT, NVDA, AMZN, GOOG, META, TSLA, IWM, DIA

Executes the full pipeline:
Real Chain -> Clean -> Live FRED Rate Curve -> IV -> SSVI -> Arbitrage Diagnostics ->
Dupire Local Vol -> VRP -> Skew -> Term Structure -> PCA -> Purged K-Fold -> VectorBT Export
"""

import time
import json
import hashlib
import numpy as np
import pandas as pd
import kuwala
from kuwala.data.adapters import YahooAdapter, FredAdapter
from kuwala.data.pipeline import clean_chain
from kuwala.volatility.iv import extract_chain_iv
from kuwala.volatility.ssvi import calibrate_ssvi, CalibrationConfig
from kuwala.volatility.surface import SsviSurface, VolatilitySurface
from kuwala.diagnostics.arbitrage import diagnose_surface
from kuwala.signals.vrp import vrp
from kuwala.signals.skew import skew_metrics
from kuwala.signals.term_structure import term_structure_metrics
from kuwala.signals.validation import purged_kfold_split, validate_signal
from kuwala.backtest.vectorbt import to_vectorbt
from kuwala.backtest.backtrader import to_backtrader
from kuwala.data.store import get_store


def run_real_market_validation():
    print("=" * 75)
    print("  KUWALA REAL-WORLD MARKET DATA & PIPELINE VALIDATION")
    print("=" * 75)

    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOG", "META", "TSLA", "IWM", "DIA"]
    yahoo = YahooAdapter()
    fred = FredAdapter()
    store = get_store()

    print("\nFetching Live Treasury Rate Curve from FRED...")
    rate_curve = fred.get_treasury_curve()
    print("Live Treasury Curve:", {f"{k}y": f"{v*100:.2f}%" for k, v in rate_curve.items()})

    manifest_entries = []
    ticker_results = {}
    surfaces_for_pca = []

    total_real_contracts = 0
    total_valid_contracts = 0
    total_rejected = 0

    for sym in tickers:
        print(f"\n--- Testing Ticker: {sym} ---")
        t0 = time.perf_counter()
        
        # 1. Fetch Option Chain
        chain = yahoo.fetch(sym, fetch_all_expiries=True)
        raw_count = len(chain)
        total_real_contracts += raw_count
        
        # 2. Audit Microstructure Invariants
        valid_q = []
        rejected_q = []
        rejection_reasons = {}

        for q in chain.quotes:
            reason = None
            if q.strike <= 0:
                reason = "non_positive_strike"
            elif q.bid < 0 or q.ask < 0:
                reason = "negative_quote"
            elif q.bid > q.ask and q.ask > 0:
                reason = "crossed_market"
            elif (q.bid == 0.0 and q.ask == 0.0) or q.mid <= 0:
                reason = "zero_bid_ask"
            
            if reason:
                rejected_q.append(q)
                rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            else:
                valid_q.append(q)

        valid_count = len(valid_q)
        rej_count = len(rejected_q)
        total_valid_contracts += valid_count
        total_rejected += rej_count

        # 3. Clean chain
        cleaned_chain = clean_chain(chain)

        # 4. Extract IV
        obs = extract_chain_iv(cleaned_chain)
        print(f"[{sym}] Raw: {raw_count} | Valid: {valid_count} | Cleaned & Solved IV: {len(obs)}")
        if rejection_reasons:
            print(f"[{sym}] Microstructure Rejections: {rejection_reasons}")

        # 5. Fit SSVI Surface
        ssvi_surf = SsviSurface.calibrate(cleaned_chain)
        surfaces_for_pca.append(ssvi_surf.iv_matrix)

        # 6. Arbitrage Diagnostics
        diag = ssvi_surf.diagnostics()
        print(f"[{sym}] Butterfly Arbitrage: {'PASSED' if diag.butterfly_passed else 'FAILED'} | Calendar: {'PASSED' if diag.calendar_passed else 'FAILED'}")

        # 7. Dupire Local Volatility
        loc_vol = ssvi_surf.local_vol()
        has_negative_var = np.any(np.isnan(loc_vol)) or np.any(loc_vol <= 0.0)
        print(f"[{sym}] Dupire Local Vol Shape: {loc_vol.shape} | Strict Positivity: {'PASSED' if not has_negative_var else 'FAILED'}")

        # 8. Signals: VRP, Skew, Term Structure
        hist_df = yahoo.fetch_history(sym, period="1y", interval="1d")
        vrp_df = vrp(ssvi_surf, hist_prices=hist_df, realized_window=20)
        skew_res = skew_metrics(ssvi_surf)
        term_res = term_structure_metrics(ssvi_surf)

        # 9. Purged Validation Harness
        sim_signal = pd.Series(np.where(hist_df["close"].pct_change().shift(-1) > 0, 1.0, -1.0), index=hist_df.index).dropna()
        val_res = validate_signal(sim_signal, hist_df["close"].pct_change().dropna())

        # 10. Backtest Connectors
        vbt_df = to_vectorbt(vrp_df)
        bt_feed = to_backtrader(hist_df)

        # 11. Columnar Store Roundtrip
        store.write_chain(cleaned_chain.to_dataframe())

        elapsed = time.perf_counter() - t0
        print(f"[{sym}] Full Pipeline Completed in {elapsed:.2f}s")

        ticker_results[sym] = {
            "raw_contracts": raw_count,
            "valid_contracts": valid_count,
            "rejected_contracts": rej_count,
            "rejection_reasons": rejection_reasons,
            "butterfly_passed": diag.butterfly_passed,
            "calendar_passed": diag.calendar_passed,
            "dupire_positive": bool(not has_negative_var),
            "vrp_spread": float(vrp_df["vrp_spread"].iloc[0]) if not vrp_df.empty else 0.0,
            "skew_25d": float(skew_res.get("risk_reversal_25d", 0.0)),
            "term_slope": float(term_res.get("term_structure_slope", 0.0)),
            "oos_sharpe": float(val_res.mean_out_of_sample_sharpe),
            "pipeline_runtime_s": round(elapsed, 3),
        }

        # Record dataset hash
        chain_bytes = cleaned_chain.to_dataframe().to_csv().encode("utf-8")
        manifest_entries.append({
            "source": "Yahoo Finance / FRED",
            "dataset": f"{sym}_OPTIONS_CHAIN",
            "instrument": sym,
            "date_range": f"{cleaned_chain.timestamp.strftime('%Y-%m-%d')} to {cleaned_chain.expiries()[-1].strftime('%Y-%m-%d') if cleaned_chain.expiries() else 'N/A'}",
            "download_timestamp": cleaned_chain.timestamp.isoformat(),
            "row_count": len(cleaned_chain),
            "file_size_bytes": len(chain_bytes),
            "schema_hash": hashlib.sha256(str(cleaned_chain.to_dataframe().columns.tolist()).encode()).hexdigest()[:16],
            "data_hash": hashlib.sha256(chain_bytes).hexdigest()[:16],
        })

    # Surface PCA Decomposition
    if surfaces_for_pca:
        from kuwala.signals.pca import surface_pca
        pca_res = surface_pca(surfaces_for_pca)
        print(f"\nSurface Multi-Asset PCA Explained Variance (PC1 Level, PC2 Slope, PC3 Curvature):")
        print(f"  PC1 (Level):     {pca_res.explained_variance_ratio[0]*100:.1f}%")
        print(f"  PC2 (Slope):     {pca_res.explained_variance_ratio[1]*100:.1f}%")
        print(f"  PC3 (Curvature): {pca_res.explained_variance_ratio[2]*100:.1f}%")

    with open("real_data_manifest.json", "w") as f:
        json.dump(manifest_entries, f, indent=4)
    print("\nSaved real data manifest to real_data_manifest.json")

    print("\n" + "=" * 75)
    print(f"REAL-WORLD VALIDATION SUMMARY: {len(tickers)} Tickers Audited")
    print(f"Total Contracts: {total_real_contracts:,} | Valid: {total_valid_contracts:,} | Rejected: {total_rejected:,}")
    print("=" * 75)


if __name__ == "__main__":
    run_real_market_validation()
