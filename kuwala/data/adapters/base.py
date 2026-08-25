"""
Base Data Adapter Interface.

LEGAL BOUNDARY & COMPLIANCE:
Fetching data at runtime under the user's own credentials and acceptance of the
upstream data vendor's Terms of Service is legally durable practice. Kuwala strictly
refuses to vendor, distribute, or bundle proprietary market data inside its repo,
wheels, or artifacts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


class BaseAdapter(ABC):
    """
    Abstract base class for all Kuwala data adapters.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the data source."""
        pass

    @property
    @abstractmethod
    def terms_of_service_url(self) -> str:
        """URL to upstream Terms of Service."""
        pass

    @abstractmethod
    def fetch(self, symbol: str, **kwargs: Any) -> Any:
        """Fetch market data from upstream source."""
        pass
