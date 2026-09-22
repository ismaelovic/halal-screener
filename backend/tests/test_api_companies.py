from sqlmodel import Session


def test_search_finds_seeded_company(client, seeded_session: Session):
    response = client.get("/api/companies/search", params={"q": "Clean"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert any(r["ticker"] == "CLEANCO" for r in results)


def test_search_is_case_insensitive_on_ticker(client, seeded_session: Session):
    response = client.get("/api/companies/search", params={"q": "bigbank"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert any(r["ticker"] == "BIGBANK" for r in results)


def test_search_no_match_returns_empty(client, seeded_session: Session):
    response = client.get("/api/companies/search", params={"q": "NoSuchCompany"})
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_get_company_by_symbol(client, seeded_session: Session):
    response = client.get("/api/companies/CLEANCO.US")
    assert response.status_code == 200
    assert response.json()["name"] == "Clean Pharma Inc"


def test_get_company_unknown_symbol_404(client, seeded_session: Session):
    response = client.get("/api/companies/NOPE.US")
    assert response.status_code == 404
