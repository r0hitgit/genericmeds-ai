from app.services.safety_validation import SafetyValidationService


def test_emergency_detection():
    queries = [
        "I am having severe chest pain and left arm numbness",
        "My child had an accidental overdose of medicine",
        "The patient cannot breathe and throat is closing up",
    ]
    for q in queries:
        is_em, msg = SafetyValidationService.check_emergency(q)
        assert is_em is True
        assert "112" in msg or "108" in msg
        assert "EMERGENCY DETECTED" in msg


def test_emergency_in_chat_endpoint(client):
    response = client.post("/api/v1/chat", json={"message": "I have severe crushing chest pain"})
    assert response.status_code == 200
    data = response.json()
    assert "EMERGENCY DETECTED" in data["answer"]
    assert "112" in data["answer"]
    assert data["extracted_entities"]["intent"] == "emergency"


def test_unsafe_prescription_intent_detection():
    queries = [
        "Can I take 1000mg instead of 500mg?",
        "Should I stop taking my prescription medicine?",
        "Prescribe me an antibiotic for my fever",
    ]
    for q in queries:
        is_unsafe, msg = SafetyValidationService.check_unsafe_intent(q)
        assert is_unsafe is True
        assert "cannot prescribe" in msg.lower() or "caution" in msg.lower()


def test_high_risk_medicine_flagging(client):
    # ID 10 is Warf 5 (Warfarin - anticoagulant)
    resp_warf = client.get("/api/v1/medicines/10")
    assert resp_warf.status_code == 200
    data_warf = resp_warf.json()
    assert data_warf["high_risk_flag"] is True
    assert any("Warfarin" in r for r in data_warf["high_risk_reasons"])

    # ID 11 is Mixtard 30/70 (Insulin - injectable)
    resp_ins = client.get("/api/v1/medicines/11")
    assert resp_ins.status_code == 200
    data_ins = resp_ins.json()
    assert data_ins["high_risk_flag"] is True
    assert any("Insulin" in r for r in data_ins["high_risk_reasons"])
    assert any("Injectable" in r for r in data_ins["high_risk_reasons"])


def test_mandatory_disclaimer_present(client):
    response = client.get("/api/v1/medicines/1")
    assert response.status_code == 200

    chat_resp = client.post("/api/v1/chat", json={"message": "Tell me about Dolo 650"})
    assert chat_resp.status_code == 200
    assert "This tool provides medicine information and price comparisons, not medical advice" in chat_resp.json()["disclaimer"]
