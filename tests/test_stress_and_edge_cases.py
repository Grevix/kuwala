"""
Pre-Release Stress Testing & Numerical Edge Cases Suite for Kuwala.
"""

import pytest
import numpy as np
import pandas as pd
import kuwala
from kuwala.pricing.black_scholes import black_scholes
from kuwala.pricing.greeks import greeks
from kuwala.volatility.iv import implied_volatility
from kuwala.volatility.surface import VolatilitySurface, SsviSurface
from kuwala.data.models import OptionChain, OptionQuote, OptionType
from kuwala.data.store import DataStore
from kuwala.data.adapters.sec_edgar import SecEdgarAdapter
from kuwala.signals.realized_vol import realized_volatility

def test_pricing_extreme_moneyness():
    spot = 100.0
    r = 0.04
    t = 1.0
    vol = 0.20

    # Deep OTM Call (K = 10000.0) -> Price should be 0.0
    otm_call = black_scholes(spot, 10000.0, t, r, 0.0, vol, is_call=True)
    assert otm_call == 0.0 or otm_call < 1e-10

    # Deep ITM Call (K = 0.01) -> Price should be close to S - K*exp(-rT)
    itm_call = black_scholes(spot, 0.01, t, r, 0.0, vol, is_call=True)
    assert pytest.approx(itm_call, rel=1e-4) == spot - 0.01 * np.exp(-r * t)

    # Deep OTM Put (K = 0.01) -> Price should be 0.0
    otm_put = black_scholes(spot, 0.01, t, r, 0.0, vol, is_call=False)
    assert otm_put == 0.0 or otm_put < 1e-10

    # Deep ITM Put (K = 10000.0) -> Price should be K*exp(-rT) - S
    itm_put = black_scholes(spot, 10000.0, t, r, 0.0, vol, is_call=False)
    assert pytest.approx(itm_put, rel=1e-4) == 10000.0 * np.exp(-r * t) - spot

def test_pricing_zero_and_negative_inputs():
    # Negative spot / strike
    assert black_scholes(-100.0, 100.0, 1.0, 0.05, 0.0, 0.2, is_call=True) == 0.0
    assert black_scholes(100.0, -100.0, 1.0, 0.05, 0.0, 0.2, is_call=True) == 0.0

    # Zero time to expiry (Intrinsic value)
    call_exp = black_scholes(110.0, 100.0, 0.0, 0.05, 0.0, 0.2, is_call=True)
    assert call_exp == 10.0
    put_exp = black_scholes(90.0, 100.0, 0.0, 0.05, 0.0, 0.2, is_call=False)
    assert put_exp == 10.0

    # Zero volatility
    call_zero_vol = black_scholes(105.0, 100.0, 1.0, 0.0, 0.0, 0.0, is_call=True)
    assert call_zero_vol == 5.0

def test_greeks_extreme_cases():
    # Zero time Greeks
    g_exp = greeks(105.0, 100.0, 0.0, 0.05, 0.0, 0.2, is_call=True)
    assert g_exp.delta == 1.0
    assert g_exp.gamma == 0.0
    assert g_exp.vega == 0.0

    # Zero volatility Greeks
    g_zvol = greeks(105.0, 100.0, 1.0, 0.05, 0.0, 0.0, is_call=True)
    assert g_zvol.gamma == 0.0
    assert g_zvol.vega == 0.0

def test_iv_extreme_short_expiry():
    spot = 100.0
    strike = 100.0
    t = 1e-5 # ~5 minutes
    vol = 0.25
    price = black_scholes(spot, strike, t, 0.0, 0.0, vol, is_call=True)
    rec_iv = implied_volatility(price, spot, strike, t, 0.0, 0.0, is_call=True)
    assert pytest.approx(rec_iv, abs=1e-3) == vol

def test_single_tenor_surface():
    expiries = [0.25]
    k_grid = np.linspace(-0.2, 0.2, 20)
    w_mat = np.zeros((1, 20))
    w_mat[0, :] = (0.20 ** 2) * 0.25

    surf = VolatilitySurface("TEST", 100.0, expiries, k_grid, w_mat)
    loc_vol = surf.local_vol()
    assert loc_vol.shape == (1, 20)
    
    # 1D interpolation
    iv_val = surf.implied_volatility(100.0, 0.25)
    assert pytest.approx(iv_val, abs=1e-3) == 0.20

def test_sec_edgar_user_agent_validation():
    adapter = SecEdgarAdapter()
    # Invalid user agent should raise ValueError
    with pytest.raises(ValueError, match="SEC EDGAR fair access policy requires a valid User-Agent"):
        adapter.fetch("AAPL", user_agent="Sample App")

    # Valid user agent should succeed
    res = adapter.fetch("AAPL", user_agent="CustomFirm/1.0 (quant@customfirm.com)")
    assert res["status"] == "active"

def test_datastore_sql_injection_protection(tmp_path):
    store = DataStore(db_path=tmp_path / "sql_test.duckdb")
    chain = kuwala.data.fetch("SPY")
    store.write_chain(chain.to_dataframe())

    # Attempt SQL injection in get_latest_chain
    res = store.get_latest_chain("SPY' OR '1'='1")
    assert res.empty  # Parameterized query treats it as literal string, no injection
    store.close()

def test_realized_vol_zero_variance_handling():
    # Flat price series -> Volatility should be 0.0 without crash
    dates = pd.date_range("2026-01-01", periods=30, freq="B")
    df = pd.DataFrame({
        "open": 100.0,
        "high": 100.0,
        "low": 100.0,
        "close": 100.0,
    }, index=dates)

    rv_c2c = realized_volatility(df, window=20, estimator="close_to_close")
    rv_gk = realized_volatility(df, window=20, estimator="garman_klass")

    assert pytest.approx(rv_c2c.dropna().iloc[-1], abs=1e-7) == 0.0
    assert pytest.approx(rv_gk.dropna().iloc[-1], abs=1e-7) == 0.0
