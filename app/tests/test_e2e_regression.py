import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.medicine import MedicineProduct
from app.services.medicine_search import MedicineSearchService
from app.services.alternatives import AlternativeMatchingService
from app.services.price_comparison import PriceComparisonService
from app.schemas.pricing import PriceComparisonRequest
from app.schemas.medicine import AlternativeSearchRequest


@pytest.fixture
def real_db():
    db = SessionLocal()
    yield db
    db.close()


def test_popular_homepage_searches_return_both_branded_and_generic(real_db):
    """
    Every popular search term on the home screen must return results and
    present verified generic Jan Aushadhi alternatives with authentic savings.
    """
    popular_branded_queries = [
        "Dolo 650",
        "Augmentin 625 Duo",
        "Glycomet 500 SR",
        "Pan 40",
        "Amlopres 5",
        "Atorva 10",
    ]
    for q in popular_branded_queries:
        res = MedicineSearchService.search_medicines(real_db, query=q, limit=5, offset=0, jan_aushadhi_only=False)
        assert len(res.items) > 0, f"Search for {q} returned no results"

        branded = [p for p in res.items if not p.is_jan_aushadhi]
        generic = [p for p in res.items if p.is_jan_aushadhi]

        assert len(branded) > 0, f"Search for {q} did not return the branded reference medicine"
        assert len(generic) > 0, f"Search for {q} did not return the Jan Aushadhi generic equivalent"

        b_price = branded[0].latest_price.amount_inr if branded[0].latest_price else None
        g_price = generic[0].latest_price.amount_inr if generic[0].latest_price else None

        assert b_price is not None and b_price > 0, f"Branded medicine {branded[0].brand_name} has invalid price: {b_price}"
        assert g_price is not None and g_price > 0, f"Generic medicine {generic[0].brand_name} has invalid price: {g_price}"
        assert g_price < b_price, f"Generic price {g_price} is not cheaper than branded {b_price} for query {q}"


def test_price_comparison_savings_mathematically_sound(real_db):
    """
    Comparing Augmentin 625 Duo against its Jan Aushadhi equivalent must yield > 65% savings.
    """
    req = PriceComparisonRequest(product_ids=[18, 2576], reference_product_id=18)
    res = PriceComparisonService.compare_prices(real_db, req=req)
    assert res.max_savings_percentage is not None
    assert res.max_savings_percentage >= 70.0, f"Expected >= 70% savings, got {res.max_savings_percentage}"
    assert len(res.comparisons) == 1
    comp = res.comparisons[0]
    assert comp.is_comparable is True
    assert comp.pack_savings_inr > 100.0


def test_chat_emergency_distress_protocol(client):
    """
    Statutory safety test: acute distress queries must be routed to statutory Indian emergency lines.
    """
    res = client.post("/api/v1/chat", json={"message": "I have severe crushing chest pain"})
    assert res.status_code == 200
    data = res.json()
    resp_text = data.get("answer", "")
    assert "EMERGENCY DETECTED" in resp_text
    assert "112" in resp_text
    assert data["extracted_entities"]["intent"] == "emergency"


def test_api_robustness_against_malformed_queries(client):
    """
    Edge case handling: special characters, SQL injection attempts, high offsets.
    """
    # SQL injection attempt
    res = client.get("/api/v1/medicines/search?q=' OR 1=1 --")
    assert res.status_code == 200

    # Punctuation spam
    res = client.get("/api/v1/medicines/search?q=@@@###$$$%%%")
    assert res.status_code == 200
    assert len(res.json()["items"]) == 0

    # High offset past dataset
    res = client.get("/api/v1/medicines/search?q=Paracetamol&offset=10000")
    assert res.status_code == 200
    assert len(res.json()["items"]) == 0
