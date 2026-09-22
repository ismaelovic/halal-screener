"""Normalized shapes returned by any FundamentalsProvider implementation.

These are what the rest of the app (screening_service, seed script) depends
on — provider-specific field-name mapping happens only inside each
provider's own module (e.g. providers/eodhd.py) and is never leaked out.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass
class SearchResult:
    ticker: str
    exchange: str
    name: str


@dataclass
class RawFundamentals:
    ticker: str
    exchange: str
    name: str
    country: str | None
    sector: str | None
    industry: str | None
    currency: str | None
    isin: str | None

    market_cap: float | None
    total_debt: float | None
    cash_and_equivalents: float | None
    total_revenue: float | None
    as_of_date: date | None

    # Full raw API response, stored verbatim in financial_ratios so a wrong
    # field-name mapping can be corrected later without re-fetching.
    raw_payload: dict[str, Any]
