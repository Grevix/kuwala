"""
Data Adapters Package.
"""

from kuwala.data.adapters.base import BaseAdapter
from kuwala.data.adapters.dukascopy import DukascopyAdapter, aggregate_ticks_to_ohlcv
from kuwala.data.adapters.fred import FredAdapter
from kuwala.data.adapters.nasdaq import NasdaqDataLinkAdapter
from kuwala.data.adapters.sec_edgar import SecEdgarAdapter
from kuwala.data.adapters.yahoo import YahooAdapter

__all__ = [
    "BaseAdapter",
    "YahooAdapter",
    "FredAdapter",
    "SecEdgarAdapter",
    "DukascopyAdapter",
    "NasdaqDataLinkAdapter",
    "aggregate_ticks_to_ohlcv",
]
