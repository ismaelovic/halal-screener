"""Ticket 5 — live-lookup fallback beyond the seeded ticker list.

Uses the `fake_provider` fixture (see conftest.py) so none of this ever
touches real Yahoo Finance/network.
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from halal_screener.models import Company, FinancialRatios
from halal_screener.services.screening_service import is_stale


def test_is_stale_handles_naive_and_aware_datetimes():
    fresh_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    fresh_aware = datetime.now(timezone.utc)
    stale_naive = fresh_naive - timedelta(hours=48)
    stale_aware = fresh_aware - timedelta(hours=48)

    assert is_stale(fresh_naive, ttl_hours=24) is False
    assert is_stale(fresh_aware, ttl_hours=24) is False
    assert is_stale(stale_naive, ttl_hours=24) is True
    assert is_stale(stale_aware, ttl_hours=24) is True


def test_live_fetch_persists_new_company_and_caches_result(client, fake_provider):
    first = client.get("/api/companies/NEWCO.US/screening")
    assert first.status_code == 200
    assert first.json()["verdict"] == "halal"
    assert fake_provider.fetch_calls == ["NEWCO.US"]

    second = client.get("/api/companies/NEWCO.US/screening")
    assert second.status_code == 200
    assert fake_provider.fetch_calls == ["NEWCO.US"]  # served from cache, not re-fetched


def test_stale_cache_triggers_refetch(client, session: Session, fake_provider):
    first = client.get("/api/companies/NEWCO.US/screening")
    assert first.status_code == 200
    assert fake_provider.fetch_calls == ["NEWCO.US"]

    company = session.exec(select(Company).where(Company.ticker == "NEWCO")).one()
    ratios = session.exec(
        select(FinancialRatios).where(FinancialRatios.company_id == company.id)
    ).one()
    ratios.fetched_at = datetime.now(timezone.utc) - timedelta(hours=48)
    session.add(ratios)
    session.commit()

    second = client.get("/api/companies/NEWCO.US/screening")
    assert second.status_code == 200
    assert fake_provider.fetch_calls == ["NEWCO.US", "NEWCO.US"]  # re-fetched, was stale


def test_unknown_ticker_returns_404(client, fake_provider):
    response = client.get("/api/companies/NOPE.US/screening")
    assert response.status_code == 404


def test_provider_outage_returns_503(client, fake_provider):
    response = client.get("/api/companies/BROKEN.US/screening")
    assert response.status_code == 503


def test_search_includes_live_result_not_in_local_db(client, fake_provider):
    response = client.get("/api/companies/search", params={"q": "New Co"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert any(r["ticker"] == "NEWCO" and r["exchange"] == "US" for r in results)


def test_search_dedupes_live_result_already_local(client, session: Session, fake_provider):
    session.add(
        Company(
            ticker="NEWCO",
            exchange="US",
            name="New Co Inc",
            sector="Technology",
            industry="Software - Application",
        )
    )
    session.commit()

    response = client.get("/api/companies/search", params={"q": "New Co"})
    assert response.status_code == 200
    matches = [
        r for r in response.json()["results"] if r["ticker"] == "NEWCO" and r["exchange"] == "US"
    ]
    assert len(matches) == 1


def test_search_skips_live_lookup_for_very_short_query(client, fake_provider):
    response = client.get("/api/companies/search", params={"q": "n"})
    assert response.status_code == 200
    assert fake_provider.search_calls == []
