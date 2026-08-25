"""
Canonical Data Models for Options, Quotes, Chains, and Volatility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import pandas as pd
import pyarrow as pa

from kuwala.data.conventions import year_fraction


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


@dataclass(frozen=True)
class OptionQuote:
    underlying: str
    expiry: datetime
    strike: float
    option_type: OptionType
    bid: float
    ask: float
    mid: float
    last: Optional[float] = None
    volume: Optional[int] = None
    open_interest: Optional[int] = None
    implied_volatility: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_call(self) -> bool:
        return self.option_type == OptionType.CALL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "underlying": self.underlying,
            "expiry": self.expiry.isoformat(),
            "strike": self.strike,
            "option_type": self.option_type.value,
            "bid": self.bid,
            "ask": self.ask,
            "mid": self.mid,
            "last": self.last,
            "volume": self.volume,
            "open_interest": self.open_interest,
            "implied_volatility": self.implied_volatility,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class OptionChain:
    underlying: str
    spot: float
    quotes: List[OptionQuote]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    rate: float = 0.04
    dividend_yield: float = 0.0

    def __len__(self) -> int:
        return len(self.quotes)

    def expiries(self) -> List[datetime]:
        return sorted(list({q.expiry for q in self.quotes}))

    def strikes(self) -> List[float]:
        return sorted(list({q.strike for q in self.quotes}))

    def to_dataframe(self) -> pd.DataFrame:
        if not self.quotes:
            return pd.DataFrame(
                columns=[
                    "underlying",
                    "expiry",
                    "strike",
                    "option_type",
                    "bid",
                    "ask",
                    "mid",
                    "last",
                    "volume",
                    "open_interest",
                    "implied_volatility",
                    "timestamp",
                    "spot",
                    "rate",
                    "dividend_yield",
                    "ttm",
                    "moneyness",
                    "log_moneyness",
                ]
            )
        records = [q.to_dict() for q in self.quotes]
        df = pd.DataFrame.from_records(records)
        df["spot"] = self.spot
        df["rate"] = self.rate
        df["dividend_yield"] = self.dividend_yield
        df["expiry"] = pd.to_datetime(df["expiry"], utc=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df["ttm"] = df.apply(lambda row: year_fraction(row["timestamp"], row["expiry"]), axis=1)
        df["moneyness"] = df["strike"] / self.spot
        df["log_moneyness"] = df.apply(
            lambda r: math_log_moneyness(self.spot, r["strike"], r["ttm"], self.rate, self.dividend_yield),
            axis=1,
        )
        return df

    def to_arrow(self) -> pa.Table:
        df = self.to_dataframe()
        return pa.Table.from_pandas(df)


def math_log_moneyness(spot: float, strike: float, ttm: float, rate: float, div: float) -> float:
    import numpy as np

    forward = spot * np.exp((rate - div) * ttm)
    return float(np.log(strike / forward)) if forward > 0 and strike > 0 else 0.0


@dataclass
class VolatilityObservation:
    underlying: str
    timestamp: datetime
    expiry: datetime
    ttm: float
    strike: float
    forward: float
    log_moneyness: float
    option_type: OptionType
    market_price: float
    implied_volatility: float
    total_implied_variance: float
    bid_iv: Optional[float] = None
    ask_iv: Optional[float] = None
