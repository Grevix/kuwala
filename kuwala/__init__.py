"""
Kuwala: A Unified, Arbitrage-Checked Quantitative Options & Volatility Research Library.
"""

__version__ = "0.1.0"

# Core submodules
from kuwala import pricing
from kuwala import volatility
from kuwala import data
from kuwala import diagnostics
from kuwala import signals
from kuwala import backtest

# Direct top-level ergonomic access
from kuwala.pricing import black_scholes, black76, greeks, OptionGreeks
from kuwala.volatility import implied_volatility, surface, VolatilitySurface, SsviSurface
from kuwala.data import fetch, clean_chain, OptionChain, OptionQuote, OptionType
from kuwala.signals import vrp, realized_volatility, validate_signal

__all__ = [
    "__version__",
    # Submodules
    "pricing",
    "volatility",
    "data",
    "diagnostics",
    "signals",
    "backtest",
    # Top-level API functions
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
]
