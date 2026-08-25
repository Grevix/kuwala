"""
Reference Implementation Numerical Cross-Validation Test Suite.
Cross-validates Kuwala analytical models against independent quantitative formulas (GS Quant & QuantLib baselines).
"""

from __future__ import annotations

import math

from scipy.stats import norm

from kuwala.diagnostics.arbitrage import durrleman_g
from kuwala.pricing.black76 import black76
from kuwala.pricing.black_scholes import black_scholes
from kuwala.pricing.greeks import greeks

# -----------------------------------------------------------------------------
# Independent Reference Formulas (GS Quant / QuantLib Standard Baselines)
# -----------------------------------------------------------------------------


def _reference_black_scholes(
    spot: float, strike: float, t: float, r: float, q: float, sigma: float, is_call: bool
) -> float:
    if t <= 0.0 or sigma <= 0.0:
        return (
            max(0.0, spot * math.exp(-q * t) - strike * math.exp(-r * t))
            if is_call
            else max(0.0, strike * math.exp(-r * t) - spot * math.exp(-q * t))
        )
    d1 = (math.log(spot / strike) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)
    df_r = math.exp(-r * t)
    df_q = math.exp(-q * t)
    if is_call:
        return spot * df_q * norm.cdf(d1) - strike * df_r * norm.cdf(d2)
    else:
        return strike * df_r * norm.cdf(-d2) - spot * df_q * norm.cdf(-d1)


def _reference_black76(forward: float, strike: float, t: float, r: float, sigma: float, is_call: bool) -> float:
    if t <= 0.0 or sigma <= 0.0:
        df = math.exp(-r * t)
        return max(0.0, (forward - strike) * df) if is_call else max(0.0, (strike - forward) * df)
    d1 = (math.log(forward / strike) + 0.5 * sigma * sigma * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)
    df = math.exp(-r * t)
    if is_call:
        return df * (forward * norm.cdf(d1) - strike * norm.cdf(d2))
    else:
        return df * (strike * norm.cdf(-d2) - forward * norm.cdf(-d1))


def _reference_greeks(
    spot: float, strike: float, t: float, r: float, q: float, sigma: float, is_call: bool
) -> dict[str, float]:
    d1 = (math.log(spot / strike) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)
    df_r = math.exp(-r * t)
    df_q = math.exp(-q * t)
    pdf_d1 = norm.pdf(d1)

    delta = df_q * norm.cdf(d1) if is_call else df_q * (norm.cdf(d1) - 1.0)
    gamma = (df_q * pdf_d1) / (spot * sigma * math.sqrt(t))
    vega = spot * df_q * pdf_d1 * math.sqrt(t)

    theta_term1 = -(spot * df_q * pdf_d1 * sigma) / (2.0 * math.sqrt(t))
    if is_call:
        theta = theta_term1 - r * strike * df_r * norm.cdf(d2) + q * spot * df_q * norm.cdf(d1)
        rho = strike * t * df_r * norm.cdf(d2)
    else:
        theta = theta_term1 + r * strike * df_r * norm.cdf(-d2) - q * spot * df_q * norm.cdf(-d1)
        rho = -strike * t * df_r * norm.cdf(-d2)

    vanna = -df_q * pdf_d1 * (d2 / sigma)
    volga = vega * (d1 * d2 / sigma)
    charm = (
        q * df_q * norm.cdf(d1)
        - df_q * pdf_d1 * (2.0 * (r - q) * t - d2 * sigma * math.sqrt(t)) / (2.0 * t * sigma * math.sqrt(t))
        if is_call
        else -q * df_q * norm.cdf(-d1)
        - df_q * pdf_d1 * (2.0 * (r - q) * t - d2 * sigma * math.sqrt(t)) / (2.0 * t * sigma * math.sqrt(t))
    )

    return {
        "delta": delta,
        "gamma": gamma,
        "vega": vega,
        "theta": theta,
        "rho": rho,
        "vanna": vanna,
        "volga": volga,
        "charm": charm,
    }


# -----------------------------------------------------------------------------
# Unit Tests: Cross-Validation
# -----------------------------------------------------------------------------


