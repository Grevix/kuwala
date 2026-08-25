import kuwala


def test_flagship_end_to_end_workflow():
    """
    End-to-End Flagship Workflow:
    Fetch data -> Calibrate SSVI Surface -> Inspect Diagnostics -> Extract Local Vol ->
    Compute VRP -> Validate -> Export to VectorBT Connector.
    """
    # 1. Fetch
    options = kuwala.data.fetch("SPY", source="yahoo")
    assert len(options) > 0

    # 2. Fit Surface
    surface = kuwala.volatility.surface(options, model="ssvi")
    assert surface is not None

    # 3. Diagnostics
    report = surface.diagnostics()
    assert hasattr(report, "is_arbitrage_free")
    summary = report.summary()
    assert len(summary) > 0

    # 4. Local Volatility
    local_vol = surface.local_vol()
    assert local_vol.shape[0] == len(surface.expiries)

    # 5. Volatility Risk Premium (VRP)
    vrp_df = kuwala.signals.vrp(surface, realized_window=20)
    assert not vrp_df.empty

    # 6. Backtest connector export
    vbt_dict = kuwala.backtest.to_vectorbt(vrp_df)
    assert "entries" in vbt_dict
    assert "exits" in vbt_dict
    assert "price" in vbt_dict
