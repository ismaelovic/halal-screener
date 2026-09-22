"""Pydantic request/response DTOs for the API layer (kept separate from the
SQLModel table models in models.py)."""

from datetime import datetime

from pydantic import BaseModel

DISCLAIMER = (
    "This is not financial advice. Screening is based on publicly available "
    "fundamentals data and an AAOIFI-inspired methodology; verify "
    "independently before investing."
)


class CompanySummary(BaseModel):
    ticker: str
    exchange: str
    name: str
    sector: str | None = None
    industry: str | None = None


class SearchResponse(BaseModel):
    results: list[CompanySummary]


class RatioBreakdown(BaseModel):
    value: float
    threshold: float
    passed: bool


class BusinessActivity(BaseModel):
    status: str
    sector: str | None
    industry: str | None


class ScreeningResponse(BaseModel):
    ticker: str
    name: str
    verdict: str
    screened_at: datetime
    business_activity: BusinessActivity
    debt_ratio: RatioBreakdown
    cash_ratio: RatioBreakdown
    purification_pct: float | None
    flagged_reasons: list[str]
    disclaimer: str = DISCLAIMER
