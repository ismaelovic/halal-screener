"""SQLModel table definitions.

Kept in sync by hand with backend/migrations/0001_init.sql (see that file's
header comment) — V1 uses raw SQL migrations against Supabase, not Alembic.
"""

import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlmodel import JSON, Column, Field, SQLModel


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: str = Field(default_factory=_uuid, primary_key=True)
    ticker: str = Field(index=True)
    exchange: str
    name: str
    country: str | None = None
    sector: str | None = None
    industry: str | None = None
    currency: str | None = None
    isin: str | None = None
    logo_url: str | None = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class FinancialRatios(SQLModel, table=True):
    __tablename__ = "financial_ratios"

    id: str = Field(default_factory=_uuid, primary_key=True)
    company_id: str = Field(foreign_key="companies.id", index=True)
    as_of_date: date | None = None

    market_cap: float | None = None
    total_debt: float | None = None
    cash_and_equivalents: float | None = None
    total_revenue: float | None = None

    # Reserved for V2 — no data source for these in V1 (see plan doc).
    non_compliant_revenue: float | None = None
    impure_revenue_ratio: float | None = None

    debt_ratio: float | None = None
    cash_ratio: float | None = None

    # Denormalized snapshot of the company's sector/industry at fetch time,
    # so a later company-record edit doesn't rewrite audit history.
    sector: str | None = None
    industry: str | None = None

    raw_provider_payload: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    source: str = Field(default="yfinance")
    fetched_at: datetime = Field(default_factory=_utcnow)


class ScreeningResult(SQLModel, table=True):
    __tablename__ = "screening_results"

    id: str = Field(default_factory=_uuid, primary_key=True)
    company_id: str = Field(foreign_key="companies.id", index=True)
    financial_ratios_id: str = Field(foreign_key="financial_ratios.id")

    # One of: "compliant", "non_compliant", "review"
    business_activity_status: str
    debt_ratio_pass: bool
    cash_ratio_pass: bool

    # One of: "halal", "haram", "questionable"
    verdict: str

    # Reserved for V2 (no impure-revenue data source in V1).
    purification_pct: float | None = None

    flagged_reasons: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    screened_at: datetime = Field(default_factory=_utcnow)
