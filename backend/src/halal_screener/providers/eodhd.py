"""EODHD (https://eodhd.com/financial-apis/) fundamentals provider.

IMPORTANT — verify-before-trusting note (see plan doc, build order step 3):
the Balance_Sheet field used for `total_debt` below is a best-guess mapping
from EODHD's documented schema, not yet confirmed against a live response.
Before running the real seed script, pull 2-3 real responses (e.g. AAPL.US,
a bank ticker, NOVO-B.CO), inspect them, and correct `_map_fundamentals` if
the field names differ. The full raw payload is always stored alongside the
mapped values specifically so this can be fixed later without re-fetching.
"""

from datetime import date
from typing import Any

import httpx

from halal_screener.providers.base import FundamentalsProvider
from halal_screener.providers.schemas import RawFundamentals, SearchResult

BASE_URL = "https://eodhd.com/api"
TIMEOUT_SECONDS = 10.0


class EODHDProvider(FundamentalsProvider):
    def __init__(self, api_key: str, client: httpx.Client | None = None):
        self.api_key = api_key
        self._client = client or httpx.Client(base_url=BASE_URL, timeout=TIMEOUT_SECONDS)

    def search(self, query: str) -> list[SearchResult]:
        response = self._get(f"/search/{query}")
        return [
            SearchResult(
                ticker=item.get("Code", ""),
                exchange=item.get("Exchange", ""),
                name=item.get("Name", ""),
            )
            for item in response
        ]

    def get_fundamentals(self, ticker: str, exchange: str) -> RawFundamentals:
        payload = self._get(f"/fundamentals/{ticker}.{exchange}")
        return _map_fundamentals(ticker, exchange, payload)

    def _get(self, path: str) -> Any:
        response = self._client.get(
            path, params={"api_token": self.api_key, "fmt": "json"}
        )
        response.raise_for_status()
        return response.json()


def _latest_period(yearly: dict[str, Any] | None) -> dict[str, Any]:
    """EODHD returns yearly financial statement rows keyed by period-end date
    (e.g. {"2025-12-31": {...}, "2024-12-31": {...}}); pick the most recent.
    """
    if not yearly:
        return {}
    latest_key = max(yearly.keys())
    return yearly[latest_key] or {}


def _as_float(value: Any) -> float | None:
    if value in (None, "", "None"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_date(value: Any) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _map_fundamentals(ticker: str, exchange: str, payload: dict[str, Any]) -> RawFundamentals:
    general = payload.get("General", {}) or {}
    highlights = payload.get("Highlights", {}) or {}
    financials = payload.get("Financials", {}) or {}

    balance_sheet = _latest_period((financials.get("Balance_Sheet") or {}).get("yearly"))
    income_statement = _latest_period((financials.get("Income_Statement") or {}).get("yearly"))

    # Gross interest-bearing debt (long-term + short-term), NOT EODHD's
    # `netDebt` — netDebt already subtracts cash, which would double-count
    # against the separate cash-ratio screen. `shortLongTermDebt` may not be
    # present for every ticker; falls back to long-term only if so.
    total_debt = _as_float(balance_sheet.get("longTermDebt"))
    short_term_debt = _as_float(balance_sheet.get("shortLongTermDebt"))
    if total_debt is not None and short_term_debt is not None:
        total_debt += short_term_debt

    return RawFundamentals(
        ticker=ticker,
        exchange=exchange,
        name=general.get("Name", ""),
        country=general.get("CountryName"),
        sector=general.get("Sector"),
        industry=general.get("Industry"),
        currency=general.get("CurrencyCode"),
        isin=general.get("ISIN"),
        market_cap=_as_float(highlights.get("MarketCapitalization")),
        total_debt=total_debt,
        cash_and_equivalents=_as_float(balance_sheet.get("cash")),
        total_revenue=_as_float(income_statement.get("totalRevenue")),
        as_of_date=_as_date(balance_sheet.get("date")),
        raw_payload=payload,
    )
