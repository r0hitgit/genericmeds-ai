def test_search_exact_match(client):
    response = client.get("/api/v1/medicines/search?q=Dolo 650")
    assert response.status_code == 200
    data = response.json()
    assert data["match_type"] == "exact"
    assert data["total"] >= 1
    assert data["items"][0]["brand_name"] == "Dolo 650"
    assert data["items"][0]["dosage_form"] == "Tablet"
    assert len(data["items"][0]["ingredients"]) == 1
    assert data["items"][0]["ingredients"][0]["name"] == "Paracetamol"
    assert data["items"][0]["ingredients"][0]["strength_value"] == 650.0


def test_search_partial_by_ingredient(client):
    response = client.get("/api/v1/medicines/search?q=Paracetamol")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    brand_names = [item["brand_name"] for item in data["items"]]
    assert "Dolo 650" in brand_names
    assert "Calpol 500" in brand_names


def test_search_jan_aushadhi_only(client):
    response = client.get("/api/v1/medicines/search?q=Paracetamol&jan_aushadhi_only=true")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["is_jan_aushadhi"] is True


def test_search_unknown_brand(client):
    response = client.get("/api/v1/medicines/search?q=NonExistentPharma12345")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_get_medicine_detail_with_source_metadata(client):
    # Medicine ID 1 is Dolo 650
    response = client.get("/api/v1/medicines/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["brand_name"] == "Dolo 650"
    assert data["source"] is not None
    assert "Verified Branded Market Retail" in data["source"]["source_name"]
    assert len(data["price_history"]) >= 1
    assert data["price_history"][0]["amount_inr"] == 30.0
    assert data["price_history"][0]["verification_status"] == "verified"


def test_get_medicine_detail_not_found(client):
    response = client.get("/api/v1/medicines/999999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_search_folvite_and_omee_500_token_fallback(client):
    # Folvite brand search
    res_folvite = client.get("/api/v1/medicines/search?q=folvite")
    assert res_folvite.status_code == 200
    data_f = res_folvite.json()
    assert data_f["total"] >= 1
    assert any("folvite" in m["brand_name"].lower() for m in data_f["items"])

    # Omee 500 query with token fallback matching Omee
    res_omee = client.get("/api/v1/medicines/search?q=omee%20500")
    assert res_omee.status_code == 200
    data_o = res_omee.json()
    assert data_o["total"] >= 1
    assert any("omee" in m["brand_name"].lower() for m in data_o["items"])


def test_chat_folvite_and_omee_500_answers(client):
    # Folvite chat
    res_f = client.post("/api/v1/chat", json={"message": "folvite"})
    assert res_f.status_code == 200
    ans_f = res_f.json()["answer"]
    assert "Folvite" in ans_f
    assert "Jan Aushadhi Folic Acid" in ans_f

    # Omee 500 chat
    res_o = client.post("/api/v1/chat", json={"message": "omee 500"})
    assert res_o.status_code == 200
    ans_o = res_o.json()["answer"]
    assert "Omee" in ans_o
    assert "Omeprazole" in ans_o
    assert "Jan Aushadhi Omeprazole" in ans_o
    assert "20mg" in ans_o

