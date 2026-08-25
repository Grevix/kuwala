"""
Signals and Relative-Value Research Layer.
"""

from kuwala.signals.realized_vol import (
    RealizedVolEstimator,
    realized_volatility,
)
from kuwala.signals.vrp import vrp
from kuwala.signals.skew import skew_metrics
from kuwala.signals.term_structure import term_structure_metrics
from kuwala.signals.pca import surface_pca, SurfacePcaResult
from kuwala.signals.validation import (
    ValidationReport,
    ValidationFoldResult,
    purged_kfold_split,
    validate_signal,
)
from kuwala.signals.indicators import (
    sma,
    ema,
    rsi,
    macd,
    bollinger_bands,
    atr,
    stochastic_oscillator,
)

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
