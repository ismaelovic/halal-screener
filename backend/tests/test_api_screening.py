from sqlmodel import Session


def test_halal_verdict(client, seeded_session: Session):
    response = client.get("/api/companies/CLEANCO.US/screening")
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "halal"
    assert body["business_activity"]["status"] == "compliant"
    assert body["debt_ratio"]["passed"] is True
    assert "not financial advice" in body["disclaimer"].lower()


def test_haram_verdict(client, seeded_session: Session):
    response = client.get("/api/companies/BIGBANK.US/screening")
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "haram"
    assert body["business_activity"]["status"] == "non_compliant"


def test_questionable_verdict(client, seeded_session: Session):
    response = client.get("/api/companies/MYSTERY.US/screening")
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "questionable"
    assert body["business_activity"]["status"] == "review"


def test_unknown_company_returns_404(client, seeded_session: Session):
    response = client.get("/api/companies/NOPE.US/screening")
    assert response.status_code == 404


def test_company_without_cached_screening_triggers_live_fetch(client, session: Session):
    from halal_screener.models import Company

    session.add(Company(ticker="NOSCREEN", exchange="US", name="No Screening Yet"))
    session.commit()

    response = client.get("/api/companies/NOSCREEN.US/screening")
    assert response.status_code == 200
    assert response.json()["verdict"] == "halal"
