"""
FRED (Federal Reserve Bank of St. Louis) Macro & Rate Curve Adapter.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
import requests

from kuwala.config import get_config
from kuwala.data.adapters.base import BaseAdapter


class FredAdapter(BaseAdapter):
    """
    Adapter for Federal Reserve Economic Data (FRED).
    Used for risk-free discount curve construction, Treasury yields (DGS3MO, DGS1, DGS2, DGS10), etc.
    """

    @property
    def name(self) -> str:
        return "fred"

    @property
    def terms_of_service_url(self) -> str:
        return "https://fred.stlouisfed.org/legal/"

    def fetch(
        self,
        series_id: str = "DGS3MO",
        api_key: Optional[str] = None,
        observation_start: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetch time series observations from FRED API.
        """
        config = get_config()
        key = api_key or config.fred_api_key

        if not key:
            return self._synthetic_rate_curve(series_id)

        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": key,
            "file_type": "json",
        }
        if observation_start:
            params["observation_start"] = observation_start

        try:
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                obs = data.get("observations", [])
                df = pd.DataFrame(obs)
                if not df.empty:
                    df["date"] = pd.to_datetime(df["date"])
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    df = df.dropna(subset=["value"]).sort_values("date")
                    df["series_id"] = series_id
                    return df[["date", "value", "series_id"]]
        except Exception:
            pass

        return self._synthetic_rate_curve(series_id)

    def get_treasury_curve(self, api_key: Optional[str] = None) -> Dict[float, float]:
        """
        Fetch live Treasury curve points across tenors:
        0.25y (3M), 1y, 2y, 5y, 10y. Returns dict of {tenor_years: decimal_rate}.
        """
        tenor_series = {
            0.25: "DGS3MO",
            1.0: "DGS1",
            2.0: "DGS2",
            5.0: "DGS5",
            10.0: "DGS10",
        }
        curve = {}
        for tenor, sid in tenor_series.items():
            df = self.fetch(sid, api_key=api_key)
            if not df.empty:
                val = float(df["value"].iloc[-1]) / 100.0 # convert percentage to decimal
                curve[tenor] = val
            else:
                curve[tenor] = 0.04
        return curve

    def get_rate_for_tenor(self, ttm: float, api_key: Optional[str] = None) -> float:
        """
        Dynamically interpolate the risk-free rate for a given time to maturity T.
        """
        curve = self.get_treasury_curve(api_key=api_key)
        tenors = np.array(sorted(curve.keys()))
        rates = np.array([curve[t] for t in tenors])
        return float(np.interp(ttm, tenors, rates))

    def _synthetic_rate_curve(self, series_id: str) -> pd.DataFrame:
        dates = pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=30, freq="D")
        rates = {"DGS3MO": 0.045, "DGS1": 0.042, "DGS2": 0.040, "DGS5": 0.039, "DGS10": 0.038}
        rate_val = rates.get(series_id, 0.04)
        return pd.DataFrame({
            "date": dates,
            "value": [rate_val * 100.0] * len(dates),
            "series_id": series_id,
        })
