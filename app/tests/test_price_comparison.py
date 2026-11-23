def test_price_comparison_exact_equivalent(client):
    # Compare Dolo 650 (ID 1) with Jan Aushadhi Paracetamol 650 (ID 2)
    payload = {
        "product_ids": [1, 2],
        "reference_product_id": 1
    }
    response = client.post("/api/v1/prices/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert len(data["comparisons"]) == 1

    comp = data["comparisons"][0]
    assert comp["is_comparable"] is True
    assert comp["compared_brand_name"] == "Jan Aushadhi Paracetamol 650"
    assert comp["reference_brand_name"] == "Dolo 650"
    assert comp["reference_unit_price_inr"] == 2.0
    assert comp["alternative_unit_price_inr"] == 1.0
    assert comp["unit_savings_inr"] == 1.0
    assert comp["savings_percentage"] == 50.0


def test_price_comparison_incompatible_strength_rejected(client):
    # Compare Dolo 650 (ID 1, 650mg) with Calpol 500 (ID 3, 500mg)
    payload = {
        "product_ids": [1, 3],
        "reference_product_id": 1
    }
    response = client.post("/api/v1/prices/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    comp = data["comparisons"][0]
    assert comp["is_comparable"] is False
    assert any("Different strength" in reason for reason in comp["incomparability_reasons"])
    assert comp["savings_percentage"] is None


def test_stale_pricing_record_flagged(client):
    # Product ID 9 has price verified 120 days ago (> 90 days)
    payload = {
        "product_ids": [1, 9],
        "reference_product_id": 1
    }
    response = client.post("/api/v1/prices/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    stale_item = next(item for item in data["items"] if item["product_id"] == 9)
    assert stale_item["is_price_verified"] is False
    assert "outdated" in stale_item["verification_status"].lower()


def test_missing_price_flagged(client):
    # Product ID 4 (Syrup) has no price record
    payload = {
        "product_ids": [1, 4],
        "reference_product_id": 1
    }
    response = client.post("/api/v1/prices/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    syrup_item = next(item for item in data["items"] if item["product_id"] == 4)
    assert syrup_item["listed_price_inr"] is None
    assert syrup_item["is_price_verified"] is False
    assert "price not verified" in syrup_item["verification_status"].lower()


def test_price_comparison_requires_at_least_two_products(client):
    payload = {"product_ids": [1]}
    response = client.post("/api/v1/prices/compare", json=payload)
    # Validation error from pydantic min_length=2
    assert response.status_code == 422


def test_jan_aushadhi_generic_prefers_government_listed_price(client, db_session):
    # Ensure that even if a retailer_price exists, Jan Aushadhi product (ID 2) strictly prefers government_listed_price
    from app.models.medicine import MedicineProduct
    from app.models.pricing import MedicinePrice
    from datetime import datetime, timezone

    p2 = db_session.query(MedicineProduct).filter(MedicineProduct.id == 2).first()
    # Add a newer retailer_price
    db_session.add(MedicinePrice(
        product_id=p2.id,
        amount_inr=30.0,
        price_type="retailer_price",
        pack_quantity=10.0,
        unit_of_measure="tablets",
        source_id=1,
        verified_at=datetime.now(timezone.utc),
        verification_status="verified",
    ))
    db_session.commit()

    # latest_verified_price must still return the government_listed_price (10.0), not retailer_price (30.0)
    assert p2.latest_verified_price.price_type == "government_listed_price"
    assert p2.latest_verified_price.amount_inr == 10.0

    payload = {
        "product_ids": [1, 2],
        "reference_product_id": 1,
    }
    response = client.post("/api/v1/prices/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2

    jan_item = next(i for i in data["items"] if i["product_id"] == 2)
    assert jan_item["listed_price_inr"] == 10.0
    assert jan_item["price_type"] == "government_listed_price"
    assert data["max_savings_percentage"] == 50.0

