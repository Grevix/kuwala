"""
Arbitrage Diagnostics Module.
"""

from kuwala.diagnostics.report import (
    ButterflyViolation,
    CalendarViolation,
    SliceDiagnosticReport,
    DiagnosticReport,
)
from kuwala.diagnostics.arbitrage import (
    durrleman_g,
    check_butterfly_slice,
    check_calendar_arbitrage,
    diagnose_surface,
)

__all__ = [
    "ButterflyViolation",
    "CalendarViolation",
    "SliceDiagnosticReport",
    "DiagnosticReport",
    "durrleman_g",
    "check_butterfly_slice",
    "check_calendar_arbitrage",
    "diagnose_surface",
]
