"""
Arbitrage Diagnostics Module.
"""

from kuwala.diagnostics.arbitrage import (
    check_butterfly_slice,
    check_calendar_arbitrage,
    diagnose_surface,
    durrleman_g,
)
from kuwala.diagnostics.report import (
    ButterflyViolation,
    CalendarViolation,
    DiagnosticReport,
    SliceDiagnosticReport,
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
