"""Pytest fixtures, mirroring underskriv_dk's conftest.py pattern."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from halal_screener.app import app
from halal_screener.database import get_session
from halal_screener.models import Company, FinancialRatios, ScreeningResult


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="seeded_session")
def seeded_session_fixture(session: Session) -> Session:
    """Three hand-picked companies covering halal / haram / questionable."""
    halal_co = Company(
        ticker="CLEANCO", exchange="US", name="Clean Pharma Inc", sector="Health Care", industry="Biotechnology"
    )
    haram_co = Company(
        ticker="BIGBANK", exchange="US", name="Big Conventional Bank", sector="Financial Services", industry="Banks - Regional"
    )
    review_co = Company(
        ticker="MYSTERY", exchange="US", name="Mystery Holdings", sector=None, industry=None
    )
    session.add_all([halal_co, haram_co, review_co])
    session.commit()
    for c in (halal_co, haram_co, review_co):
        session.refresh(c)

    def _add_ratios_and_result(
        company: Company, debt_ratio: float, cash_ratio: float, status: str, verdict: str
    ) -> None:
        ratios = FinancialRatios(
            company_id=company.id,
            market_cap=1_000_000.0,
            total_debt=debt_ratio * 1_000_000.0,
            cash_and_equivalents=cash_ratio * 1_000_000.0,
            total_revenue=500_000.0,
            debt_ratio=debt_ratio,
            cash_ratio=cash_ratio,
            sector=company.sector,
            industry=company.industry,
            raw_provider_payload={},
        )
        session.add(ratios)
        session.commit()
        session.refresh(ratios)

        result = ScreeningResult(
            company_id=company.id,
            financial_ratios_id=ratios.id,
            business_activity_status=status,
            debt_ratio_pass=debt_ratio < 0.33,
            cash_ratio_pass=cash_ratio < 0.33,
            verdict=verdict,
            flagged_reasons=[],
        )
        session.add(result)
        session.commit()

    _add_ratios_and_result(halal_co, debt_ratio=0.1, cash_ratio=0.1, status="compliant", verdict="halal")
    _add_ratios_and_result(haram_co, debt_ratio=0.1, cash_ratio=0.1, status="non_compliant", verdict="haram")
    _add_ratios_and_result(review_co, debt_ratio=0.1, cash_ratio=0.1, status="review", verdict="questionable")

    return session
