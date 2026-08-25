import numpy as np
import pytest

import kuwala


def test_implied_volatility_recovery():
    spot = 100.0
    strike = 102.0
    t = 0.5
    r = 0.03
    q = 0.01
    true_sigma = 0.285

    price = kuwala.black_scholes(spot, strike, t, r, q, true_sigma, is_call=True)
    recovered_iv = kuwala.implied_volatility(price, spot, strike, t, r, q, is_call=True)

    assert pytest.approx(recovered_iv, abs=1e-5) == true_sigma


def test_implied_volatility_put_recovery():
    spot = 50.0
    strike = 48.0
    t = 0.25
    r = 0.05
    q = 0.0
    true_sigma = 0.35

    price = kuwala.black_scholes(spot, strike, t, r, q, true_sigma, is_call=False)
    recovered_iv = kuwala.implied_volatility(price, spot, strike, t, r, q, is_call=False)

    assert pytest.approx(recovered_iv, abs=1e-5) == true_sigma


def test_implied_volatility_batch():
    spots = np.array([100.0, 100.0, 100.0])
    strikes = np.array([95.0, 100.0, 105.0])
    vols = np.array([0.20, 0.22, 0.25])
    prices = kuwala.black_scholes(spots, strikes, 1.0, 0.04, 0.0, vols, is_call=True)

    recovered = kuwala.implied_volatility(prices, spots, strikes, 1.0, 0.04, 0.0, is_call=True)
    np.testing.assert_allclose(recovered, vols, rtol=1e-4)


def test_implied_volatility_arbitrage_bound_rejection():
    # Price below intrinsic value should return NaN or error
    spot = 100.0
    strike = 50.0
    t = 1.0
    # Intrinsic call is > 50, but pass price = 10.0
    bad_price = 10.0
    res = kuwala.implied_volatility(bad_price, spot, strike, t, 0.05, 0.0, is_call=True)
    assert np.isnan(res)
