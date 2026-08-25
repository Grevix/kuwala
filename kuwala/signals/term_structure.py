"""
Term Structure Relative-Value Analytics.
"""

from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from kuwala.volatility.surface import VolatilitySurface


def term_structure_metrics(surface: VolatilitySurface) -> pd.DataFrame:
    """
    Extract ATM term structure slope, roll-down curvature, and forward variance across all tenors.
    """
    spot = surface.spot
    records = []

    for i, t in enumerate(surface.expiries):
        atm_iv = surface.implied_volatility(spot, t)
        total_var = (atm_iv ** 2) * t
        records.append({
            "tenor_years": t,
            "atm_iv": atm_iv,
            "total_variance": total_var,
        })

    df = pd.DataFrame(records)
    if len(df) > 1:
        df["fwd_variance"] = np.diff(df["total_variance"], prepend=0.0) / np.diff(df["tenor_years"], prepend=1e-5)
        df["fwd_vol"] = np.sqrt(np.maximum(0.0, df["fwd_variance"]))
        df["slope_to_next"] = np.diff(df["atm_iv"], append=np.nan)
    return df
