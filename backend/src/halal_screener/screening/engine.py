"""Pure screening functions — no DB, no HTTP, no FastAPI imports.

Everything here operates on plain values/dataclasses so it can be
exhaustively unit tested with hand-picked numbers, independent of whether
the database or the EODHD provider exist or are reachable.
"""

from dataclasses import dataclass, field
from typing import Literal

from halal_screener.screening.rules import (
    CASH_RATIO_THRESHOLD,
    DEBT_RATIO_THRESHOLD,
    NON_COMPLIANT_INDUSTRIES,
    NON_COMPLIANT_SECTORS,
)

BusinessActivityStatus = Literal["compliant", "non_compliant", "review"]
Verdict = Literal["halal", "haram", "questionable"]


class InsufficientDataError(ValueError):
    """Raised when a screen can't be computed from the given inputs."""


def business_activity_screen(sector: str | None, industry: str | None) -> BusinessActivityStatus:
    """Core-business exclusion check against the curated non-compliant list.

    Missing sector/industry data (nothing returned by the provider) is
    "review", not an assumed pass — see rules.py's module docstring for why.
    """
    if not sector and not industry:
        return "review"

    normalized_sector = (sector or "").strip().lower()
    normalized_industry = (industry or "").strip().lower()

    if normalized_sector in NON_COMPLIANT_SECTORS:
        return "non_compliant"
    if normalized_industry in NON_COMPLIANT_INDUSTRIES:
        return "non_compliant"

    return "compliant"


@dataclass
class RatiosResult:
    debt_ratio: float
    cash_ratio: float
    debt_ratio_pass: bool
    cash_ratio_pass: bool


def financial_ratios_screen(
    market_cap: float | None,
    total_debt: float | None,
    cash_and_equivalents: float | None,
) -> RatiosResult:
    """Computes the debt-ratio and cash-ratio screens.

    Raises InsufficientDataError (never a bare ZeroDivisionError) if
    market_cap is missing or non-positive, since both ratios divide by it.
    """
    if market_cap is None or market_cap <= 0:
        raise InsufficientDataError("market_cap must be a positive number to compute ratios")

    debt_ratio = (total_debt or 0.0) / market_cap
    cash_ratio = (cash_and_equivalents or 0.0) / market_cap

    return RatiosResult(
        debt_ratio=debt_ratio,
        cash_ratio=cash_ratio,
        debt_ratio_pass=debt_ratio < DEBT_RATIO_THRESHOLD,
        cash_ratio_pass=cash_ratio < CASH_RATIO_THRESHOLD,
    )


@dataclass
class ScreeningInput:
    sector: str | None
    industry: str | None
    market_cap: float | None
    total_debt: float | None
    cash_and_equivalents: float | None


@dataclass
class ScreeningOutcome:
    business_activity_status: BusinessActivityStatus
    debt_ratio: float
    cash_ratio: float
    debt_ratio_pass: bool
    cash_ratio_pass: bool
    verdict: Verdict
    flagged_reasons: list[str] = field(default_factory=list)


def screen_company(inputs: ScreeningInput) -> ScreeningOutcome:
    activity_status = business_activity_screen(inputs.sector, inputs.industry)
    ratios = financial_ratios_screen(
        inputs.market_cap, inputs.total_debt, inputs.cash_and_equivalents
    )

    reasons: list[str] = []
    if activity_status == "non_compliant":
        reasons.append(
            f"core business in a non-compliant sector/industry "
            f"(sector={inputs.sector!r}, industry={inputs.industry!r})"
        )
    if activity_status == "review":
        reasons.append("sector/industry data missing — needs manual review")
    if not ratios.debt_ratio_pass:
        reasons.append(
            f"debt ratio {ratios.debt_ratio:.2%} exceeds {DEBT_RATIO_THRESHOLD:.0%} threshold"
        )
    if not ratios.cash_ratio_pass:
        reasons.append(
            f"cash ratio {ratios.cash_ratio:.2%} exceeds {CASH_RATIO_THRESHOLD:.0%} threshold"
        )

    if activity_status == "non_compliant" or not ratios.debt_ratio_pass or not ratios.cash_ratio_pass:
        verdict: Verdict = "haram"
    elif activity_status == "review":
        verdict = "questionable"
    else:
        verdict = "halal"

    return ScreeningOutcome(
        business_activity_status=activity_status,
        debt_ratio=ratios.debt_ratio,
        cash_ratio=ratios.cash_ratio,
        debt_ratio_pass=ratios.debt_ratio_pass,
        cash_ratio_pass=ratios.cash_ratio_pass,
        verdict=verdict,
        flagged_reasons=reasons,
    )
