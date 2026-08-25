"""
Realized Volatility Estimators: Close-to-Close, Parkinson, Garman-Klass, Rogers-Satchell.
"""

from __future__ import annotations

from enum import Enum
from typing import Union

import numpy as np
import pandas as pd


class RealizedVolEstimator(str, Enum):
    CLOSE_TO_CLOSE = "close_to_close"
    PARKINSON = "parkinson"
    GARMAN_KLASS = "garman_klass"
    ROGERS_SATCHELL = "rogers_satchell"


def realized_volatility(
    df: pd.DataFrame,
    window: int = 20,
    estimator: Union[str, RealizedVolEstimator] = RealizedVolEstimator.GARMAN_KLASS,
    annualization_factor: float = 252.0,
) -> pd.Series:
    """
    Calculate rolling annualized realized volatility using the chosen estimator.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with datetime index or 'timestamp' column, containing 'open', 'high', 'low', 'close' (case-insensitive).
    window : int, default 20
        Rolling window in trading days.
    estimator : str or RealizedVolEstimator, default 'garman_klass'
        The estimator formula to apply.
    annualization_factor : float, default 252.0
        Trading days per year.

    Returns
    -------
    pd.Series
        Rolling annualized realized volatility.
    """
    data = df.copy()
    data.columns = [str(c).strip().lower() for c in data.columns]

    est = RealizedVolEstimator(estimator) if isinstance(estimator, str) else estimator

    if est == RealizedVolEstimator.CLOSE_TO_CLOSE:
        log_ret = np.log(data["close"] / data["close"].shift(1))
        rolling_std = log_ret.rolling(window=window).std()
        return rolling_std * np.sqrt(annualization_factor)

    elif est == RealizedVolEstimator.PARKINSON:
        # Parkinson (1980): uses High-Low
        # sigma^2 = (1 / (4 * ln(2))) * sum(ln(H/L)^2)
        factor = 1.0 / (4.0 * np.log(2.0))
        hl_term = np.log(data["high"] / data["low"]) ** 2
        rolling_var = factor * hl_term.rolling(window=window).mean()
        return np.sqrt(rolling_var * annualization_factor)

    elif est == RealizedVolEstimator.GARMAN_KLASS:
        # Garman-Klass (1980): uses Open-High-Low-Close
        # sigma^2 = 0.5 * ln(H/L)^2 - (2*ln(2) - 1) * ln(C/O)^2
        term1 = 0.5 * (np.log(data["high"] / data["low"]) ** 2)
        term2 = (2.0 * np.log(2.0) - 1.0) * (np.log(data["close"] / data["open"]) ** 2)
        rolling_var = (term1 - term2).rolling(window=window).mean()
        return np.sqrt(np.maximum(0.0, rolling_var) * annualization_factor)

    elif est == RealizedVolEstimator.ROGERS_SATCHELL:
        # Rogers-Satchell (1991): accounts for non-zero drift
        # u = ln(H/O), d = ln(L/O), c = ln(C/O)
        u = np.log(data["high"] / data["open"])
        d = np.log(data["low"] / data["open"])
        c = np.log(data["close"] / data["open"])
        rs_term = u * (u - c) + d * (d - c)
        rolling_var = rs_term.rolling(window=window).mean()
        return np.sqrt(np.maximum(0.0, rolling_var) * annualization_factor)

    else:
        raise ValueError(f"Unsupported estimator: {estimator}")
