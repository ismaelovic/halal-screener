"""Provider mapping tests against a saved sample JSON response.

NOTE: `tests/fixtures/eodhd_aapl_sample.json` is a hand-built sample matching
EODHD's *documented* schema, not a response captured from a live API key —
see the module docstring in providers/eodhd.py. Replace it with a real
captured response during implementation step 3 (validate against real data)
and re-run this test to confirm the mapping still holds.
"""

import json
from datetime import date
from pathlib import Path

from halal_screener.providers.eodhd import _map_fundamentals

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "eodhd_aapl_sample.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def test_maps_general_fields():
    payload = load_fixture()
    result = _map_fundamentals("AAPL", "US", payload)

    assert result.ticker == "AAPL"
    assert result.exchange == "US"
    assert result.name == "Apple Inc"
    assert result.sector == "Technology"
    assert result.industry == "Consumer Electronics"
    assert result.currency == "USD"
    assert result.isin == "US0378331005"


def test_maps_market_cap():
    payload = load_fixture()
    result = _map_fundamentals("AAPL", "US", payload)
    assert result.market_cap == 3500000000000


def test_picks_latest_balance_sheet_period():
    payload = load_fixture()
    result = _map_fundamentals("AAPL", "US", payload)

    # latest period is 2024-09-30, not 2023-09-30
    assert result.as_of_date == date(2024, 9, 30)
    assert result.cash_and_equivalents == 29943000000
    # gross debt = longTermDebt + shortLongTermDebt for the latest period
    assert result.total_debt == 85750000000 + 10912000000


def test_maps_total_revenue_from_latest_period():
    payload = load_fixture()
    result = _map_fundamentals("AAPL", "US", payload)
    assert result.total_revenue == 391035000000


def test_stores_full_raw_payload():
    payload = load_fixture()
    result = _map_fundamentals("AAPL", "US", payload)
    assert result.raw_payload == payload


def test_missing_short_term_debt_falls_back_to_long_term_only():
    payload = load_fixture()
    del payload["Financials"]["Balance_Sheet"]["yearly"]["2024-09-30"]["shortLongTermDebt"]
    result = _map_fundamentals("AAPL", "US", payload)
    assert result.total_debt == 85750000000
