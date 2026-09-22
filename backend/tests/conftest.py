"""Pytest fixtures, mirroring underskriv_dk's conftest.py pattern."""

from collections.abc import Generator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from halal_screener.app import app
from halal_screener.database import get_session
from halal_screener.models import Company, FinancialRatios, ScreeningResult
from halal_screener.providers.base import FundamentalsProvider
from halal_screener.providers.dependency import get_fundamentals_provider
from halal_screener.providers.schemas import RawFundamentals, SearchResult


class FakeProvider(FundamentalsProvider):
    """In-memory stand-in for YFinanceProvider — never touches the network.

    `fetch_calls` records every `get_fundamentals` call so tests can assert
    on cache-hit vs cache-miss behavior. Ticker "BROKEN.US" simulates an
    upstream provider failure (as opposed to a genuinely unknown ticker,
    which raises ValueError like the real provider does for a nonexistent
    symbol).
    """

    def __init__(self) -> None:
        self.fetch_calls: list[str] = []
        self.search_calls: list[str] = []
        self._data: dict[tuple[str, str], RawFundamentals] = {
            ("NEWCO", "US"): RawFundamentals(
                ticker="NEWCO",
                exchange="US",
                name="New Co Inc",
                country="US",
                sector="Technology",
                industry="Software - Application",
                currency="USD",
                isin=None,
                market_cap=1_000_000.0,
                total_debt=100_000.0,
                cash_and_equivalents=100_000.0,
                total_revenue=500_000.0,
                as_of_date=date(2025, 1, 1),
                raw_payload={},
            ),
            ("NOSCREEN", "US"): RawFundamentals(
                ticker="NOSCREEN",
                exchange="US",
                name="No Screening Yet",
                country="US",
                sector="Technology",
                industry="Software - Application",
                currency="USD",
                isin=None,
                market_cap=1_000_000.0,
                total_debt=100_000.0,
                cash_and_equivalents=100_000.0,
                total_revenue=500_000.0,
                as_of_date=date(2025, 1, 1),
                raw_payload={},
            ),
        }

    def search(self, query: str) -> list[SearchResult]:
        self.search_calls.append(query)
        needle = query.lower()
        return [
            SearchResult(ticker=t, exchange=e, name=d.name)
            for (t, e), d in self._data.items()
            if needle in d.name.lower()
        ]

    def get_fundamentals(self, ticker: str, exchange: str) -> RawFundamentals:
        self.fetch_calls.append(f"{ticker}.{exchange}")
        if ticker == "BROKEN":
            raise RuntimeError("simulated provider outage")
        key = (ticker, exchange)
        if key not in self._data:
            raise ValueError(f"no data returned by fake provider for {ticker}.{exchange}")
        return self._data[key]


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="fake_provider")
def fake_provider_fixture() -> FakeProvider:
    return FakeProvider()


@pytest.fixture(name="client")
def client_fixture(
    session: Session, fake_provider: FakeProvider
) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    def get_provider_override():
        return fake_provider

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_fundamentals_provider] = get_provider_override
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
