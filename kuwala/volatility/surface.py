"""
First-Class Volatility Surface Research Objects.
"""

from __future__ import annotations

import math
from typing import List, Optional, Union

import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator, interp1d

from kuwala.data.models import OptionChain
from kuwala.diagnostics.arbitrage import diagnose_surface
from kuwala.diagnostics.report import DiagnosticReport
from kuwala.pricing.greeks import OptionGreeks, greeks
from kuwala.volatility.iv import extract_chain_iv
from kuwala.volatility.local_vol import extract_dupire_local_volatility
from kuwala.volatility.ssvi import (
    CalibrationConfig,
    SsviParameters,
    calibrate_ssvi,
)


class VolatilitySurface:
    """
    Base representation of an arbitrage-checked Implied Volatility Surface.
    """

    def __init__(
        self,
        underlying: str,
        spot: float,
        expiries: List[float],
        k_grid: np.ndarray,
        w_matrix: np.ndarray,
        rate: float = 0.04,
        dividend_yield: float = 0.0,
    ):
        self.underlying = underlying
        self.spot = spot
        self.expiries = sorted(expiries)
        self.k_grid = np.asarray(k_grid, dtype=np.float64)
        self.w_matrix = np.asarray(w_matrix, dtype=np.float64)
        self.rate = rate
        self.dividend_yield = dividend_yield

    @property
    def iv_matrix(self) -> np.ndarray:
        """Implied volatility grid sigma(k, T) = sqrt(w(k, T) / T)."""
        t_col = np.array(self.expiries)[:, np.newaxis]
        return np.sqrt(np.maximum(1e-8, self.w_matrix / np.maximum(1e-5, t_col)))

    def diagnostics(self) -> DiagnosticReport:
        """
        Run full butterfly (Durrleman second derivative) and calendar arbitrage diagnostics.
        """
        return diagnose_surface(
            expiries=self.expiries,
            k_grid=self.k_grid,
            w_matrix=self.w_matrix,
            spot=self.spot,
        )

    def local_vol(self) -> np.ndarray:
        """
        Extract Dupire local volatility matrix sigma_loc(k, T).
        """
        if len(self.expiries) < 2:
            # Single tenor: fallback to instantaneous implied vol slice
            return self.iv_matrix.copy()

        return extract_dupire_local_volatility(
            k_grid=self.k_grid,
            expiries=np.array(self.expiries),
            w_matrix=self.w_matrix,
        )

    def implied_volatility(self, strike: float, expiry_ttm: float) -> float:
        """Interpolate implied volatility at a specific strike and tenor."""
        forward = self.spot * math.exp((self.rate - self.dividend_yield) * expiry_ttm)
        k = math.log(strike / forward) if forward > 0 and strike > 0 else 0.0

        if len(self.expiries) == 1:
            # 1D interpolation
            f = interp1d(self.k_grid, self.iv_matrix[0, :], bounds_error=False, fill_value="extrapolate")
            return float(f(k))

        # 2D bilinear interpolation
        interp = RegularGridInterpolator(
            (self.expiries, self.k_grid),
            self.iv_matrix,
            bounds_error=False,
            fill_value=None,
        )
        return float(interp([[expiry_ttm, k]])[0])

    def greeks(self, strike: float, expiry_ttm: float, is_call: bool = True) -> OptionGreeks:
        """Calculate option Greeks on the surface."""
        iv = self.implied_volatility(strike, expiry_ttm)
        return greeks(
            spot=self.spot,
            strike=strike,
            t=expiry_ttm,
            r=self.rate,
            q=self.dividend_yield,
            sigma=iv,
            is_call=is_call,
        )

    def shock(self, parallel_vol_bump: float = 0.01, spot_pct_bump: float = 0.0) -> VolatilitySurface:
        """Apply scenario shocks (parallel vol shifts, spot shifts)."""
        new_spot = self.spot * (1.0 + spot_pct_bump)
        new_iv = np.maximum(0.01, self.iv_matrix + parallel_vol_bump)
        t_col = np.array(self.expiries)[:, np.newaxis]
        new_w = (new_iv**2) * t_col
        return VolatilitySurface(
            underlying=self.underlying,
            spot=new_spot,
            expiries=self.expiries,
            k_grid=self.k_grid,
            w_matrix=new_w,
            rate=self.rate,
            dividend_yield=self.dividend_yield,
        )

    def plot(self, show: bool = True) -> None:
        """Plot the 3D implied volatility surface."""
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection="3d")
        K, T = np.meshgrid(self.k_grid, self.expiries)
        surf = ax.plot_surface(K, T, self.iv_matrix, cmap="viridis", edgecolor="none", alpha=0.9)
        ax.set_title(f"Kuwala Calibrated Volatility Surface ({self.underlying})", fontsize=12, fontweight="bold")
        ax.set_xlabel("Log-Moneyness ln(K/F)")
        ax.set_ylabel("Tenor (Years)")
        ax.set_zlabel("Implied Volatility")
        fig.colorbar(surf, shrink=0.5, aspect=5)
        if show:
            plt.tight_layout()
            plt.show()

    def plot_smile(self, expiry_idx: int = 0, show: bool = True) -> None:
        """Plot a single volatility smile slice."""
        import matplotlib.pyplot as plt

        t = self.expiries[expiry_idx]
        iv_slice = self.iv_matrix[expiry_idx, :]

        plt.figure(figsize=(8, 4.5))
        plt.plot(self.k_grid, iv_slice * 100.0, "b-", lw=2, label=f"SSVI Smile (T={t:.2f}y)")
        plt.title(f"Implied Volatility Smile — {self.underlying} (T={t:.2f}y)", fontsize=11, fontweight="bold")
        plt.xlabel("Log-Moneyness ln(K/F)")
        plt.ylabel("Implied Volatility (%)")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        if show:
            plt.tight_layout()
            plt.show()


