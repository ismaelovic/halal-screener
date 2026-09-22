"""yfinance (unofficial Yahoo Finance wrapper) fundamentals provider.

Chosen over EODHD's paid Fundamentals Data Feed ($59.99/mo, not included in
the free plan we're on) — see the seed-run 403s that surfaced this. Verified
live against the full seed ticker list before writing this mapping:
`sector`/`industry` come from Yahoo's own fixed taxonomy (e.g. "Banks -
Regional", "Insurance - Diversified", "Beverages - Brewers" — see
screening/rules.py, which was updated to match these exact strings).

Caveat (unofficial API): this scrapes Yahoo Finance's undocumented endpoints
via the `yfinance` package. It can break without notice if Yahoo changes
their site. The full raw `.info` dict is stored in `raw_payload` so a broken
field mapping can be fixed later without re-fetching.
"""

from datetime import date, datetime, timezone
from typing import Any

import yfinance as yf

from halal_screener.providers.base import FundamentalsProvider
from halal_screener.providers.schemas import RawFundamentals, SearchResult

# Yahoo's ticker suffix only differs from our internal exchange code for US
# listings (no suffix at all). Every other exchange in the seed list (CO, OL,
# ST, HE, AS, PA, DE, L) uses the same code as Yahoo's own suffix — verified
# live, not guessed.
_US_EXCHANGE_CODE = "US"


def _to_yahoo_symbol(ticker: str, exchange: str) -> str:
    if exchange == _US_EXCHANGE_CODE:
        return ticker
    return f"{ticker}.{exchange}"


def _as_float(value: Any) -> float | None:
    if value in (None, "", "None"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_of_date(info: dict[str, Any]) -> date | None:
    timestamp = info.get("lastFiscalYearEnd") or info.get("mostRecentQuarter")
    if not timestamp:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).date()


class YFinanceProvider(FundamentalsProvider):
    def search(self, query: str) -> list[SearchResult]:
        # Not used by the running app in V1 (company search only hits the
        # local seeded table — see plan doc), kept only to satisfy the
        # FundamentalsProvider interface. Yahoo's own exchange codes here
        # (e.g. "CPH", "GER") are NOT translated to our internal exchange
        # vocabulary since nothing consumes this path yet.
        results = yf.Search(query, max_results=10).quotes
        return [
            SearchResult(
                ticker=item.get("symbol", ""),
                exchange=item.get("exchange", ""),
                name=item.get("longname") or item.get("shortname", ""),
            )
            for item in results
        ]

    def get_fundamentals(self, ticker: str, exchange: str) -> RawFundamentals:
        symbol = _to_yahoo_symbol(ticker, exchange)
        info = yf.Ticker(symbol).info

        if not info.get("longName") and not info.get("shortName"):
            raise ValueError(f"no data returned by yfinance for {symbol!r}")

        return RawFundamentals(
            ticker=ticker,
            exchange=exchange,
            name=info.get("longName") or info.get("shortName") or "",
            country=info.get("country"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            currency=info.get("currency"),
            isin=info.get("isin"),
            market_cap=_as_float(info.get("marketCap")),
            total_debt=_as_float(info.get("totalDebt")),
            cash_and_equivalents=_as_float(info.get("totalCash")),
            total_revenue=_as_float(info.get("totalRevenue")),
            as_of_date=_as_of_date(info),
            raw_payload=info,
        )
