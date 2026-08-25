"""
Unified loader for the compiled Rust kuwala_core extension module.
"""

from __future__ import annotations

_HAS_RUST_CORE = False
_core = None

try:
    from kuwala import kuwala_core as _core

    _HAS_RUST_CORE = hasattr(_core, "py_black_scholes")
except ImportError:
    try:
        import kuwala_core as _core

        _HAS_RUST_CORE = hasattr(_core, "py_black_scholes")
    except ImportError:
        _HAS_RUST_CORE = False


def has_rust_core() -> bool:
    return _HAS_RUST_CORE


def get_rust_core():
    return _core
