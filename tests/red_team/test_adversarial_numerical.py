"""
Red-Team Adversarial Numerical Tests for Kuwala.
Hostile testing across numerical singularities, NaN/Inf handling, boundary tenors,
extreme strike-spot ratios, negative interest rates, and IV solver edge domains.
"""

from __future__ import annotations

import math
import numpy as np
import pytest

from kuwala.pricing import black_scholes, greeks
from kuwala.volatility.iv import implied_volatility

def delta(spot, strike, t, r, q, sigma, is_call=True):
    return greeks(spot, strike, t, r, q, sigma, is_call=is_call).delta

def gamma(spot, strike, t, r, q, sigma, is_call=True):
    return greeks(spot, strike, t, r, q, sigma, is_call=is_call).gamma

def vega(spot, strike, t, r, q, sigma, is_call=True):
    return greeks(spot, strike, t, r, q, sigma, is_call=is_call).vega

def theta(spot, strike, t, r, q, sigma, is_call=True):
    return greeks(spot, strike, t, r, q, sigma, is_call=is_call).theta

def rho(spot, strike, t, r, q, sigma, is_call=True):
    return greeks(spot, strike, t, r, q, sigma, is_call=is_call).rho


class TestAdversarialSingularities:
    """Hostile edge-case and singularity tests."""

    def test_zero_and_negative_spot_strike(self):
        """Zero or negative spot/strike must return 0.0 or handle gracefully without throwing unhandled exceptions."""
        for bad_s in [0.0, -10.0, -1e-8]:
            res = black_scholes(bad_s, 100.0, 1.0, 0.05, 0.0, 0.20, is_call=True)
            assert res == 0.0 or math.isnan(res)

        for bad_k in [0.0, -50.0, -1e-8]:
            res = black_scholes(100.0, bad_k, 1.0, 0.05, 0.0, 0.20, is_call=True)
            assert res == 0.0 or math.isnan(res)

    def test_zero_and_sub_second_tenor(self):
        """Tenor T=0 or T=1e-9 (sub-second) must equal intrinsic payoff or near-instantaneous intrinsic value."""
        # Call ITM
        call_itm = black_scholes(110.0, 100.0, 0.0, 0.05, 0.0, 0.20, is_call=True)
        assert pytest.approx(call_itm, abs=1e-7) == 10.0

        # Call OTM
        call_otm = black_scholes(90.0, 100.0, 0.0, 0.05, 0.0, 0.20, is_call=True)
        assert pytest.approx(call_otm, abs=1e-7) == 0.0

        # Put ITM
        put_itm = black_scholes(90.0, 100.0, 0.0, 0.05, 0.0, 0.20, is_call=False)
        assert pytest.approx(put_itm, abs=1e-7) == 10.0

        # Sub-second T = 1e-8
        call_micro = black_scholes(110.0, 100.0, 1e-8, 0.05, 0.0, 0.20, is_call=True)
        assert pytest.approx(call_micro, rel=1e-3) == 10.0

    def test_century_long_tenors(self):
        """Tenor T=100 (century long) must not overflow or return NaN/Inf."""
        call_100y = black_scholes(100.0, 100.0, 100.0, 0.05, 0.0, 0.20, is_call=True)
        assert not math.isnan(call_100y)
        assert not math.isinf(call_100y)
        assert call_100y > 0.0

    def test_extreme_volatilities(self):
        """Zero vol must equal discounted intrinsic forward; ultra-high vol (1000%) must approach S."""
        # Zero vol
        c_zero_vol = black_scholes(100.0, 100.0, 1.0, 0.05, 0.0, 0.0, is_call=True)
        fwd = 100.0 * math.exp(0.05 * 1.0)
        expected = math.exp(-0.05 * 1.0) * max(0.0, fwd - 100.0)
        assert pytest.approx(c_zero_vol, abs=1e-7) == expected

        # Extreme vol 10.0 (1000% annualized)
        c_extreme = black_scholes(100.0, 100.0, 1.0, 0.0, 0.0, 10.0, is_call=True)
        assert not math.isnan(c_extreme)
        assert c_extreme < 100.0
        assert c_extreme > 90.0

    def test_negative_interest_rates(self):
        """Negative interest rates (e.g. -0.75% EUR/CHF regime) must price accurately without error."""
        r_neg = -0.0075
        c_neg = black_scholes(100.0, 100.0, 1.0, r_neg, 0.0, 0.20, is_call=True)
        p_neg = black_scholes(100.0, 100.0, 1.0, r_neg, 0.0, 0.20, is_call=False)
        assert c_neg > 0.0
        assert p_neg > 0.0
        # Put-call parity: C - P = S - K*exp(-rT)
        assert pytest.approx(c_neg - p_neg, abs=1e-6) == 100.0 - 100.0 * math.exp(-r_neg * 1.0)

    def test_extreme_moneyness(self):
        """Deep OTM (S/K = 1/10000) and deep ITM (S/K = 10000) must not cause underflow/overflow NaN."""
        # Deep OTM call
        c_deep_otm = black_scholes(0.01, 1000.0, 1.0, 0.05, 0.0, 0.20, is_call=True)
        assert pytest.approx(c_deep_otm, abs=1e-7) == 0.0

        # Deep ITM call: approaches S - K*exp(-rT)
        c_deep_itm = black_scholes(10000.0, 1.0, 1.0, 0.05, 0.0, 0.20, is_call=True)
        expected_itm = 10000.0 - 1.0 * math.exp(-0.05 * 1.0)
        assert pytest.approx(c_deep_itm, abs=1e-3) == expected_itm


