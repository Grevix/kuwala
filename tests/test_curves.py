"""
Unit & Numerical Tests for Multi-Tenor Risk-Free Yield Curves.
"""

from __future__ import annotations

import numpy as np

from kuwala.data.curves import (
    CubicSplineCurve,
    FlatYieldCurve,
    NelsonSiegelCurve,
    bootstrap_treasury_curve,
)


def test_flat_yield_curve():
    curve = FlatYieldCurve(0.05)
    assert curve.zero_rate(0.5) == 0.05
    assert curve.zero_rate(10.0) == 0.05
    assert abs(curve.discount_factor(1.0) - np.exp(-0.05)) < 1e-12
    assert abs(curve.forward_rate(1.0, 2.0) - 0.05) < 1e-10


def test_cubic_spline_curve_interpolation():
    tenors = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
    yields = [0.052, 0.050, 0.046, 0.042, 0.040, 0.041]
    curve = CubicSplineCurve(tenors, yields)

    # Exact pillar matches
    for t, y in zip(tenors, yields):
        assert abs(curve.zero_rate(t) - y) < 1e-12

    # Smooth intermediate interpolation
    r_18m = curve.zero_rate(1.5)
    assert 0.040 <= r_18m <= 0.046

    # Discount factor monotonicity
    df1 = curve.discount_factor(1.0)
    df2 = curve.discount_factor(2.0)
    assert df1 > df2 > 0.0


def test_nelson_siegel_curve_fitting():
    tenors = [0.083, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0]
    # Inverted / humped yield curve typical of real markets
    yields = [0.054, 0.053, 0.051, 0.047, 0.042, 0.041, 0.040, 0.041, 0.042, 0.045, 0.046]

    ns = NelsonSiegelCurve.fit(tenors, yields)

    # Check that fitted rates are physically sensible
    for t in tenors:
        fitted = ns.zero_rate(t)
        assert 0.02 <= fitted <= 0.08

    # Discount factors are valid probabilities
    for t in [0.1, 0.5, 1.0, 5.0, 10.0]:
        df = ns.discount_factor(t)
        assert 0.0 < df <= 1.0


def test_bootstrap_treasury_curve_offline_and_online():
    curve = bootstrap_treasury_curve(method="nelson_siegel")
    assert curve.zero_rate(1.0) > 0.0
    assert 0.0 < curve.discount_factor(2.0) < 1.0

    spline_curve = bootstrap_treasury_curve(method="spline")
    assert spline_curve.zero_rate(0.5) > 0.0
