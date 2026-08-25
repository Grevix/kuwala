"""
Arbitrage Diagnostic Reports & Structured Inspection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ButterflyViolation:
    log_moneyness: float
    g_value: float
    total_variance: float
    strike: Optional[float] = None
    severity: str = "HIGH"

    def __repr__(self) -> str:
        s_str = f" strike={self.strike:.2f}," if self.strike is not None else ""
        return f"<ButterflyViolation k={self.log_moneyness:.4f},{s_str} g(k)={self.g_value:.6f}, w={self.total_variance:.6f}>"


@dataclass
class CalendarViolation:
    log_moneyness: float
    expiry_1: float
    expiry_2: float
    total_var_1: float
    total_var_2: float
    strike: Optional[float] = None
    severity: str = "HIGH"

    def __repr__(self) -> str:
        s_str = f" strike={self.strike:.2f}," if self.strike is not None else ""
        return (
            f"<CalendarViolation k={self.log_moneyness:.4f},{s_str} "
            f"T1={self.expiry_1:.2f}(w1={self.total_var_1:.4f}) > T2={self.expiry_2:.2f}(w2={self.total_var_2:.4f})>"
        )


@dataclass
class SliceDiagnosticReport:
    expiry: float
    butterfly_passed: bool
    min_g_value: float
    violations: List[ButterflyViolation] = field(default_factory=list)

    def summary(self) -> str:
        status = "PASSED" if self.butterfly_passed else "FAILED"
        msg = f"  Slice T={self.expiry:.3f} yrs: Butterfly Arbitrage [{status}] (min g(k) = {self.min_g_value:.6f})"
        if not self.butterfly_passed:
            msg += f"\n    -> {len(self.violations)} violations detected (e.g. k={self.violations[0].log_moneyness:.4f}, g={self.violations[0].g_value:.6f})"
        return msg


@dataclass
class DiagnosticReport:
    """
    Structured arbitrage diagnostic report for a calibrated volatility surface.
    """

    is_arbitrage_free: bool
    butterfly_passed: bool
    calendar_passed: bool
    slice_reports: List[SliceDiagnosticReport] = field(default_factory=list)
    calendar_violations: List[CalendarViolation] = field(default_factory=list)

    def summary(self) -> str:
        status = "NO ARBITRAGE DETECTED (PASSED)" if self.is_arbitrage_free else "ARBITRAGE DETECTED (FAILED)"
        lines = [
            "===========================================================",
            f"  KUWALA ARBITRAGE DIAGNOSTIC REPORT: {status}",
            "===========================================================",
            f"• Butterfly Arbitrage: {'PASSED' if self.butterfly_passed else 'FAILED'}",
            f"• Calendar Arbitrage:  {'PASSED' if self.calendar_passed else 'FAILED'}",
            "",
            "Slice-by-Slice Butterfly Diagnostics:",
        ]
        for sr in self.slice_reports:
            lines.append(sr.summary())

        if self.calendar_violations:
            lines.append("")
            lines.append(f"Calendar Arbitrage Violations ({len(self.calendar_violations)} total):")
            for cv in self.calendar_violations[:5]:
                lines.append(f"  - {cv}")
            if len(self.calendar_violations) > 5:
                lines.append(f"  ... and {len(self.calendar_violations) - 5} more.")

        lines.append("===========================================================")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_arbitrage_free": self.is_arbitrage_free,
            "butterfly_passed": self.butterfly_passed,
            "calendar_passed": self.calendar_passed,
            "num_slice_reports": len(self.slice_reports),
            "num_calendar_violations": len(self.calendar_violations),
        }
