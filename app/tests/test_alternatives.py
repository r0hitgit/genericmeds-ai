def test_exact_ingredient_and_strength_matching(client):
    # Dolo 650 is Paracetamol 650mg Oral Tablet immediate-release
    payload = {"medicine_id": 1}
    response = client.post("/api/v1/alternatives/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["reference_product"]["brand_name"] == "Dolo 650"

    # Must find Jan Aushadhi Paracetamol 650 as EXACT_COMPOSITION_MATCH
    candidates = data["candidates"]
    exact_matches = [c for c in candidates if c["match_classification"] == "EXACT_COMPOSITION_MATCH"]
    assert len(exact_matches) >= 1
    assert exact_matches[0]["product"]["brand_name"] == "Jan Aushadhi Paracetamol 650"
    assert exact_matches[0]["product"]["is_jan_aushadhi"] is True

    # Unit price verification:
    # Dolo 650: ₹30 for 15 tablets = ₹2.00/tablet
    # Jan Aushadhi: ₹10 for 10 tablets = ₹1.00/tablet
    # Savings: ₹1.00/tablet (50% savings)
    assert exact_matches[0]["reference_unit_price"] == 2.0
    assert exact_matches[0]["alternative_unit_price"] == 1.0
    assert exact_matches[0]["unit_savings_inr"] == 1.0
    assert exact_matches[0]["savings_percentage"] == 50.0


def test_combination_products_matching(client):
    # Augmentin 625 Duo is Amoxicillin 500mg + Potassium Clavulanate 125mg
    payload = {"medicine_id": 5}
    response = client.post("/api/v1/alternatives/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["reference_product"]["brand_name"] == "Augmentin 625 Duo"

    exact_matches = [c for c in data["candidates"] if c["match_classification"] == "EXACT_COMPOSITION_MATCH"]
    assert len(exact_matches) >= 1
    match = exact_matches[0]
    assert match["product"]["brand_name"] == "Jan Aushadhi Amoxyclav 625"
    assert match["product"]["is_jan_aushadhi"] is True
    # Augmentin: ₹200 for 10 = ₹20/tab. Jan Aushadhi: ₹50 for 10 = ₹5/tab.
    assert match["reference_unit_price"] == 20.0
    assert match["alternative_unit_price"] == 5.0
    assert match["unit_savings_inr"] == 15.0
    assert match["savings_percentage"] == 75.0


def test_different_strength_rejected_as_equivalent(client):
    # Calpol 500 has Paracetamol 500mg, whereas Dolo 650 has 650mg
    payload = {"medicine_id": 1}
    response = client.post("/api/v1/alternatives/search", json=payload)
    assert response.status_code == 200
    data = response.json()

    calpol_candidate = next((c for c in data["candidates"] if c["product"]["brand_name"] == "Calpol 500"), None)
    assert calpol_candidate is not None
    assert calpol_candidate["match_classification"] == "DIFFERENT_STRENGTH"
    assert "not an equivalent dose" in calpol_candidate["match_notes"].lower()


def test_incompatible_dosage_form_rejected(client):
    # Search alternatives for Paracetamol 250mg syrup vs tablets
    payload = {
        "name": "Paracetamol",
        "dosage_form": "Syrup",
        "active_ingredients": [
            {"name": "Paracetamol", "strength_value": 250.0, "strength_unit": "mg"}
        ]
    }
    response = client.post("/api/v1/alternatives/search", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Tablets should not be marked as EXACT_COMPOSITION_MATCH for a Syrup
    for cand in data["candidates"]:
        if cand["product"]["dosage_form"] != "Syrup":
            assert cand["match_classification"] in ("DIFFERENT_FORMULATION", "INCOMPATIBLE")


def test_incompatible_release_types(client):
    # Glycomet 500 SR is sustained-release Metformin 500mg
    payload = {"medicine_id": 7}
    response = client.post("/api/v1/alternatives/search", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Immediate-release Metformin 500mg should NOT be an exact match
    ir_cand = next((c for c in data["candidates"] if c["product"]["brand_name"] == "Metformin 500 Plain"), None)
    if ir_cand:
        assert ir_cand["match_classification"] == "DIFFERENT_FORMULATION"
        assert "release profile" in ir_cand["match_notes"].lower()


def test_missing_formulation_details_returns_no_equivalence(client):
    # Empty query without valid ingredients or form
    payload = {}
    response = client.post("/api/v1/alternatives/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_candidates"] == 0
    assert "insufficient formulation details" in data["safety_notice"].lower()
