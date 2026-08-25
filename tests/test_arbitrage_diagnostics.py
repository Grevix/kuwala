import pytest

import kuwala
from kuwala.diagnostics.arbitrage import durrleman_g


def test_durrleman_g_calculation():
    # Flat surface w = 0.04 -> dw=0, d2w=0 -> g(k) = (1 - 0)^2 - 0 + 0 = 1.0 >= 0 (arbitrage free)
    g_flat = durrleman_g(0.0, 0.04, 0.0, 0.0)
    assert pytest.approx(g_flat, abs=1e-7) == 1.0


def test_surface_diagnostics_report():
    chain = kuwala.data.fetch("SPY")
    surf = kuwala.volatility.surface(chain, model="ssvi")
    report = surf.diagnostics()

    assert hasattr(report, "is_arbitrage_free")
    assert hasattr(report, "butterfly_passed")
    assert hasattr(report, "calendar_passed")
    summary = report.summary()
    assert "KUWALA ARBITRAGE DIAGNOSTIC REPORT" in summary
