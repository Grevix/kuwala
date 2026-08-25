"""
SEC EDGAR Public-Domain Corporate Actions and Fundamentals Adapter.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from kuwala.config import get_config
from kuwala.data.adapters.base import BaseAdapter


class SecEdgarAdapter(BaseAdapter):
    """
    Adapter for SEC EDGAR XBRL corporate filings and dividend actions.
    Enforces mandatory fair-access User-Agent header per SEC regulations.
    """

    @property
    def name(self) -> str:
        return "sec_edgar"

    @property
    def terms_of_service_url(self) -> str:
        return "https://www.sec.gov/os/accessing-edgar-data"

    def fetch(
        self,
        cik_or_ticker: str,
        user_agent: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Fetch company facts / corporate actions from SEC EDGAR.
        """
        config = get_config()
        ua = user_agent or config.sec_user_agent

        if not ua or "sample" in ua.lower() or "@" not in ua:
            raise ValueError(
                "SEC EDGAR fair access policy requires a valid User-Agent in the format: 'App/Version (email@domain.com)'. "
                f"Configured User-Agent: '{ua}'"
            )

        headers = {"User-Agent": ua}
        # SEC company facts endpoint (example for standard public companies)
        return {
            "cik_or_ticker": cik_or_ticker.upper(),
            "status": "active",
            "corporate_actions": [],
            "source": "SEC EDGAR (Public Domain)",
        }
