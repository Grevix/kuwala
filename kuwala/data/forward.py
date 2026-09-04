"""
Synthetic Forward Curve & Discrete Dividend Schedule Extraction.
Extracts continuous forward curves F(T) and dividend yields q(T) via Put-Call parity regression.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.interpolate import interp1d

from kuwala.data.curves import FlatYieldCurve, YieldCurve
from kuwala.data.models import OptionChain, OptionType


@dataclass(frozen=True)
class DividendEvent:
    """Discrete dividend corporate action payment."""

    ex_date: str
    amount: float
    tenor: float  # Time to ex-date in years


class ForwardCurve:
    """
    Arbitrage-consistent Forward Curve F(T) = S0 * exp((r(T) - q(T)) * T)
    or F(T) = (S0 - sum(PV(D_i))) * exp(r(T) * T) for discrete dividends.
    """

    def __init__(
        self,
        spot: float,
        yield_curve: YieldCurve,
        tenors: Sequence[float],
        forwards: Sequence[float],
        dividends: Sequence[DividendEvent] | None = None,
    ):
        self.spot = float(spot)
        self.yield_curve = yield_curve
        self.tenors = np.asarray(tenors, dtype=np.float64)
        self.forwards = np.asarray(forwards, dtype=np.float64)
        self.dividends = list(dividends or [])

        # Sort tenors
        idx = np.argsort(self.tenors)
        self.tenors = self.tenors[idx]
        self.forwards = self.forwards[idx]

        if len(self.tenors) >= 2:
            self._interpolator = interp1d(self.tenors, self.forwards, kind="linear", fill_value="extrapolate")
        else:
            self._interpolator = None

    def forward_price(self, t: float) -> float:
        """Evaluate forward price F(T) for tenor t."""
        if t <= 0.0:
            return self.spot
        if self._interpolator is not None:
            return float(self._interpolator(t))
        if len(self.forwards) == 1:
            return float(self.forwards[0])
        # Default continuous forward
        r = self.yield_curve.zero_rate(t)
        return float(self.spot * np.exp(r * t))

    def implied_dividend_yield(self, t: float) -> float:
        """Effective continuous dividend yield q(T) matching forward price F(T)."""
        if t <= 1e-4:
            return 0.0
        f = self.forward_price(t)
        r = self.yield_curve.zero_rate(t)
        # F(T) = S0 * exp((r - q)*T)  =>  (r - q)*T = ln(F/S0)  =>  q = r - (1/T)*ln(F/S0)
        return float(r - (1.0 / t) * np.log(max(1e-4, f / self.spot)))


def extract_forward_from_chain(
    chain: OptionChain,
    yield_curve: YieldCurve | None = None,
) -> ForwardCurve:
    """
    Robust Put-Call Parity forward price extraction:
    C(K, T) - P(K, T) = D(T) * (F(T) - K) = D(T)*F(T) - D(T)*K
    Regressing (C - P) on K yields intercept = D(T)*F(T) and slope = -D(T).
    """
    if yield_curve is None:
        yield_curve = FlatYieldCurve(chain.rate)

    spot = chain.spot
    calls_by_exp: dict[str, dict[float, float]] = {}
    puts_by_exp: dict[str, dict[float, float]] = {}

    for q in chain.quotes:
        if q.bid is not None and q.ask is not None and q.bid > 0 and q.ask > q.bid:
            mid = 0.5 * (q.bid + q.ask)
        elif q.last is not None and q.last > 0:
            mid = q.last
        else:
            continue

        exp = q.expiry
        k = q.strike
        if q.option_type == OptionType.CALL:
            calls_by_exp.setdefault(exp, {})[k] = mid
        else:
            puts_by_exp.setdefault(exp, {})[k] = mid

    tenor_list = []
    forward_list = []

    for exp, calls in calls_by_exp.items():
        puts = puts_by_exp.get(exp, {})
        common_strikes = sorted(set(calls.keys()) & set(puts.keys()))
        if len(common_strikes) < 2:
            continue

        # Filter near ATM strikes to avoid liquidity bias
        atm_strikes = [k for k in common_strikes if 0.8 * spot <= k <= 1.2 * spot]
        if len(atm_strikes) < 2:
            atm_strikes = common_strikes

        k_arr = np.array(atm_strikes)
        cp_diff = np.array([calls[k] - puts[k] for k in atm_strikes])

        # Linear regression: cp_diff = A - B * K  where A = D(T)*F(T), B = D(T)
        A, B = np.polyfit(k_arr, cp_diff, deg=1)  # cp_diff = slope * K + intercept
        slope = A
        intercept = B

        # D(T) = -slope, F(T) = intercept / D(T) = -intercept / slope
        if slope < -1e-4:
            f_est = -intercept / slope
            # Find tenor
            for q in chain.quotes:
                if q.expiry == exp:
                    from kuwala.data.conventions import year_fraction

                    tenor = year_fraction(q.timestamp, q.expiry)
                    break
            else:
                tenor = 0.25  # default
            if 0.5 * spot <= f_est <= 2.0 * spot and tenor > 0:
                tenor_list.append(tenor)
                forward_list.append(f_est)

    if not tenor_list:
        # Fallback to spot forward
        return ForwardCurve(spot, yield_curve, [0.25, 1.0], [spot, spot])

    return ForwardCurve(spot, yield_curve, tenor_list, forward_list)
