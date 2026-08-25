"""
Dupire Local Volatility Extraction Engine.
"""

from __future__ import annotations

import numpy as np

from kuwala._core import get_rust_core, has_rust_core
from kuwala.diagnostics.arbitrage import durrleman_g


def extract_dupire_local_volatility(
    k_grid: np.ndarray,
    expiries: np.ndarray,
    w_matrix: np.ndarray,
) -> np.ndarray:
    """
    Extract discrete Dupire local volatility surface from total implied variance matrix w(k, T).
    """
    n_exp = len(expiries)
    n_k = len(k_grid)
    local_vol_matrix = np.zeros((n_exp, n_k), dtype=np.float64)

    dw_dt = np.zeros_like(w_matrix)
    for j in range(n_k):
        dw_dt[:, j] = np.gradient(w_matrix[:, j], expiries)

    for i in range(n_exp):
        w_slice = w_matrix[i, :]
        dw_dk = np.gradient(w_slice, k_grid)
        d2w_dk2 = np.gradient(dw_dk, k_grid)

        for j in range(n_k):
            k = float(k_grid[j])
            w = float(w_slice[j])
            dw = float(dw_dk[j])
            d2w = float(d2w_dk2[j])
            dt = float(dw_dt[i, j])

            if has_rust_core():
                try:
                    lv = get_rust_core().py_dupire_local_volatility(k, w, dw, d2w, dt)
                    local_vol_matrix[i, j] = lv
                    continue
                except Exception:
                    pass

            g = durrleman_g(k, w, dw, d2w)
            if g > 1e-6 and dt > 0 and w > 0:
                loc_var = dt / g
                local_vol_matrix[i, j] = np.sqrt(loc_var) if loc_var > 0 else np.nan
            else:
                local_vol_matrix[i, j] = np.nan

    return local_vol_matrix
