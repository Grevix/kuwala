import math

import numpy as np
import pytest

import kuwala


def test_black_scholes_call_put_parity():
    spot = 100.0
    strike = 105.0
    t = 1.0
    r = 0.05
    q = 0.02
    sigma = 0.25

    call = kuwala.black_scholes(spot, strike, t, r, q, sigma, is_call=True)
    put = kuwala.black_scholes(spot, strike, t, r, q, sigma, is_call=False)

    # C - P = S*exp(-q*T) - K*exp(-r*T)
    expected_diff = spot * math.exp(-q * t) - strike * math.exp(-r * t)
    actual_diff = call - put

    assert pytest.approx(actual_diff, rel=1e-6) == expected_diff


def test_black_scholes_known_values():
    # Reference values: S=100, K=100, T=1, r=0.05, q=0, vol=0.20 -> Call = 10.4505756
    call = kuwala.black_scholes(100.0, 100.0, 1.0, 0.05, 0.0, 0.20, is_call=True)
    assert pytest.approx(call, abs=1e-4) == 10.45058

    # Deep ITM Call -> S*exp(-qT) - K*exp(-rT)
    deep_call = kuwala.black_scholes(200.0, 50.0, 0.5, 0.05, 0.0, 0.20, is_call=True)
    assert deep_call > 150.0


def test_black76_pricing():
    forward = 100.0
    strike = 100.0
    t = 0.5
    r = 0.04
    sigma = 0.30

    call = kuwala.black76(forward, strike, t, r, sigma, is_call=True)
    put = kuwala.black76(forward, strike, t, r, sigma, is_call=False)

    # C - P = exp(-r*T) * (F - K) = 0 for ATM forward
    assert pytest.approx(call - put, abs=1e-7) == 0.0
    assert call > 0.0


def test_black_scholes_vectorized():
    spots = np.array([90.0, 100.0, 110.0])
    strikes = np.array([100.0, 100.0, 100.0])
    calls = kuwala.black_scholes(spots, strikes, 1.0, 0.05, 0.0, 0.2, is_call=True)
    assert len(calls) == 3
    assert calls[0] < calls[1] < calls[2]
