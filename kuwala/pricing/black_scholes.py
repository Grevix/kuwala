"""
Black-Scholes (1973) European Option Analytical Pricing.
"""

from __future__ import annotations

import math
from typing import Sequence, Union

import numpy as np
from scipy.stats import norm

from kuwala._core import get_rust_core, has_rust_core


def black_scholes(
    spot: Union[float, Sequence[float], np.ndarray],
    strike: Union[float, Sequence[float], np.ndarray],
    t: Union[float, Sequence[float], np.ndarray],
    r: Union[float, Sequence[float], np.ndarray] = 0.0,
    q: Union[float, Sequence[float], np.ndarray] = 0.0,
    sigma: Union[float, Sequence[float], np.ndarray] = 0.2,
    is_call: Union[bool, Sequence[bool], np.ndarray] = True,
) -> Union[float, np.ndarray]:
    """
    Compute European option price under Black-Scholes-Merton model.

    Parameters
    ----------
    spot : float or array-like
        Current underlying spot price S.
    strike : float or array-like
        Strike price K.
    t : float or array-like
        Time to expiration T in years.
    r : float or array-like, default 0.0
        Annualized continuously compounded risk-free rate.
    q : float or array-like, default 0.0
        Annualized continuous dividend yield or borrow cost.
    sigma : float or array-like, default 0.2
        Annualized volatility.
    is_call : bool or array-like, default True
        True for Call options, False for Put options.

    Returns
    -------
    float or np.ndarray
        Theoretical Black-Scholes option price.
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

    if is_scalar:
        if spot <= 0 or strike <= 0:
            return 0.0
        if has_rust_core():
            return get_rust_core().py_black_scholes(
                float(spot),
                float(strike),
                float(t),
                float(r),
                float(q),
                float(sigma),
                bool(is_call),
            )
        else:
            return _black_scholes_scalar_py(
                float(spot),
                float(strike),
                float(t),
                float(r),
                float(q),
                float(sigma),
                bool(is_call),
            )

    # Vectorized path
    spots = np.asarray(spot, dtype=np.float64)
    strikes = np.asarray(strike, dtype=np.float64)
    ts = np.asarray(t, dtype=np.float64)
    rs = np.asarray(r, dtype=np.float64)
    qs = np.asarray(q, dtype=np.float64)
    sigmas = np.asarray(sigma, dtype=np.float64)
    calls = np.asarray(is_call, dtype=bool)

    # Broadcast shapes
    broadcasted = np.broadcast_arrays(spots, strikes, ts, rs, qs, sigmas, calls)
    s_arr, k_arr, t_arr, r_arr, q_arr, sig_arr, call_arr = broadcasted

    result = np.zeros_like(s_arr, dtype=np.float64)

    # Boundary conditions
    invalid = (s_arr <= 0.0) | (k_arr <= 0.0)
    expired = (t_arr <= 0.0) & (~invalid)
    zero_vol = (sig_arr <= 0.0) & (~invalid) & (~expired)
    active = (~invalid) & (~expired) & (~zero_vol)

    # Handle expired
    if np.any(expired):
        call_mask = expired & call_arr
        put_mask = expired & (~call_arr)
        result[call_mask] = np.maximum(0.0, s_arr[call_mask] - k_arr[call_mask])
        result[put_mask] = np.maximum(0.0, k_arr[put_mask] - s_arr[put_mask])

    # Handle zero vol
    if np.any(zero_vol):
        df_r = np.exp(-r_arr[zero_vol] * t_arr[zero_vol])
        fwd = s_arr[zero_vol] * np.exp((r_arr[zero_vol] - q_arr[zero_vol]) * t_arr[zero_vol])
        call_m = zero_vol & call_arr
        put_m = zero_vol & (~call_arr)
        result[call_m] = df_r[call_arr[zero_vol]] * np.maximum(0.0, fwd[call_arr[zero_vol]] - k_arr[call_m])
        result[put_m] = df_r[~call_arr[zero_vol]] * np.maximum(0.0, k_arr[put_m] - fwd[~call_arr[zero_vol]])

    # Active options
    if np.any(active):
        s_act = s_arr[active]
        k_act = k_arr[active]
        t_act = t_arr[active]
        r_act = r_arr[active]
        q_act = q_arr[active]
        sig_act = sig_arr[active]
        call_act = call_arr[active]

        sqrt_t = np.sqrt(t_act)
        vol_sqrt_t = sig_act * sqrt_t
        d1 = (np.log(s_act / k_act) + (r_act - q_act + 0.5 * sig_act**2) * t_act) / vol_sqrt_t
        d2 = d1 - vol_sqrt_t

        df_r = np.exp(-r_act * t_act)
        df_q = np.exp(-q_act * t_act)

        c_prices = s_act * df_q * norm.cdf(d1) - k_act * df_r * norm.cdf(d2)
        p_prices = k_act * df_r * norm.cdf(-d2) - s_act * df_q * norm.cdf(-d1)

        result[active] = np.where(call_act, c_prices, p_prices)

    return result


def _black_scholes_scalar_py(
    spot: float,
    strike: float,
    t: float,
    r: float,
    q: float,
    sigma: float,
    is_call: bool,
) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if t <= 0.0:
        return max(0.0, spot - strike) if is_call else max(0.0, strike - spot)
    if sigma <= 0.0:
        df_r = math.exp(-r * t)
        forward = spot * math.exp((r - q) * t)
        return df_r * max(0.0, forward - strike) if is_call else df_r * max(0.0, strike - forward)

    sqrt_t = math.sqrt(t)
    vol_sqrt_t = sigma * sqrt_t
    d1 = (math.log(spot / strike) + (r - q + 0.5 * sigma * sigma) * t) / vol_sqrt_t
    d2 = d1 - vol_sqrt_t

    df_r = math.exp(-r * t)
    df_q = math.exp(-q * t)

    if is_call:
        return spot * df_q * norm.cdf(d1) - strike * df_r * norm.cdf(d2)
    else:
        return strike * df_r * norm.cdf(-d2) - spot * df_q * norm.cdf(-d1)
