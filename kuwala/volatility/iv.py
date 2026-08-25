"""
High-Performance Implied Volatility Solver.
"""

from __future__ import annotations

import math
from typing import Union, Sequence, Optional, List
import numpy as np
from scipy.optimize import brentq

from kuwala.data.models import OptionChain, VolatilityObservation, OptionType
from kuwala.pricing.black_scholes import black_scholes
from kuwala._core import get_rust_core, has_rust_core


def implied_volatility(
    price: Union[float, Sequence[float], np.ndarray],
    spot: Union[float, Sequence[float], np.ndarray],
    strike: Union[float, Sequence[float], np.ndarray],
    t: Union[float, Sequence[float], np.ndarray],
    r: Union[float, Sequence[float], np.ndarray] = 0.0,
    q: Union[float, Sequence[float], np.ndarray] = 0.0,
    is_call: Union[bool, Sequence[bool], np.ndarray] = True,
    initial_guess: Optional[Union[float, Sequence[float]]] = None,
    tol: float = 1e-8,
    max_iter: int = 100,
) -> Union[float, np.ndarray]:
    """
    Calculate Black-Scholes implied volatility using hybrid Halley / Brent-Dekker solver.
    """
    is_scalar = (
        isinstance(price, (int, float))
        and isinstance(spot, (int, float))
        and isinstance(strike, (int, float))
        and isinstance(t, (int, float))
        and isinstance(r, (int, float))
        and isinstance(q, (int, float))
        and isinstance(is_call, (bool, np.bool_))
    )

    if is_scalar:
        if has_rust_core():
            try:
                return get_rust_core().py_implied_volatility(
                    float(price),
                    float(spot),
                    float(strike),
                    float(t),
                    float(r),
                    float(q),
                    bool(is_call),
                    float(initial_guess) if initial_guess is not None else None,
                    tol,
                    max_iter,
                )
            except Exception:
                return _implied_volatility_scalar_py(
                    float(price), float(spot), float(strike), float(t), float(r), float(q), bool(is_call), tol
                )
        else:
            return _implied_volatility_scalar_py(
                float(price), float(spot), float(strike), float(t), float(r), float(q), bool(is_call), tol
            )

    # Batch / Vectorized
    p_arr = np.asarray(price, dtype=np.float64)
    s_arr = np.asarray(spot, dtype=np.float64)
    k_arr = np.asarray(strike, dtype=np.float64)
    t_arr = np.asarray(t, dtype=np.float64)
    r_arr = np.asarray(r, dtype=np.float64)
    q_arr = np.asarray(q, dtype=np.float64)
    call_arr = np.asarray(is_call, dtype=bool)

    p_b, s_b, k_b, t_b, r_b, q_b, call_b = np.broadcast_arrays(
        p_arr, s_arr, k_arr, t_arr, r_arr, q_arr, call_arr
    )

    if has_rust_core():
        try:
            res = get_rust_core().py_implied_volatility_batch(
                p_b.ravel().tolist(),
                s_b.ravel().tolist(),
                k_b.ravel().tolist(),
                t_b.ravel().tolist(),
                r_b.ravel().tolist(),
                q_b.ravel().tolist(),
                call_b.ravel().tolist(),
                None,
                tol,
                max_iter,
            )
            res_arr = np.array([np.nan if x is None else x for x in res], dtype=np.float64)
            return res_arr.reshape(p_b.shape)
        except Exception:
            pass

    out = np.full_like(p_b, np.nan, dtype=np.float64)
    flat_out = out.ravel()
    for i, (pr, sp, st, tm, rt, qy, cl) in enumerate(
        zip(
            p_b.ravel(),
            s_b.ravel(),
            k_b.ravel(),
            t_b.ravel(),
            r_b.ravel(),
            q_b.ravel(),
            call_b.ravel(),
        )
    ):
        flat_out[i] = _implied_volatility_scalar_py(pr, sp, st, tm, rt, qy, cl, tol)
    return out


def _implied_volatility_scalar_py(
    price: float,
    spot: float,
    strike: float,
    t: float,
    r: float,
    q: float,
    is_call: bool,
    tol: float = 1e-8,
) -> float:
    if price <= 0.0 or spot <= 0.0 or strike <= 0.0 or t <= 0.0:
        return np.nan

    df_r = math.exp(-r * t)
    df_q = math.exp(-q * t)
    intrinsic = max(0.0, spot * df_q - strike * df_r) if is_call else max(0.0, strike * df_r - spot * df_q)
    upper_bound = spot * df_q if is_call else strike * df_r

    if price < intrinsic - 1e-7 or price > upper_bound + 1e-7:
        return np.nan

    def objective(sigma: float) -> float:
        return black_scholes(spot, strike, t, r, q, sigma, is_call) - price

    try:
        return brentq(objective, 1e-5, 10.0, xtol=tol)
    except Exception:
        return np.nan


def extract_chain_iv(chain: OptionChain) -> List[VolatilityObservation]:
    """
    Extract implied volatilities for an entire OptionChain.
    """
    observations: List[VolatilityObservation] = []
    spot = chain.spot
    r = chain.rate
    q = chain.dividend_yield

    for quote in chain.quotes:
        ttm = max(1e-5, (quote.expiry - quote.timestamp).total_seconds() / (365.0 * 86400.0))
        forward = spot * math.exp((r - q) * ttm)
        k = math.log(quote.strike / forward) if forward > 0 and quote.strike > 0 else 0.0

        iv = implied_volatility(
            price=quote.mid,
            spot=spot,
            strike=quote.strike,
            t=ttm,
            r=r,
            q=q,
            is_call=quote.is_call,
        )

        if not np.isnan(iv) and iv > 0:
            total_var = iv * iv * ttm
            observations.append(
                VolatilityObservation(
                    underlying=chain.underlying,
                    timestamp=quote.timestamp,
                    expiry=quote.expiry,
                    ttm=ttm,
                    strike=quote.strike,
                    forward=forward,
                    log_moneyness=k,
                    option_type=quote.option_type,
                    market_price=quote.mid,
                    implied_volatility=float(iv),
                    total_implied_variance=float(total_var),
                )
            )

    return observations
