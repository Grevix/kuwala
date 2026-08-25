"""
Analytic 1st and 2nd Order Option Greeks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Union, Sequence
import numpy as np
from scipy.stats import norm

from kuwala._core import get_rust_core, has_rust_core


@dataclass
class OptionGreeks:
    delta: Union[float, np.ndarray]
    gamma: Union[float, np.ndarray]
    vega: Union[float, np.ndarray]
    theta: Union[float, np.ndarray]
    rho: Union[float, np.ndarray]
    vanna: Union[float, np.ndarray]
    volga: Union[float, np.ndarray]
    charm: Union[float, np.ndarray]

    def to_dict(self) -> Dict[str, Union[float, np.ndarray]]:
        return {
            "delta": self.delta,
            "gamma": self.gamma,
            "vega": self.vega,
            "theta": self.theta,
            "rho": self.rho,
            "vanna": self.vanna,
            "volga": self.volga,
            "charm": self.charm,
        }


def greeks(
    spot: Union[float, Sequence[float], np.ndarray],
    strike: Union[float, Sequence[float], np.ndarray],
    t: Union[float, Sequence[float], np.ndarray],
    r: Union[float, Sequence[float], np.ndarray] = 0.0,
    q: Union[float, Sequence[float], np.ndarray] = 0.0,
    sigma: Union[float, Sequence[float], np.ndarray] = 0.2,
    is_call: Union[bool, Sequence[bool], np.ndarray] = True,
) -> OptionGreeks:
    """
    Calculate 1st and 2nd order analytical Black-Scholes Greeks.
    """
    is_scalar = (
        isinstance(spot, (int, float))
        and isinstance(strike, (int, float))
        and isinstance(t, (int, float))
        and isinstance(r, (int, float))
        and isinstance(q, (int, float))
        and isinstance(sigma, (int, float))
        and isinstance(is_call, (bool, np.bool_))
    )

    if is_scalar and has_rust_core():
        d = get_rust_core().py_greeks(
            float(spot),
            float(strike),
            float(t),
            float(r),
            float(q),
            float(sigma),
            bool(is_call),
        )
        return OptionGreeks(**d)

    # Vectorized / Pure Python path
    s_arr, k_arr, t_arr, r_arr, q_arr, sig_arr, call_arr = np.broadcast_arrays(
        np.asarray(spot, dtype=np.float64),
        np.asarray(strike, dtype=np.float64),
        np.asarray(t, dtype=np.float64),
        np.asarray(r, dtype=np.float64),
        np.asarray(q, dtype=np.float64),
        np.asarray(sigma, dtype=np.float64),
        np.asarray(is_call, dtype=bool),
    )

    delta = np.zeros_like(s_arr)
    gamma = np.zeros_like(s_arr)
    vega = np.zeros_like(s_arr)
    theta = np.zeros_like(s_arr)
    rho = np.zeros_like(s_arr)
    vanna = np.zeros_like(s_arr)
    volga = np.zeros_like(s_arr)
    charm = np.zeros_like(s_arr)

    valid = (t_arr > 1e-12) & (sig_arr > 1e-12) & (s_arr > 1e-12) & (k_arr > 1e-12)
    invalid = ~valid

    if np.any(invalid):
        delta[invalid] = np.where(call_arr[invalid], np.where(s_arr[invalid] > k_arr[invalid], 1.0, 0.0), np.where(s_arr[invalid] < k_arr[invalid], -1.0, 0.0))

    if np.any(valid):
        s = s_arr[valid]
        k = k_arr[valid]
        t_val = t_arr[valid]
        r_val = r_arr[valid]
        q_val = q_arr[valid]
        sig = sig_arr[valid]
        is_c = call_arr[valid]

        sqrt_t = np.sqrt(t_val)
        vol_sqrt_t = sig * sqrt_t
        d1 = (np.log(s / k) + (r_val - q_val + 0.5 * sig**2) * t_val) / vol_sqrt_t
        d2 = d1 - vol_sqrt_t

        pdf_d1 = norm.pdf(d1)
        cdf_d1 = norm.cdf(d1)
        cdf_d2 = norm.cdf(d2)
        df_r = np.exp(-r_val * t_val)
        df_q = np.exp(-q_val * t_val)

        delta_val = np.where(is_c, df_q * cdf_d1, df_q * (cdf_d1 - 1.0))
        gamma_val = (df_q * pdf_d1) / (s * vol_sqrt_t)
        vega_val = s * df_q * sqrt_t * pdf_d1

        theta_common = -(s * df_q * pdf_d1 * sig) / (2.0 * sqrt_t)
        theta_val = np.where(
            is_c,
            theta_common - r_val * k * df_r * cdf_d2 + q_val * s * df_q * cdf_d1,
            theta_common + r_val * k * df_r * norm.cdf(-d2) - q_val * s * df_q * norm.cdf(-d1),
        )

        rho_val = np.where(is_c, k * t_val * df_r * cdf_d2, -k * t_val * df_r * norm.cdf(-d2))
        vanna_val = -df_q * pdf_d1 * d2 / sig
        volga_val = vega_val * d1 * d2 / sig

        charm_val = np.where(
            is_c,
            q_val * df_q * cdf_d1 - df_q * pdf_d1 * (2.0 * (r_val - q_val) * t_val - d2 * vol_sqrt_t) / (2.0 * t_val * vol_sqrt_t),
            -q_val * df_q * norm.cdf(-d1) - df_q * pdf_d1 * (2.0 * (r_val - q_val) * t_val - d2 * vol_sqrt_t) / (2.0 * t_val * vol_sqrt_t),
        )

        delta[valid] = delta_val
        gamma[valid] = gamma_val
        vega[valid] = vega_val
        theta[valid] = theta_val
        rho[valid] = rho_val
        vanna[valid] = vanna_val
        volga[valid] = volga_val
        charm[valid] = charm_val

    if is_scalar:
        return OptionGreeks(
            delta=float(delta),
            gamma=float(gamma),
            vega=float(vega),
            theta=float(theta),
            rho=float(rho),
            vanna=float(vanna),
            volga=float(volga),
            charm=float(charm),
        )

    return OptionGreeks(
        delta=delta,
        gamma=gamma,
        vega=vega,
        theta=theta,
        rho=rho,
        vanna=vanna,
        volga=volga,
        charm=charm,
    )
