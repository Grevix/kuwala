"""
Kuwala: A Unified, Arbitrage-Checked Quantitative Options & Volatility Research Library.
"""

__version__ = "0.2.0"

# Core submodules
from kuwala import backtest, data, diagnostics, pricing, signals, volatility
from kuwala.data import (
    CubicSplineCurve,
    DataStore,
    ForwardCurve,
    NelsonSiegelCurve,
    OptionChain,
    OptionQuote,
    OptionType,
    YieldCurve,
    aggregate_ticks_to_bars,
    bootstrap_treasury_curve,
    clean_chain,
    extract_forward_from_chain,
    fetch,
)

# Direct top-level ergonomic access
from kuwala.pricing import OptionGreeks, black76, black_scholes, greeks
from kuwala.signals import realized_volatility, validate_signal, vrp
from kuwala.volatility import SsviSurface, VolatilitySurface, implied_volatility, surface

__all__ = [
    "__version__",
    # Submodules
    "pricing",
    "volatility",
    "data",
    "diagnostics",
    "signals",
    "backtest",
    # Top-level API functions & models
    "black_scholes",
    "black76",
    "greeks",
    "OptionGreeks",
    "implied_volatility",
    "surface",
    "VolatilitySurface",
    "SsviSurface",
    "fetch",
    "clean_chain",
    "OptionChain",
    "OptionQuote",
    "OptionType",
    "vrp",
    "realized_volatility",
    "validate_signal",
    "YieldCurve",
    "CubicSplineCurve",
    "NelsonSiegelCurve",
    "bootstrap_treasury_curve",
    "ForwardCurve",
    "extract_forward_from_chain",
    "aggregate_ticks_to_bars",
    "DataStore",
]
