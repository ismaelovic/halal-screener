from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from halal_screener.database import get_session
from halal_screener.schemas import CompanySummary, SearchResponse
from halal_screener.services.company_service import get_by_symbol, search_companies

router = APIRouter()


@router.get("/companies/search", response_model=SearchResponse)
def search(q: str, session: Session = Depends(get_session)) -> SearchResponse:
    companies = search_companies(session, q)
    return SearchResponse(
        results=[
            CompanySummary(
                ticker=c.ticker, exchange=c.exchange, name=c.name, sector=c.sector, industry=c.industry
            )
            for c in companies
        ]
    )


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
