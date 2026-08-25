"""
End-to-End Relative-Value Volatility Research & Backtesting Pipeline.
"""

import kuwala
import pandas as pd
import numpy as np

def run_pipeline():
    print("==================================================")
    print("  KUWALA END-TO-END QUANT RESEARCH PIPELINE")
    print("==================================================")

    # 1. Ingest market options
    print("\n[1] Fetching live options chain for SPY...")
    chain = kuwala.data.fetch("SPY")
    print(f"    Retrieved {len(chain)} quotes across {len(chain.expiries())} expiries.")

    # 2. Clean quotes & filter illiquid entries
    cleaned_chain = kuwala.data.clean_chain(chain, filter_crossed=True, filter_zero_bid=True)
    print(f"    Cleaned chain contains {len(cleaned_chain)} valid quotes.")

    # 3. Fit SSVI Surface
    print("\n[2] Calibrating Gatheral-Jacquier (2014) SSVI Surface...")
    surface = kuwala.volatility.surface(cleaned_chain, model="ssvi")
    print(f"    Fitted parameters: rho={surface.params.rho:.4f}, eta={surface.params.eta:.4f}, gamma={surface.params.gamma:.4f}")

    # 4. Arbitrage diagnostics
    print("\n[3] Running Arbitrage Diagnostics...")
    diag = surface.diagnostics()
    print(diag.summary())

    # 5. Extract Dupire local volatility
    print("\n[4] Extracting Discrete Dupire Local Volatility...")
    loc_vol = surface.local_vol()
    print(f"    Local Vol Grid Shape: {loc_vol.shape}, Mean Local Vol: {np.nanmean(loc_vol)*100:.2f}%")

    # 6. Relative-Value VRP Signal
    print("\n[5] Calculating Volatility Risk Premium (VRP)...")
    vrp_df = kuwala.signals.vrp(surface, realized_window=20, estimator="garman_klass")
    print(vrp_df.to_string(index=False))

    # 7. Overfitting & Walk-forward Validation
    print("\n[6] Running Walk-Forward Validation Harness...")
    n_pts = 100
    dates = pd.date_range("2026-01-01", periods=n_pts, freq="B")
    sig = pd.Series(np.where(np.random.normal(0, 1, n_pts) > 0, 1.0, -1.0), index=dates)
    rets = pd.Series(np.random.normal(0.0005, 0.01, n_pts), index=dates)
    val_report = kuwala.signals.validate_signal(sig, rets, method="walk_forward", n_folds=4)
    print(val_report.summary())

    # 8. Export to VectorBT
    print("\n[7] Exporting Signals to VectorBT Bridge...")
    vbt_dict = kuwala.backtest.to_vectorbt(vrp_df)
    print(f"    VectorBT payload ready with keys: {list(vbt_dict.keys())}")
    print("\nPipeline execution complete!")

if __name__ == "__main__":
    run_pipeline()