class SsviSurface(VolatilitySurface):
    """
    Surface calibrated using Gatheral & Jacquier (2014) SSVI model.
    """

    def __init__(
        self,
        underlying: str,
        spot: float,
        params: SsviParameters,
        expiries: List[float],
        k_grid: np.ndarray,
        rate: float = 0.04,
        dividend_yield: float = 0.0,
    ):
        self.params = params
        sorted_exp = sorted(expiries)

        n_exp = len(sorted_exp)
        n_k = len(k_grid)
        w_mat = np.zeros((n_exp, n_k), dtype=np.float64)
        for i, t in enumerate(sorted_exp):
            theta = params.theta_map.get(t, t * 0.04)
            w_mat[i, :] = params.total_variance(k_grid, theta)

        super().__init__(
            underlying=underlying,
            spot=spot,
            expiries=sorted_exp,
            k_grid=k_grid,
            w_matrix=w_mat,
            rate=rate,
            dividend_yield=dividend_yield,
        )

    @classmethod
    def calibrate(
        cls,
        chain: OptionChain,
        config: Optional[CalibrationConfig] = None,
        k_grid: Optional[np.ndarray] = None,
    ) -> SsviSurface:
        """
        Calibrate SSVI Surface directly from an OptionChain.
        """
        obs = extract_chain_iv(chain)
        if not obs:
            raise ValueError(f"No valid implied volatility observations found in option chain for {chain.underlying}")

        df = pd.DataFrame([{"ttm": o.ttm, "k": o.log_moneyness, "iv": o.implied_volatility} for o in obs])

        expiries = sorted(df["ttm"].unique().tolist())
        log_moneyness_dict = {}
        market_iv_dict = {}

        for t in expiries:
            sub = df[df["ttm"] == t].sort_values("k")
            log_moneyness_dict[t] = sub["k"].values
            market_iv_dict[t] = sub["iv"].values

        params = calibrate_ssvi(
            expiries=expiries,
            log_moneyness_dict=log_moneyness_dict,
            market_iv_dict=market_iv_dict,
            config=config,
        )

        grid = k_grid if k_grid is not None else np.linspace(-0.35, 0.35, 100)

        return cls(
            underlying=chain.underlying,
            spot=chain.spot,
            params=params,
            expiries=expiries,
            k_grid=grid,
            rate=chain.rate,
            dividend_yield=chain.dividend_yield,
        )


def surface(
    chain_or_symbol: Union[OptionChain, str],
    model: str = "ssvi",
    source: str = "yahoo",
    **kwargs,
) -> VolatilitySurface:
    """
    High-level convenience API (Layer 1): One-call to get an arbitrage-checked volatility surface.
    """
    if isinstance(chain_or_symbol, str):
        from kuwala.data.pipeline import fetch

        chain = fetch(chain_or_symbol, source=source, **kwargs)
    else:
        chain = chain_or_symbol

    if model.lower() == "ssvi":
        return SsviSurface.calibrate(chain, **kwargs)
    else:
        return SsviSurface.calibrate(chain, **kwargs)
