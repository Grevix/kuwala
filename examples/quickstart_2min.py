"""
Kuwala 2-Minute Quickstart Demo.
=================================
8 lines of code from raw data to arbitrage-checked volatility surface.
"""

import kuwala

# 1. Fetch real market options chain (adapter-only, never bundled)
options = kuwala.data.fetch("SPY", source="yahoo")

# 2. Fit Gatheral-Jacquier SSVI arbitrage-checked surface
surface = kuwala.volatility.surface(options, model="ssvi")

# 3. Inspect inspectable diagnostics (never a silent boolean)
report = surface.diagnostics()
print(report.summary())

# 4. Extract local volatility & VRP
local_vol = surface.local_vol()
vrp_df = kuwala.signals.vrp(surface, realized_window=20)
print("\nVolatility Risk Premium (VRP):")
print(vrp_df.to_string(index=False))

# 5. Export to backtesting ecosystem
vbt_signals = kuwala.backtest.to_vectorbt(vrp_df)
print("\nVectorBT Connector Entries:")
print(vbt_signals["entries"])
