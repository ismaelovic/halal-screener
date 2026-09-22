"""Company lookup/search against the local seeded database.

V1 only searches the pre-seeded `companies` table — it does not fall back to
a live EODHD search for arbitrary tickers (that's a V2 "request a stock"
feature per the plan doc).
"""

from sqlmodel import Session, or_, select

from halal_screener.models import Company

SEARCH_LIMIT = 20


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


def get_by_symbol(session: Session, symbol: str) -> Company | None:
    """`symbol` is a `TICKER.EXCHANGE` pair, e.g. `AAPL.US` or `NOVO-B.CO`."""
    ticker, _, exchange = symbol.rpartition(".")
    if not ticker:
        ticker, exchange = symbol, ""

    statement = select(Company).where(
        Company.ticker.ilike(ticker), Company.exchange.ilike(exchange)
    )
    return session.exec(statement).first()
