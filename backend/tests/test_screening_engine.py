"""Pure unit tests for the screening engine — no DB, no network, no FastAPI."""

import pytest

from halal_screener.screening.engine import (
    InsufficientDataError,
    ScreeningInput,
    business_activity_screen,
    financial_ratios_screen,
    screen_company,
)


class TestBusinessActivityScreen:
    def test_compliant_industry_passes(self):
        assert business_activity_screen("Health Care", "Biotechnology") == "compliant"

    def test_non_compliant_industry_fails(self):
        assert business_activity_screen("Financial Services", "Banks - Regional") == "non_compliant"

    def test_non_compliant_sector_alone_fails(self):
        assert business_activity_screen("Financial Services", "Some Unlisted Industry") == "non_compliant"

    def test_missing_data_is_review(self):
        assert business_activity_screen(None, None) == "review"

    def test_matching_is_case_insensitive(self):
        assert business_activity_screen("financial services", "BANKS - REGIONAL") == "non_compliant"

    def test_unmapped_but_present_industry_is_compliant(self):
        assert business_activity_screen("Technology", "Software") == "compliant"


class TestFinancialRatiosScreen:
    def test_clean_ratios_pass(self):
        result = financial_ratios_screen(market_cap=1000.0, total_debt=100.0, cash_and_equivalents=50.0)
        assert result.debt_ratio == pytest.approx(0.1)
        assert result.cash_ratio == pytest.approx(0.05)
        assert result.debt_ratio_pass is True
        assert result.cash_ratio_pass is True

    def test_debt_ratio_exactly_at_threshold_fails(self):
        result = financial_ratios_screen(market_cap=1000.0, total_debt=330.0, cash_and_equivalents=0.0)
        assert result.debt_ratio == pytest.approx(0.33)
        assert result.debt_ratio_pass is False  # strict <, boundary itself fails

    def test_debt_ratio_just_below_threshold_passes(self):
        result = financial_ratios_screen(market_cap=1000.0, total_debt=329.0, cash_and_equivalents=0.0)
        assert result.debt_ratio_pass is True

    def test_cash_ratio_just_above_threshold_fails(self):
        result = financial_ratios_screen(market_cap=1000.0, total_debt=0.0, cash_and_equivalents=331.0)
        assert result.cash_ratio_pass is False

    def test_none_market_cap_raises(self):
        with pytest.raises(InsufficientDataError):
            financial_ratios_screen(market_cap=None, total_debt=100.0, cash_and_equivalents=50.0)

    def test_zero_market_cap_raises(self):
        with pytest.raises(InsufficientDataError):
            financial_ratios_screen(market_cap=0.0, total_debt=100.0, cash_and_equivalents=50.0)

    def test_missing_debt_and_cash_default_to_zero(self):
        result = financial_ratios_screen(market_cap=1000.0, total_debt=None, cash_and_equivalents=None)
        assert result.debt_ratio == 0.0
        assert result.cash_ratio == 0.0
        assert result.debt_ratio_pass is True
        assert result.cash_ratio_pass is True


class TestScreenCompany:
    def test_halal_verdict(self):
        outcome = screen_company(
            ScreeningInput(
                sector="Health Care",
                industry="Biotechnology",
                market_cap=1000.0,
                total_debt=100.0,
                cash_and_equivalents=50.0,
            )
        )
        assert outcome.verdict == "halal"
        assert outcome.flagged_reasons == []

    def test_haram_verdict_from_business_activity(self):
        outcome = screen_company(
            ScreeningInput(
                sector="Financial Services",
                industry="Banks - Regional",
                market_cap=1000.0,
                total_debt=100.0,
                cash_and_equivalents=50.0,
            )
        )
        assert outcome.verdict == "haram"
        assert any("non-compliant" in r for r in outcome.flagged_reasons)

    def test_haram_verdict_from_debt_ratio(self):
        outcome = screen_company(
            ScreeningInput(
                sector="Technology",
                industry="Software",
                market_cap=1000.0,
                total_debt=500.0,
                cash_and_equivalents=50.0,
            )
        )
        assert outcome.verdict == "haram"
        assert any("debt ratio" in r for r in outcome.flagged_reasons)

    def test_questionable_verdict_from_missing_sector_data(self):
        outcome = screen_company(
            ScreeningInput(
                sector=None,
                industry=None,
                market_cap=1000.0,
                total_debt=100.0,
                cash_and_equivalents=50.0,
            )
        )
        assert outcome.verdict == "questionable"
