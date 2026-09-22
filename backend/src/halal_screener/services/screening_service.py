"""Orchestrates: raw fundamentals -> screening engine -> persisted rows.

This is the only place that wires the pure `screening.engine` functions to
the database — the engine itself stays DB-free and independently testable.
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from halal_screener.models import Company, FinancialRatios, ScreeningResult
from halal_screener.providers.base import FundamentalsProvider
from halal_screener.providers.schemas import RawFundamentals
from halal_screener.screening.engine import ScreeningInput, screen_company
from halal_screener.services.company_service import get_by_symbol


def upsert_company(session: Session, fundamentals: RawFundamentals) -> Company:
    statement = select(Company).where(
        Company.ticker == fundamentals.ticker, Company.exchange == fundamentals.exchange
    )
    company = session.exec(statement).first()
    if company is None:
        company = Company(ticker=fundamentals.ticker, exchange=fundamentals.exchange)

    company.name = fundamentals.name
    company.country = fundamentals.country
    company.sector = fundamentals.sector
    company.industry = fundamentals.industry
    company.currency = fundamentals.currency
    company.isin = fundamentals.isin

    session.add(company)
    session.commit()
    session.refresh(company)
    return company


def screen_and_persist(session: Session, company: Company, fundamentals: RawFundamentals) -> ScreeningResult:
    """Runs the pure screening engine against fresh fundamentals and persists
    a FinancialRatios + ScreeningResult row pair for the company.
    """
    outcome = screen_company(
        ScreeningInput(
            sector=fundamentals.sector,
            industry=fundamentals.industry,
            market_cap=fundamentals.market_cap,
            total_debt=fundamentals.total_debt,
            cash_and_equivalents=fundamentals.cash_and_equivalents,
        )
    )

    ratios = FinancialRatios(
        company_id=company.id,
        as_of_date=fundamentals.as_of_date,
        market_cap=fundamentals.market_cap,
        total_debt=fundamentals.total_debt,
        cash_and_equivalents=fundamentals.cash_and_equivalents,
        total_revenue=fundamentals.total_revenue,
        debt_ratio=outcome.debt_ratio,
        cash_ratio=outcome.cash_ratio,
        sector=fundamentals.sector,
        industry=fundamentals.industry,
        raw_provider_payload=fundamentals.raw_payload,
    )
    session.add(ratios)
    session.commit()
    session.refresh(ratios)

    result = ScreeningResult(
        company_id=company.id,
        financial_ratios_id=ratios.id,
        business_activity_status=outcome.business_activity_status,
        debt_ratio_pass=outcome.debt_ratio_pass,
        cash_ratio_pass=outcome.cash_ratio_pass,
        verdict=outcome.verdict,
        purification_pct=None,
        flagged_reasons=outcome.flagged_reasons,
    )
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


def get_latest_screening(
    session: Session, company_id: str
) -> tuple[ScreeningResult, FinancialRatios] | None:
    statement = (
        select(ScreeningResult)
        .where(ScreeningResult.company_id == company_id)
        .order_by(ScreeningResult.screened_at.desc())
        .limit(1)
    )
    result = session.exec(statement).first()
    if result is None:
        return None

    ratios = session.get(FinancialRatios, result.financial_ratios_id)
    if ratios is None:
        return None

    return result, ratios


def is_stale(fetched_at: datetime, ttl_hours: int) -> bool:
    """SQLite drops tzinfo on round-trip (Postgres may not), so normalize to
    UTC-aware before comparing rather than assuming either.
    """
    aware_fetched_at = fetched_at if fetched_at.tzinfo else fetched_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - aware_fetched_at > timedelta(hours=ttl_hours)


def get_or_fetch_screening(
    session: Session,
    provider: FundamentalsProvider,
    ticker: str,
    exchange: str,
    ttl_hours: int,
) -> tuple[Company, ScreeningResult, FinancialRatios]:
    """Serves a cached screening result if one exists and isn't stale;
    otherwise fetches live fundamentals, persists them, and re-screens.

    Raises whatever `provider.get_fundamentals` raises on a cache miss/stale
    hit — a `ValueError` means "not a real ticker" (see yfinance_provider),
    anything else means the provider itself is unavailable. Both are left to
    the caller (the API route) to translate into the right HTTP status.
    """
    company = get_by_symbol(session, f"{ticker}.{exchange}")
    latest = get_latest_screening(session, company.id) if company else None

    if company is None or latest is None or is_stale(latest[1].fetched_at, ttl_hours):
        fundamentals = provider.get_fundamentals(ticker, exchange)
        company = upsert_company(session, fundamentals)
        result = screen_and_persist(session, company, fundamentals)
        ratios = session.get(FinancialRatios, result.financial_ratios_id)
        assert ratios is not None  # just written above
        return company, result, ratios

    result, ratios = latest
    return company, result, ratios
