from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from halal_screener.database import get_session
from halal_screener.providers.base import FundamentalsProvider
from halal_screener.providers.dependency import get_fundamentals_provider
from halal_screener.schemas import CompanySummary, SearchResponse
from halal_screener.services.company_service import (
    SEARCH_LIMIT,
    get_by_symbol,
    search_companies,
    search_live,
)

router = APIRouter()

MIN_LIVE_SEARCH_QUERY_LENGTH = 2


@router.get("/companies/search", response_model=SearchResponse)
def search(
    q: str,
    session: Session = Depends(get_session),
    provider: FundamentalsProvider = Depends(get_fundamentals_provider),
) -> SearchResponse:
    local = search_companies(session, q)
    results = [
        CompanySummary(
            ticker=c.ticker, exchange=c.exchange, name=c.name, sector=c.sector, industry=c.industry
        )
        for c in local
    ]

    if len(q.strip()) >= MIN_LIVE_SEARCH_QUERY_LENGTH:
        exclude = {(c.ticker.upper(), c.exchange.upper()) for c in local}
        live = search_live(provider, q, exclude)
        results.extend(
            CompanySummary(ticker=r.ticker, exchange=r.exchange, name=r.name)
            for r in live
        )

    return SearchResponse(results=results[:SEARCH_LIMIT])


@router.get("/companies/{symbol}", response_model=CompanySummary)
def get_company(symbol: str, session: Session = Depends(get_session)):
    company = get_by_symbol(session, symbol)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanySummary(
        ticker=company.ticker,
        exchange=company.exchange,
        name=company.name,
        sector=company.sector,
        industry=company.industry,
    )
