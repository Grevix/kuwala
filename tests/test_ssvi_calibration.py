import kuwala
from kuwala.volatility import CalibrationConfig, SsviSurface


def test_ssvi_surface_calibration():
    chain = kuwala.data.fetch("SPY")
    cfg = CalibrationConfig(optimizer="lbfgsb", max_iter=500)
    surf = kuwala.volatility.surface(chain, model="ssvi", config=cfg)

    assert isinstance(surf, SsviSurface)
    assert abs(surf.params.rho) < 1.0
    assert surf.params.eta > 0.0
    assert 0.0 < surf.params.gamma <= 1.0

    # Test interpolation
    iv_atm = surf.implied_volatility(surf.spot, 0.25)
    assert 0.05 < iv_atm < 1.0
