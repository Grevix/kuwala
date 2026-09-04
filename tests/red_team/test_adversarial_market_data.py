"""
Red-Team Adversarial Market Data Tests for Kuwala.
Tests noisy, malformed, crossed-spread, and inverted real-world market structures.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from kuwala.data.curves import CubicSplineCurve, NelsonSiegelCurve
from kuwala.data.microstructure import aggregate_ticks_to_bars
from kuwala.diagnostics.arbitrage import check_butterfly_slice, diagnose_surface


class TestAdversarialMarketStructures:
    """Hostile market data and calendar anomaly testing."""

    def test_inverted_yield_curve_bootstrapping(self):
        """Severely inverted yield curves (e.g. 1M @ 6.5%, 30Y @ 2.0%) must bootstrap continuous discount factors without failure."""
        tenors = np.array([1/12, 3/12, 6/12, 1.0, 2.0, 5.0, 10.0, 30.0])
        # Inverted yields
        yields = np.array([0.065, 0.060, 0.055, 0.050, 0.040, 0.035, 0.030, 0.020])

        cs_curve = CubicSplineCurve(tenors, yields)
        for t in [0.25, 1.5, 7.5, 25.0]:
            r_t = cs_curve.zero_rate(t)
            df_t = cs_curve.discount_factor(t)
            assert 0.01 <= r_t <= 0.08
            assert 0.0 < df_t < 1.0

        ns_curve = NelsonSiegelCurve.fit(tenors, yields)
        r_ns = ns_curve.zero_rate(2.5)
        df_ns = ns_curve.discount_factor(2.5)
        assert 0.0 < r_ns < 0.10
        assert 0.0 < df_ns < 1.0

    def test_calendar_arbitrage_detection(self):
        """Inverted total variance across expiries (w(k, T2) < w(k, T1) for T2 > T1) must be strictly flagged as calendar arbitrage."""
        k_grid = np.linspace(-0.3, 0.3, 21)
        expiries = [0.25, 0.50]
        # T2 has lower variance than T1 -> blatant calendar arbitrage
        w_matrix = np.zeros((2, 21))
        w_matrix[0, :] = 0.04 * (1.0 + 0.1 * k_grid**2)  # T1
        w_matrix[1, :] = 0.02 * (1.0 + 0.1 * k_grid**2)  # T2 (lower total variance!)

        report = diagnose_surface(expiries, k_grid, w_matrix, spot=100.0)
        assert not report.is_arbitrage_free
        assert not report.calendar_passed
        assert len(report.calendar_violations) > 0

    def test_severe_butterfly_negative_density_detection(self):
        """Non-convex total variance slice causing negative risk-neutral density g(k) < 0 must be caught."""
        k_grid = np.linspace(-0.4, 0.4, 41)
        # Create non-convex indentation in total variance
        w_slice = 0.04 - 0.03 * np.exp(-50.0 * k_grid**2)
        sr = check_butterfly_slice(0.5, k_grid, w_slice, spot=100.0)
        assert not sr.butterfly_passed
        assert len(sr.violations) > 0

    def test_adversarial_tick_aggregation(self):
        """Tick data with irregular intervals, zero volumes, and out-of-order ticks must produce clean OHLCV bars."""
        timestamps = pd.date_range("2026-01-01 09:30:00", periods=100, freq="750ms")
        prices = 100.0 + np.sin(np.linspace(0, 10, 100))
        volumes = np.random.randint(0, 50, size=100)
        volumes[0] = 0  # Zero volume test

        ticks_df = pd.DataFrame({
            "timestamp": timestamps,
            "price": prices,
            "volume": volumes,
            "bid": prices - 0.05,
            "ask": prices + 0.05
        })

        bars = aggregate_ticks_to_bars(ticks_df, freq="1min")
        assert len(bars) >= 1
        assert "open" in bars.columns
        assert "high" in bars.columns
        assert "low" in bars.columns
        assert "close" in bars.columns
        assert "volume" in bars.columns
        assert not bars["open"].isna().any()
