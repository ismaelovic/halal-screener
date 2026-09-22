from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from halal_screener.database import get_session
from halal_screener.schemas import BusinessActivity, RatioBreakdown, ScreeningResponse
from halal_screener.screening.rules import CASH_RATIO_THRESHOLD, DEBT_RATIO_THRESHOLD
from halal_screener.services.company_service import get_by_symbol
from halal_screener.services.screening_service import get_latest_screening

router = APIRouter()


@router.get("/companies/{symbol}/screening", response_model=ScreeningResponse)
def get_screening(symbol: str, session: Session = Depends(get_session)) -> ScreeningResponse:
    company = get_by_symbol(session, symbol)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    latest = get_latest_screening(session, company.id)
    if latest is None:
        raise HTTPException(status_code=404, detail="No screening result for this company yet")

    result, ratios = latest

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
