"""
SVI and Gatheral-Jacquier (2014) Surface SVI (SSVI) Calibration Engine.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Union
import numpy as np
from scipy.optimize import minimize, differential_evolution

from kuwala._core import get_rust_core, has_rust_core


@dataclass
class SsviParameters:
    rho: float       # Correlation skew parameter in (-1, 1)
    eta: float       # Scale parameter > 0
    gamma: float     # Power-law parameter in (0, 1]
    theta_map: Dict[float, float] = field(default_factory=dict) # ATM total variance per expiry T

    def phi(self, theta: float) -> float:
        if theta <= 1e-8:
            return self.eta
        return self.eta / (theta ** self.gamma)

    def total_variance(self, k: Union[float, np.ndarray], theta: float) -> Union[float, np.ndarray]:
        """
        w(k, theta) = (theta / 2) * (1 + rho * phi(theta) * k + sqrt((phi(theta) * k + rho)^2 + (1 - rho^2)))
        """
        if isinstance(k, (int, float)):
            if has_rust_core():
                return get_rust_core().py_ssvi_total_variance(float(k), float(theta), self.rho, self.eta, self.gamma)
            phi = self.phi(theta)
            phi_k = phi * k
            rad = math.sqrt(max(0.0, (phi_k + self.rho)**2 + (1.0 - self.rho**2)))
            return 0.5 * theta * (1.0 + self.rho * phi_k + rad)

        k_arr = np.asarray(k, dtype=np.float64)
        phi = self.phi(theta)
        phi_k = phi * k_arr
        rad = np.sqrt(np.maximum(0.0, (phi_k + self.rho)**2 + (1.0 - self.rho**2)))
        return 0.5 * theta * (1.0 + self.rho * phi_k + rad)

    def implied_volatility(self, k: Union[float, np.ndarray], t: float) -> Union[float, np.ndarray]:
        theta = self.theta_map.get(t, t * 0.04) # fallback
        total_var = self.total_variance(k, theta)
        return np.sqrt(np.maximum(1e-8, total_var / max(1e-5, t)))


@dataclass
class CalibrationConfig:
    optimizer: str = "multi_start"  # "multi_start", "differential_evolution", "lbfgsb"
    weighting: str = "vega"         # "vega", "equal", "inverse_spread"
    tol: float = 1e-8
    max_iter: int = 2000
    n_starts: int = 10


def calibrate_ssvi(
    expiries: List[float],
    log_moneyness_dict: Dict[float, np.ndarray],
    market_iv_dict: Dict[float, np.ndarray],
    config: Optional[CalibrationConfig] = None,
) -> SsviParameters:
    """
    Calibrate Gatheral & Jacquier (2014) SSVI surface across multiple tenors.
    """
    cfg = config or CalibrationConfig()
    sorted_expiries = sorted(expiries)

    theta_map: Dict[float, float] = {}
    for t in sorted_expiries:
        ks = log_moneyness_dict[t]
        ivs = market_iv_dict[t]
        idx_atm = np.argmin(np.abs(ks))
        atm_iv = float(ivs[idx_atm])
        theta_map[t] = max(1e-5, atm_iv * atm_iv * t)

    theta_vals = [theta_map[t] for t in sorted_expiries]
    for i in range(1, len(theta_vals)):
        if theta_vals[i] <= theta_vals[i - 1]:
            theta_vals[i] = theta_vals[i - 1] + 1e-5
            theta_map[sorted_expiries[i]] = theta_vals[i]

    def objective(params: np.ndarray) -> float:
        rho, eta, gamma = params
        if abs(rho) >= 0.999 or eta <= 1e-4 or gamma <= 0.01 or gamma > 1.0:
            return 1e9

        total_err = 0.0
        for t in sorted_expiries:
            theta = theta_map[t]
            phi_val = eta / (theta ** gamma) if theta > 1e-8 else eta
            if theta * phi_val * (1.0 + abs(rho)) > 4.0:
                total_err += 1e5 * (theta * phi_val * (1.0 + abs(rho)) - 4.0) ** 2

            ks = log_moneyness_dict[t]
            market_w = (market_iv_dict[t] ** 2) * t
            
            phi_k = phi_val * ks
            rad = np.sqrt(np.maximum(0.0, (phi_k + rho)**2 + (1.0 - rho**2)))
            model_w = 0.5 * theta * (1.0 + rho * phi_k + rad)

            diff = model_w - market_w
            if cfg.weighting == "vega":
                weights = np.exp(-0.5 * (ks / 0.2)**2)
            else:
                weights = np.ones_like(ks)

            total_err += np.sum(weights * (diff ** 2))

        return total_err

    bounds = [(-0.95, 0.95), (0.01, 5.0), (0.01, 0.99)]
    best_loss = float("inf")
    best_params = np.array([-0.3, 0.8, 0.4])

    if cfg.optimizer in ("differential_evolution", "multi_start"):
        de_res = differential_evolution(objective, bounds, seed=42, maxiter=200, tol=1e-5)
        if de_res.fun < best_loss:
            best_loss = de_res.fun
            best_params = de_res.x

    opt_res = minimize(objective, best_params, method="L-BFGS-B", bounds=bounds, tol=cfg.tol)
    if opt_res.success or opt_res.fun < best_loss:
        best_params = opt_res.x

    return SsviParameters(
        rho=float(best_params[0]),
        eta=float(best_params[1]),
        gamma=float(best_params[2]),
        theta_map=theta_map,
    )
