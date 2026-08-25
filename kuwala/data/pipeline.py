"""
Unified Data Pipeline: Fetch -> Clean -> Extract IV -> Store.
"""

from __future__ import annotations

from typing import Optional, Union, List
import pandas as pd

from kuwala.data.adapters.yahoo import YahooAdapter
from kuwala.data.adapters.fred import FredAdapter
from kuwala.data.adapters.sec_edgar import SecEdgarAdapter
from kuwala.data.adapters.dukascopy import DukascopyAdapter
from kuwala.data.adapters.nasdaq import NasdaqDataLinkAdapter
from kuwala.data.models import OptionChain, OptionQuote, OptionType
from kuwala.data.store import get_store, DataStore


ADAPTERS = {
    "yahoo": YahooAdapter(),
    "fred": FredAdapter(),
    "sec_edgar": SecEdgarAdapter(),
    "dukascopy": DukascopyAdapter(),
    "nasdaq": NasdaqDataLinkAdapter(),
}


def fetch(
    symbol: str,
    source: str = "yahoo",
    expiry: Optional[str] = None,
    rate: float = 0.04,
    dividend_yield: float = 0.0,
    **kwargs,
) -> OptionChain:
    """
    Fetch market data using the specified adapter.
    """
    source_lower = source.lower()
    adapter = ADAPTERS.get(source_lower)
    if not adapter:
        raise ValueError(f"Unknown data source '{source}'. Supported sources: {list(ADAPTERS.keys())}")

    if source_lower == "yahoo":
        return adapter.fetch(symbol, expiry=expiry, rate=rate, dividend_yield=dividend_yield, **kwargs)
    else:
        return adapter.fetch(symbol, **kwargs)


def clean_chain(
    chain: OptionChain,
    filter_crossed: bool = True,
    filter_zero_bid: bool = True,
    min_volume: int = 0,
    min_open_interest: int = 0,
    max_bid_ask_spread_pct: float = 0.8,
) -> OptionChain:
    """
    Clean raw option quotes by filtering out crossed markets, stale zero bids, and wide spreads.
    """
    cleaned_quotes: List[OptionQuote] = []

    for q in chain.quotes:
        # Check positive prices
        if q.bid < 0 or q.ask < 0 or q.mid <= 0:
            continue

        # Filter zero bid if requested
        if filter_zero_bid and q.bid <= 0.0:
            continue

        # Filter crossed markets (bid > ask)
        if filter_crossed and q.bid > q.ask and q.ask > 0.0:
            continue

        # Filter wide spreads
        if q.ask > 0 and q.bid > 0:
            spread_pct = (q.ask - q.bid) / q.mid
            if spread_pct > max_bid_ask_spread_pct:
                continue

        # Liquidity filters
        if q.volume is not None and q.volume < min_volume:
            continue
        if q.open_interest is not None and q.open_interest < min_open_interest:
            continue

        cleaned_quotes.append(q)

    return OptionChain(
        underlying=chain.underlying,
        spot=chain.spot,
        quotes=cleaned_quotes,
        timestamp=chain.timestamp,
        rate=chain.rate,
        dividend_yield=chain.dividend_yield,
    )
