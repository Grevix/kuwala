"""
Signals and Relative-Value Research Layer.
"""

from kuwala.signals.indicators import (
    atr,
    bollinger_bands,
    ema,
    macd,
    rsi,
    sma,
    stochastic_oscillator,
)
from kuwala.signals.pca import SurfacePcaResult, surface_pca
from kuwala.signals.realized_vol import (
    RealizedVolEstimator,
    realized_volatility,
)
from kuwala.signals.skew import skew_metrics
from kuwala.signals.term_structure import term_structure_metrics
from kuwala.signals.validation import (
    ValidationFoldResult,
    ValidationReport,
    purged_kfold_split,
    validate_signal,
)
from kuwala.signals.vrp import vrp

__all__ = [
    "RealizedVolEstimator",
    "realized_volatility",
    "vrp",
    "skew_metrics",
    "term_structure_metrics",
    "surface_pca",
    "SurfacePcaResult",
    "ValidationReport",
    "ValidationFoldResult",
    "purged_kfold_split",
    "validate_signal",
    "sma",
    "ema",
    "rsi",
    "macd",
    "bollinger_bands",
    "atr",
    "stochastic_oscillator",
]
