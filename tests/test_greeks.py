import pytest
import numpy as np
import kuwala

def test_analytic_vs_finite_difference_greeks():
    spot = 100.0
    strike = 105.0
    t = 0.75
    r = 0.04
    q = 0.015
    sigma = 0.22

    # Analytic
    g = kuwala.greeks(spot, strike, t, r, q, sigma, is_call=True)

    # Finite difference bumps
    h_s = 1e-4 * spot
    p_up = kuwala.black_scholes(spot + h_s, strike, t, r, q, sigma, is_call=True)
    p_down = kuwala.black_scholes(spot - h_s, strike, t, r, q, sigma, is_call=True)
    p_mid = kuwala.black_scholes(spot, strike, t, r, q, sigma, is_call=True)

    fd_delta = (p_up - p_down) / (2.0 * h_s)
    fd_gamma = (p_up - 2.0 * p_mid + p_down) / (h_s ** 2)

    h_v = 1e-5
    p_vol_up = kuwala.black_scholes(spot, strike, t, r, q, sigma + h_v, is_call=True)
    p_vol_down = kuwala.black_scholes(spot, strike, t, r, q, sigma - h_v, is_call=True)
    fd_vega = (p_vol_up - p_vol_down) / (2.0 * h_v)

    assert pytest.approx(g.delta, rel=1e-3) == fd_delta
    assert pytest.approx(g.gamma, rel=1e-3) == fd_gamma
    assert pytest.approx(g.vega, rel=1e-3) == fd_vega
    assert g.volga > 0  # Volga is positive for standard options
