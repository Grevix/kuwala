# Kuwala Pre-Release Bug Discovery & Resolution Log

This document records all confirmed bugs discovered during real-data testing and stress testing, along with root-cause analyses and permanent regression tests.

## Summary of Resolved Bugs

### [BUG-01] kuwala.data.models — Severity: `HIGH`
- **Date**: 2026-08-25
- **Dataset / Trigger**: Data Model Serialization
- **Input**: `OptionChain default factory timestamp initialization`
- **Expected Behavior**: Default timestamp initialized to UTC timezone
- **Actual Behavior**: `AttributeError: type object 'datetime.datetime' has no attribute 'timezone'`
- **Root Cause**: datetime.timezone referenced on class rather than imported timezone.utc
- **Resolution**: Imported timezone from datetime and used timezone.utc in default_factory
- **Regression Test**: `tests/test_data_models.py::test_conventions_and_year_fraction`
- **Status**: **PASSED**

---

### [BUG-02] kuwala.signals.pca — Severity: `MEDIUM`
- **Date**: 2026-08-25
- **Dataset / Trigger**: Multi-Asset Surface Cross-Section
- **Input**: `surface_pca([surf1, surf2, ...]) list input`
- **Expected Behavior**: Automatically converts list of 2D surfaces to 3D numpy tensor
- **Actual Behavior**: `AttributeError: 'list' object has no attribute 'shape'`
- **Root Cause**: Directly called .shape on input parameter without np.asarray()
- **Resolution**: Converted input via np.asarray(surface_matrices) and supported both dict and dataclass attribute access
- **Regression Test**: `tests/test_signals_vrp.py`
- **Status**: **PASSED**

---

### [BUG-03] kuwala.signals.realized_vol — Severity: `MEDIUM`
- **Date**: 2026-08-25
- **Dataset / Trigger**: Nasdaq-100 Intraday Data (novandra)
- **Input**: `Tab-delimited or whitespace-padded CSV columns`
- **Expected Behavior**: Robust case-insensitive and whitespace-stripped column matching
- **Actual Behavior**: `KeyError on unstripped column names`
- **Root Cause**: Column lowercasing did not strip whitespace / delimiter tabs
- **Resolution**: Applied [str(c).strip().lower() for c in data.columns]
- **Regression Test**: `tests/test_stress_and_edge_cases.py::test_realized_vol_zero_variance_handling`
- **Status**: **PASSED**

---

### [BUG-04] kuwala.signals.vrp — Severity: `LOW`
- **Date**: 2026-08-25
- **Dataset / Trigger**: Real-world Historical Options & OHLC Pipelines
- **Input**: `vrp(surface, hist_prices=df)`
- **Expected Behavior**: Accepts hist_prices as parameter or alias for price_history
- **Actual Behavior**: `TypeError: vrp() got an unexpected keyword argument 'hist_prices'`
- **Root Cause**: vrp() only declared price_history without alias support
- **Resolution**: Added hist_prices optional parameter defaulting to price_history
- **Regression Test**: `tests/test_signals_vrp.py::test_vrp_signal_computation`
- **Status**: **PASSED**

---

### [BUG-05] kuwala.volatility.surface — Severity: `HIGH`
- **Date**: 2026-08-25
- **Dataset / Trigger**: Single-Tenor Options Expiry Slices
- **Input**: `surface.implied_volatility() and surface.local_vol() on 1-tenor surface`
- **Expected Behavior**: Graceful 1D interpolation and flat slice local volatility
- **Actual Behavior**: `RegularGridInterpolator crashed due to len(expiries) < 2`
- **Root Cause**: Assumed multi-tenor grid in 2D interpolator
- **Resolution**: Added conditional 1D interpolation fallback (interp1d) when len(expiries) == 1
- **Regression Test**: `tests/test_stress_and_edge_cases.py::test_single_tenor_surface`
- **Status**: **PASSED**

---