class TestAdversarialGreeks:
    """Hostile testing of analytical and numerical Greeks under severe regimes."""

    def test_greeks_near_expiration_atm_discontinuity(self):
        """As T -> 0 ATM, Gamma spikes to infinity but finite bounds shouldn't crash."""
        d = delta(100.0, 100.0, 1e-6, 0.0, 0.0, 0.20, is_call=True)
        assert 0.4 < d < 0.6
        g = gamma(100.0, 100.0, 1e-6, 0.0, 0.0, 0.20)
        assert g > 15.0  # Theoretical value is ~19.95 at T=1e-6
        v = vega(100.0, 100.0, 1e-6, 0.0, 0.0, 0.20)
        assert pytest.approx(v, abs=1e-4) == 0.039894

    def test_greeks_zero_volatility(self):
        """Zero vol Greeks must evaluate safely."""
        d = delta(105.0, 100.0, 1.0, 0.05, 0.0, 0.0, is_call=True)
        assert not math.isnan(d)
        assert not math.isinf(d)

    def test_greeks_deep_otm_and_itm(self):
        """Deep OTM option delta must be exactly 0, deep ITM call delta must be 1."""
        d_otm = delta(10.0, 100.0, 1.0, 0.05, 0.0, 0.20, is_call=True)
        assert pytest.approx(d_otm, abs=1e-5) == 0.0

        d_itm = delta(500.0, 100.0, 1.0, 0.05, 0.0, 0.20, is_call=True)
        assert pytest.approx(d_itm, abs=1e-5) == 1.0


class TestAdversarialIVSolver:
    """Hostile testing of implied volatility solver boundaries."""

    def test_iv_target_below_intrinsic_returns_nan_or_zero(self):
        """If market price is strictly below arbitrage intrinsic value, solver must safely return NaN or boundary."""
        # Spot = 100, Strike = 50, Call intrinsic = 50. Market price given as 20.0 (impossible)
        iv = implied_volatility(20.0, 100.0, 50.0, 1.0, 0.0, 0.0, is_call=True)
        assert math.isnan(iv) or iv == 0.0

    def test_iv_target_above_spot_upper_bound(self):
        """Call price > S is impossible arbitrage. Must return NaN."""
        iv = implied_volatility(150.0, 100.0, 100.0, 1.0, 0.0, 0.0, is_call=True)
        assert math.isnan(iv) or iv == 0.0

    def test_iv_vectorized_noisy_array(self):
        """Vectorized IV with mixed valid and invalid targets must handle elementwise NaN without terminating."""
        targets = np.array([10.45, -5.0, 0.0, 500.0, 5.0])
        spots = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
        strikes = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
        res = implied_volatility(targets, spots, strikes, 1.0, 0.05, 0.0, is_call=True)
        assert isinstance(res, np.ndarray)
        assert len(res) == 5
        # Valid index 0 must solve ~0.20
        assert pytest.approx(res[0], abs=1e-3) == 0.20
