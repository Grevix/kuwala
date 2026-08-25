"""
Durrleman (2002) Butterfly and Calendar Arbitrage Diagnostic Kernels.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

import numpy as np

from kuwala._core import get_rust_core, has_rust_core
from kuwala.diagnostics.report import (
    ButterflyViolation,
    CalendarViolation,
    DiagnosticReport,
    SliceDiagnosticReport,
)


def durrleman_g(k: float, w: float, dw: float, d2w: float) -> float:
    """
    Compute Durrleman's g(k) value:
    g(k) = (1 - k*w'/(2w))^2 - (w'^2 / 4)*(1/w + 1/4) + w''/2
    """
    if has_rust_core():
        return get_rust_core().py_durrleman_g(k, w, dw, d2w)
    if w <= 1e-12:
        return -1.0
    term1 = (1.0 - (k * dw) / (2.0 * w)) ** 2
    term2 = (dw * dw / 4.0) * (1.0 / w + 0.25)
    term3 = 0.5 * d2w
    return term1 - term2 + term3


def check_butterfly_slice(
    expiry: float,
    k_grid: np.ndarray,
    w_grid: np.ndarray,
    spot: Optional[float] = None,
) -> SliceDiagnosticReport:
    """
    Check Durrleman's butterfly condition g(k) >= 0 on a single variance slice.
    """
    dw = np.gradient(w_grid, k_grid)
    d2w = np.gradient(dw, k_grid)

    violations: List[ButterflyViolation] = []
    min_g = float("inf")

    for i in range(len(k_grid)):
        k = float(k_grid[i])
        w = float(w_grid[i])
        g = durrleman_g(k, w, float(dw[i]), float(d2w[i]))
        if g < min_g:
            min_g = g

        if g < -1e-5 or w <= 0:
            strike = spot * np.exp(k) if spot is not None else None
            violations.append(
                ButterflyViolation(
                    log_moneyness=k,
                    g_value=g,
                    total_variance=w,
                    strike=strike,
                    severity="HIGH" if g < -0.05 else "MEDIUM",
                )
            )

    return SliceDiagnosticReport(
        expiry=expiry,
        butterfly_passed=len(violations) == 0,
        min_g_value=min_g if min_g != float("inf") else 0.0,
        violations=violations,
    )


def check_calendar_arbitrage(
    expiries: Sequence[float],
    k_grid: np.ndarray,
    w_matrix: np.ndarray,
    spot: Optional[float] = None,
) -> List[CalendarViolation]:
    """
    Check calendar arbitrage: total variance w(k, T2) >= w(k, T1) for T2 > T1.
    """
    violations: List[CalendarViolation] = []
    num_tenors = len(expiries)

    for i in range(num_tenors - 1):
        t1 = expiries[i]
        t2 = expiries[i + 1]
        w1 = w_matrix[i, :]
        w2 = w_matrix[i + 1, :]

        for j in range(len(k_grid)):
            k = float(k_grid[j])
            if w2[j] < w1[j] - 1e-6:
                strike = spot * np.exp(k) if spot is not None else None
                violations.append(
                    CalendarViolation(
                        log_moneyness=k,
                        expiry_1=t1,
                        expiry_2=t2,
                        total_var_1=float(w1[j]),
                        total_var_2=float(w2[j]),
                        strike=strike,
                    )
                )

    return violations


def diagnose_surface(
    expiries: Sequence[float],
    k_grid: np.ndarray,
    w_matrix: np.ndarray,
    spot: Optional[float] = None,
) -> DiagnosticReport:
    """
    Perform full butterfly and calendar arbitrage diagnosis on a surface.
    """
    slice_reports = []
    all_butterfly_passed = True

    for i, t in enumerate(expiries):
        sr = check_butterfly_slice(t, k_grid, w_matrix[i, :], spot=spot)
        if not sr.butterfly_passed:
            all_butterfly_passed = False
        slice_reports.append(sr)

    cal_violations = check_calendar_arbitrage(expiries, k_grid, w_matrix, spot=spot)
    cal_passed = len(cal_violations) == 0

    return DiagnosticReport(
        is_arbitrage_free=(all_butterfly_passed and cal_passed),
        butterfly_passed=all_butterfly_passed,
        calendar_passed=cal_passed,
        slice_reports=slice_reports,
        calendar_violations=cal_violations,
    )
