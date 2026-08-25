import pytest
import pandas as pd
import numpy as np
import kuwala
from kuwala.signals.realized_vol import realized_volatility, RealizedVolEstimator

def test_realized_volatility_estimators():
    dates = pd.date_range("2026-01-01", periods=50, freq="B")
    np.random.seed(42)
    close = 100.0 * np.exp(np.cumsum(np.random.normal(0, 0.01, 50)))
    high = close * 1.01
    low = close * 0.99
    open_p = close * 1.002

    df = pd.DataFrame({
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
    }, index=dates)

    rv_c2c = realized_volatility(df, window=20, estimator="close_to_close")
    rv_park = realized_volatility(df, window=20, estimator="parkinson")
    rv_gk = realized_volatility(df, window=20, estimator="garman_klass")

    assert not rv_c2c.dropna().empty
    assert not rv_park.dropna().empty
    assert not rv_gk.dropna().empty
    assert rv_gk.dropna().iloc[-1] > 0.0

def test_vrp_signal_computation():
    chain = kuwala.data.fetch("SPY")
    surf = kuwala.volatility.surface(chain)
    vrp_df = kuwala.signals.vrp(surf, realized_window=20, estimator="garman_klass")

    assert not vrp_df.empty
    assert "implied_vol" in vrp_df.columns
    assert "realized_vol" in vrp_df.columns
    assert "vrp_spread" in vrp_df.columns
