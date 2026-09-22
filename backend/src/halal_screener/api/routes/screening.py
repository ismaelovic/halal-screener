from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from halal_screener.config import get_settings
from halal_screener.database import get_session
from halal_screener.providers.base import FundamentalsProvider
from halal_screener.providers.dependency import get_fundamentals_provider
from halal_screener.schemas import BusinessActivity, RatioBreakdown, ScreeningResponse
from halal_screener.screening.rules import CASH_RATIO_THRESHOLD, DEBT_RATIO_THRESHOLD
from halal_screener.services.company_service import split_symbol
from halal_screener.services.screening_service import get_or_fetch_screening

router = APIRouter()


@router.get("/companies/{symbol}/screening", response_model=ScreeningResponse)
def get_screening(
    symbol: str,
    session: Session = Depends(get_session),
    provider: FundamentalsProvider = Depends(get_fundamentals_provider),
) -> ScreeningResponse:
    ticker, exchange = split_symbol(symbol)
    ttl_hours = get_settings().FUNDAMENTALS_TTL_HOURS

    try:
        company, result, ratios = get_or_fetch_screening(
            session, provider, ticker, exchange, ttl_hours
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Company not found") from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Live data provider is temporarily unavailable — try again shortly",
        ) from exc

    return ScreeningResponse(
        ticker=f"{company.ticker}.{company.exchange}",
        name=company.name,
        verdict=result.verdict,
        screened_at=result.screened_at,
        business_activity=BusinessActivity(
            status=result.business_activity_status,
            sector=ratios.sector,
            industry=ratios.industry,
        ),
        debt_ratio=RatioBreakdown(
            value=ratios.debt_ratio or 0.0,
            threshold=DEBT_RATIO_THRESHOLD,
            passed=result.debt_ratio_pass,
        ),
        cash_ratio=RatioBreakdown(
            value=ratios.cash_ratio or 0.0,
            threshold=CASH_RATIO_THRESHOLD,
            passed=result.cash_ratio_pass,
        ),
        purification_pct=result.purification_pct,
        flagged_reasons=result.flagged_reasons,
    )
