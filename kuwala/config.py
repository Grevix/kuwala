"""
Configuration and Environment Management for Kuwala.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Automatically find and load .env file
_env_path = Path.cwd() / ".env"
if not _env_path.exists():
    _env_path = Path(__file__).resolve().parent.parent / ".env"

if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)


@dataclass
class KuwalaConfig:
    fred_api_key: Optional[str] = None
    nasdaq_api_key: Optional[str] = None
    sec_user_agent: str = "KuwalaResearch/0.1.0 (contact@kuwala.org)"
    data_dir: Path = Path.home() / ".kuwala" / "data"

    @classmethod
    def load(cls) -> KuwalaConfig:
        fred_key = (
            os.getenv("FRED_API_KEY")
            or os.getenv("FRED_(Federal Reserve Bank of St. Louis)_api_key")
            or os.getenv("KUWALA_FRED_API_KEY")
        )
        nasdaq_key = (
            os.getenv("NASDAQ_DATA_LINK_API_KEY")
            or os.getenv("Nasdaq_Data_Link_API_key")
            or os.getenv("KUWALA_NASDAQ_DATA_LINK_API_KEY")
        )
        sec_ua = os.getenv(
            "SEC_EDGAR_USER_AGENT", "KuwalaResearch/0.1.0 (contact@kuwala.org)"
        )
        custom_data_dir = os.getenv("KUWALA_DATA_DIR")
        data_path = Path(custom_data_dir) if custom_data_dir else Path.home() / ".kuwala" / "data"
        data_path.mkdir(parents=True, exist_ok=True)

        return cls(
            fred_api_key=fred_key,
            nasdaq_api_key=nasdaq_key,
            sec_user_agent=sec_ua,
            data_dir=data_path,
        )


_DEFAULT_CONFIG = KuwalaConfig.load()


def get_config() -> KuwalaConfig:
    return _DEFAULT_CONFIG