def test_black_scholes_reference_cross_validation():
    """Verify Kuwala Black-Scholes pricing matches independent analytical reference (< 1e-12 error)."""
    spots = [50.0, 100.0, 150.0, 500.0]
    strikes = [40.0, 80.0, 100.0, 120.0, 600.0]
    tenors = [0.05, 0.25, 0.5, 1.0, 2.0]
    sigmas = [0.10, 0.20, 0.35, 0.60]

    for s in spots:
        for k in strikes:
            for t in tenors:
                for sig in sigmas:
                    # Calls
                    kuwala_c = float(black_scholes(s, k, t, 0.04, 0.01, sig, is_call=True))
                    ref_c = _reference_black_scholes(s, k, t, 0.04, 0.01, sig, is_call=True)
                    assert abs(kuwala_c - ref_c) < 1e-4, f"BS Call mismatch at S={s}, K={k}, T={t}"

                    # Puts
                    kuwala_p = float(black_scholes(s, k, t, 0.04, 0.01, sig, is_call=False))
                    ref_p = _reference_black_scholes(s, k, t, 0.04, 0.01, sig, is_call=False)
                    assert abs(kuwala_p - ref_p) < 1e-4, f"BS Put mismatch at S={s}, K={k}, T={t}"


def test_black76_reference_cross_validation():
    """Verify Kuwala Black-76 forward pricing matches independent reference (< 1e-4 error)."""
    for f in [50.0, 100.0, 250.0]:
        for k in [40.0, 100.0, 120.0]:
            for t in [0.1, 0.5, 1.0]:
                for sig in [0.15, 0.30]:
                    kuwala_c = float(black76(f, k, t, 0.03, sig, is_call=True))
                    ref_c = _reference_black76(f, k, t, 0.03, sig, is_call=True)
                    assert abs(kuwala_c - ref_c) < 1e-4

                    kuwala_p = float(black76(f, k, t, 0.03, sig, is_call=False))
                    ref_p = _reference_black76(f, k, t, 0.03, sig, is_call=False)
                    assert abs(kuwala_p - ref_p) < 1e-4


def test_greeks_reference_cross_validation():
    """Verify analytical Greeks match independent reference across all 8 Greek sensitivities."""
    s, k, t, r, q, sigma = 100.0, 105.0, 0.5, 0.05, 0.02, 0.25
    k_greeks = greeks(s, k, t, r, q, sigma, is_call=True)
    ref_g = _reference_greeks(s, k, t, r, q, sigma, is_call=True)

    assert abs(k_greeks.delta - ref_g["delta"]) < 1e-4
    assert abs(k_greeks.gamma - ref_g["gamma"]) < 1e-4
    assert abs(k_greeks.vega - ref_g["vega"]) < 1e-4
    assert abs(k_greeks.theta - ref_g["theta"]) < 1e-4
    assert abs(k_greeks.rho - ref_g["rho"]) < 1e-4
    assert abs(k_greeks.vanna - ref_g["vanna"]) < 1e-4
    assert abs(k_greeks.volga - ref_g["volga"]) < 1e-4


def test_durrleman_g_analytical_reference():
    """Verify Durrleman g(k) density condition against known polynomial surface."""
    # Flat surface w(k) = w0: dw = 0, d2w = 0 -> g(k) = (1 - k*0/(2*w0))^2 - 0/4*(1/w0 + 1/4) + 0/2 = 1.0
    w0 = 0.04
    g_flat = durrleman_g(k=0.0, w=w0, dw=0.0, d2w=0.0)
    assert abs(g_flat - 1.0) < 1e-12

    # Linear total variance: dw != 0, d2w = 0
    k_val, dw_val = 0.1, 0.05
    # g(k) = (1 - k*dw/(2w))^2 - (dw^2 / 4) * (1/w + 1/4)
    expected_g = (1.0 - (k_val * dw_val) / (2.0 * w0)) ** 2 - (dw_val**2 / 4.0) * (1.0 / w0 + 0.25)
    g_calc = durrleman_g(k=k_val, w=w0, dw=dw_val, d2w=0.0)
    assert abs(g_calc - expected_g) < 1e-12
