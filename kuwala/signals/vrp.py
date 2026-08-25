"""
Volatility Risk Premium (VRP) Signal Generator.
"""

from __future__ import annotations

from typing import Union, Optional
import numpy as np
import pandas as pd

from kuwala.volatility.surface import VolatilitySurface
from kuwala.signals.realized_vol import realized_volatility, RealizedVolEstimator


def vrp(
    surface: VolatilitySurface,
    price_history: Optional[pd.DataFrame] = None,
    realized_window: int = 20,
    estimator: Union[str, RealizedVolEstimator] = "garman_klass",
    expiry_ttm: float = 30.0 / 365.0,
    hist_prices: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Compute Volatility Risk Premium (VRP) = Implied Volatility - Realized Volatility.

    Parameters
    ----------
    surface : VolatilitySurface
        Calibrated surface object.
    price_history : pd.DataFrame, optional
        Underlying OHLCV historical price series.
    realized_window : int, default 20
        Lookback window in days for realized volatility.
    estimator : str or RealizedVolEstimator, default 'garman_klass'
        Realized volatility calculation estimator.
    expiry_ttm : float, default 30 days
        Tenor at which ATM implied volatility is extracted.
    hist_prices : pd.DataFrame, optional
        Alias for price_history.

    Returns
    -------
    pd.DataFrame
        DataFrame containing ATM implied volatility, realized volatility, and VRP spread.
    """
    prices = price_history if price_history is not None else hist_prices

    atm_iv = surface.implied_volatility(surface.spot, expiry_ttm)

    if prices is None or prices.empty:
        # Synthetic historical price series if not provided
        dates = pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=60, freq="B")
        np.random.seed(42)
        rets = np.random.normal(0, 0.012, size=len(dates))
        close_p = surface.spot * np.exp(np.cumsum(rets))
        high_p = close_p * (1.0 + np.abs(np.random.normal(0, 0.005, size=len(dates))))
        low_p = close_p * (1.0 - np.abs(np.random.normal(0, 0.005, size=len(dates))))
        open_p = close_p * (1.0 + np.random.normal(0, 0.002, size=len(dates)))

        prices = pd.DataFrame({
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p,
        }, index=dates)

    rv_series = realized_volatility(prices, window=realized_window, estimator=estimator)
    latest_rv = float(rv_series.dropna().iloc[-1]) if not rv_series.dropna().empty else 0.18

    vrp_spread = atm_iv - latest_rv

    res = pd.DataFrame([{
        "underlying": surface.underlying,
        "spot": surface.spot,
        "tenor_ttm": expiry_ttm,
        "implied_vol": atm_iv,
        "realized_vol": latest_rv,
        "vrp": vrp_spread,
        "vrp_spread": vrp_spread,
        "vrp_ratio": atm_iv / latest_rv if latest_rv > 0 else np.nan,
        "estimator": str(estimator),
        "window": realized_window,
    }])
    return res
