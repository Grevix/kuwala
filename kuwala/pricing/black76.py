"""
Black-76 European Commodity/Futures/Forward Option Analytical Pricing.
"""

from __future__ import annotations

import math
from typing import Union, Sequence
import numpy as np
from scipy.stats import norm

from kuwala._core import get_rust_core, has_rust_core


def black76(
    forward: Union[float, Sequence[float], np.ndarray],
    strike: Union[float, Sequence[float], np.ndarray],
    t: Union[float, Sequence[float], np.ndarray],
    r: Union[float, Sequence[float], np.ndarray] = 0.0,
    sigma: Union[float, Sequence[float], np.ndarray] = 0.2,
    is_call: Union[bool, Sequence[bool], np.ndarray] = True,
) -> Union[float, np.ndarray]:
    """
    Compute European option price under Black-76 model for futures/forwards.
    """
    is_scalar = (
        isinstance(forward, (int, float))
        and isinstance(strike, (int, float))
        and isinstance(t, (int, float))
        and isinstance(r, (int, float))
        and isinstance(sigma, (int, float))
        and isinstance(is_call, (bool, np.bool_))
    )

    if is_scalar:
        if has_rust_core():
            return get_rust_core().py_black76(
                float(forward),
                float(strike),
                float(t),
                float(r),
                float(sigma),
                bool(is_call),
            )
        else:
            return _black76_scalar_py(
                float(forward),
                float(strike),
                float(t),
                float(r),
                float(sigma),
                bool(is_call),
            )

    # Vectorized path
    f_arr, k_arr, t_arr, r_arr, sig_arr, call_arr = np.broadcast_arrays(
        np.asarray(forward, dtype=np.float64),
        np.asarray(strike, dtype=np.float64),
        np.asarray(t, dtype=np.float64),
        np.asarray(r, dtype=np.float64),
        np.asarray(sigma, dtype=np.float64),
        np.asarray(is_call, dtype=bool),
    )

    result = np.zeros_like(f_arr, dtype=np.float64)
    expired = t_arr <= 0.0
    zero_vol = sig_arr <= 0.0
    active = (~expired) & (~zero_vol)

    if np.any(expired):
        call_mask = expired & call_arr
        put_mask = expired & (~call_arr)
        result[call_mask] = np.maximum(0.0, f_arr[call_mask] - k_arr[call_mask])
        result[put_mask] = np.maximum(0.0, k_arr[put_mask] - f_arr[put_mask])

    if np.any(zero_vol & ~expired):
        mask = zero_vol & ~expired
        df_r = np.exp(-r_arr[mask] * t_arr[mask])
        call_m = mask & call_arr
        put_m = mask & (~call_arr)
        result[call_m] = df_r[call_arr[mask]] * np.maximum(0.0, f_arr[call_arr[mask]] - k_arr[call_m])
        result[put_m] = df_r[~call_arr[mask]] * np.maximum(0.0, k_arr[put_m] - f_arr[~call_arr[mask]])

    if np.any(active):
        f_act = f_arr[active]
        k_act = k_arr[active]
        t_act = t_arr[active]
        r_act = r_arr[active]
        sig_act = sig_arr[active]
        call_act = call_arr[active]

        sqrt_t = np.sqrt(t_act)
        vol_sqrt_t = sig_act * sqrt_t
        d1 = (np.log(f_act / k_act) + 0.5 * sig_act**2 * t_act) / vol_sqrt_t
        d2 = d1 - vol_sqrt_t
        df_r = np.exp(-r_act * t_act)

        c_prices = df_r * (f_act * norm.cdf(d1) - k_act * norm.cdf(d2))
        p_prices = df_r * (k_act * norm.cdf(-d2) - f_act * norm.cdf(-d1))
        result[active] = np.where(call_act, c_prices, p_prices)

    return result


def _black76_scalar_py(
    forward: float,
    strike: float,
    t: float,
    r: float,
    sigma: float,
    is_call: bool,
) -> float:
    if t <= 0.0:
        return max(0.0, forward - strike) if is_call else max(0.0, strike - forward)
    discount = math.exp(-r * t)
    if sigma <= 0.0:
        return discount * max(0.0, forward - strike) if is_call else discount * max(0.0, strike - forward)

    sqrt_t = math.sqrt(t)
    vol_sqrt_t = sigma * sqrt_t
    d1 = (math.log(forward / strike) + 0.5 * sigma * sigma * t) / vol_sqrt_t
    d2 = d1 - vol_sqrt_t

    if is_call:
        return discount * (forward * norm.cdf(d1) - strike * norm.cdf(d2))
    else:
        return discount * (strike * norm.cdf(-d2) - forward * norm.cdf(-d1))
