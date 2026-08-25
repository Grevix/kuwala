"""
Test suite validating that all code snippets presented in README.md execute without error.
"""

from datetime import datetime, timedelta, timezone
import pytest
import numpy as np
import pandas as pd
import kuwala
from kuwala.pricing.black_scholes import black_scholes
from kuwala.volatility.surface import SsviSurface
from kuwala.data.models import OptionQuote, OptionChain, OptionType
from kuwala.signals import vrp
from kuwala.backtest.vectorbt import to_vectorbt


def test_readme_quickstart_offline_mock():
    # Construct a valid, real-shaped chain
    now = datetime.now(timezone.utc)
    spot = 500.0
    rate = 0.045
    div_yield = 0.015
    quotes = []
    
    for days in [30, 60, 90]:
        ttm = days / 365.0
        expiry = now + timedelta(days=days)
        for strike in [470.0, 485.0, 500.0, 515.0, 530.0]:
            p_call = float(black_scholes(spot, strike, ttm, rate, div_yield, 0.20, is_call=True))
            quotes.append(
                OptionQuote(
                    underlying="SPY",
                    expiry=expiry,
                    strike=strike,
                    option_type=OptionType.CALL,
                    bid=max(0.01, p_call - 0.10),
                    ask=p_call + 0.10,
                    mid=p_call,
                    last=p_call,
                    volume=1000,
                    open_interest=5000,
                    timestamp=now,
                )
            )

    chain = OptionChain(
        underlying="SPY",
        spot=spot,
        rate=rate,
        dividend_yield=div_yield,
        quotes=quotes,
        timestamp=now,
    )

    # 1. Fit Gatheral-Jacquier SSVI arbitrage-checked surface
    surface = SsviSurface.calibrate(chain)

    # 2. Inspect diagnostics (never a silent boolean)
    report = surface.diagnostics()
    summary = report.summary()
    assert isinstance(summary, str)
    assert report.butterfly_passed is True
    assert report.calendar_passed is True

    # 3. Extract local volatility & Volatility Risk Premium (VRP)
    local_vol = surface.local_vol()
    assert not np.any(np.isnan(local_vol))

    # Mock 40-day price history
    dates = pd.date_range("2025-01-01", periods=40, freq="B")
    hist_prices = pd.DataFrame(
        {
            "open": np.linspace(480, 500, 40),
            "high": np.linspace(485, 505, 40),
            "low": np.linspace(475, 495, 40),
            "close": np.linspace(480, 500, 40),
            "volume": 1000000,
        },
        index=dates,
    )

    vrp_df = vrp(surface, hist_prices=hist_prices, realized_window=20)
    assert "vrp" in vrp_df.columns

    # 4. Export to VectorBT backtest connector
    vbt_signals = to_vectorbt(vrp_df)
    assert "entries" in vbt_signals
    assert "exits" in vbt_signals
    assert "price" in vbt_signals
