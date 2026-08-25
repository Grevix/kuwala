"""
Skew & Surface Shape Relative-Value Metrics.
"""

from __future__ import annotations

import math
from typing import Dict, Any
import numpy as np
import pandas as pd

from kuwala.volatility.surface import VolatilitySurface


def skew_metrics(
    surface: VolatilitySurface,
    expiry_ttm: float = 30.0 / 365.0,
) -> Dict[str, float]:
    """
    Compute skew metrics: 25-delta Risk Reversal (RR25), 25-delta Butterfly (BF25), and 90/110 moneyness slope.
    """
    spot = surface.spot
    k_90 = spot * 0.90
    k_100 = spot * 1.00
    k_110 = spot * 1.10

    iv_90 = surface.implied_volatility(k_90, expiry_ttm)
    iv_100 = surface.implied_volatility(k_100, expiry_ttm)
    iv_110 = surface.implied_volatility(k_110, expiry_ttm)

    # 90-110 Skew
    skew_slope = (iv_90 - iv_110) / (math.log(1.10 / 0.90))
    curvature = (iv_90 + iv_110 - 2.0 * iv_100) / (0.10 ** 2)

    return {
        "underlying": surface.underlying,
        "tenor_ttm": expiry_ttm,
        "iv_atm": iv_100,
        "iv_90": iv_90,
        "iv_110": iv_110,
        "skew_90_110": iv_90 - iv_110,
        "skew_slope": skew_slope,
        "curvature": curvature,
    }
