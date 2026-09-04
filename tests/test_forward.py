"""
Unit Tests for Synthetic Forward Curve & Put-Call Parity Regression.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from kuwala.data.curves import FlatYieldCurve
from kuwala.data.forward import ForwardCurve, extract_forward_from_chain
from kuwala.data.models import OptionChain, OptionQuote, OptionType
from kuwala.pricing.black_scholes import black_scholes


def test_forward_curve_interpolation():
    curve = FlatYieldCurve(0.04)
    fc = ForwardCurve(
        spot=100.0,
        yield_curve=curve,
        tenors=[0.25, 0.5, 1.0],
        forwards=[100.5, 101.2, 102.8],
    )

    assert abs(fc.forward_price(0.0) - 100.0) < 1e-10
    assert abs(fc.forward_price(0.25) - 100.5) < 1e-10
    assert abs(fc.forward_price(1.0) - 102.8) < 1e-10

    # Implied dividend yield calculation
    q_1y = fc.implied_dividend_yield(1.0)
    assert abs(q_1y - 0.012375) < 1e-4


def test_extract_forward_from_synthetic_chain():
    spot = 500.0
    rate = 0.05
    div_yield = 0.015
    tenor = 0.5
    vol = 0.20
    now_dt = datetime(2026, 1, 1, 16, 0, 0, tzinfo=timezone.utc)
    exp_dt = datetime(2026, 7, 2, 16, 0, 0, tzinfo=timezone.utc)

    quotes = []
    strikes = [450.0, 480.0, 500.0, 520.0, 550.0]
    for k in strikes:
        c_px = black_scholes(spot, k, tenor, rate, div_yield, vol, is_call=True)
        p_px = black_scholes(spot, k, tenor, rate, div_yield, vol, is_call=False)

        quotes.append(
            OptionQuote(
                underlying="SPY",
                strike=k,
                expiry=exp_dt,
                option_type=OptionType.CALL,
                bid=c_px - 0.05,
                ask=c_px + 0.05,
                mid=c_px,
                last=c_px,
                timestamp=now_dt,
            )
        )
        quotes.append(
            OptionQuote(
                underlying="SPY",
                strike=k,
                expiry=exp_dt,
                option_type=OptionType.PUT,
                bid=p_px - 0.05,
                ask=p_px + 0.05,
                mid=p_px,
                last=p_px,
                timestamp=now_dt,
            )
        )

    chain = OptionChain(
        underlying="SPY",
        spot=spot,
        quotes=quotes,
        rate=rate,
        dividend_yield=div_yield,
        timestamp=now_dt,
    )

    f_curve = extract_forward_from_chain(chain)
    f_extracted = f_curve.forward_price(tenor)
    f_expected = spot * np.exp((rate - div_yield) * tenor)

    # Check forward price matches within bid-ask spread resolution
    assert abs(f_extracted - f_expected) < 0.25
