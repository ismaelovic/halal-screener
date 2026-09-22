"""Company lookup/search.

Search combines the local seeded `companies` table with a live provider
lookup (`search_live`) for anything not already seeded — see ticket 5. The
screening flow (`services/screening_service.py`) is what actually persists
a live-fetched company; search itself never writes to the database.
"""

from sqlmodel import Session, or_, select

from halal_screener.models import Company
from halal_screener.providers.base import FundamentalsProvider
from halal_screener.providers.schemas import SearchResult

SEARCH_LIMIT = 20


def split_symbol(symbol: str) -> tuple[str, str]:
    """`symbol` is a `TICKER.EXCHANGE` pair, e.g. `AAPL.US` or `NOVO-B.CO`."""
    ticker, dot, exchange = symbol.rpartition(".")
    if not dot:
        ticker, exchange = symbol, ""
    return ticker, exchange


def search_companies(session: Session, query: str) -> list[Company]:
    like_query = f"%{query}%"
    statement = (
        select(Company)
        .where(
            Company.is_active == True,  # noqa: E712
            or_(Company.name.ilike(like_query), Company.ticker.ilike(like_query)),
        )
        .limit(SEARCH_LIMIT)
    )
    return list(session.exec(statement))


def search_live(
    provider: FundamentalsProvider, query: str, exclude: set[tuple[str, str]]
) -> list[SearchResult]:
    """Best-effort live company-name search for tickers not already in
    `exclude` (local matches, keyed by upper-cased (ticker, exchange)). A
    provider hiccup here shouldn't break the whole search response — swallow
    and return nothing extra rather than raising.
    """
    try:
        results = provider.search(query)
    except Exception:  # noqa: BLE001 — best-effort, log and degrade gracefully
        return []

    return [r for r in results if (r.ticker.upper(), r.exchange.upper()) not in exclude]


def get_by_symbol(session: Session, symbol: str) -> Company | None:
    ticker, exchange = split_symbol(symbol)
    statement = select(Company).where(
        Company.ticker.ilike(ticker), Company.exchange.ilike(exchange)
    )
    return session.exec(statement).first()

