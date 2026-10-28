def test_chat_generic_discovery_english(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "What is the generic alternative to Dolo 650?", "language": "en"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Dolo 650" in data["answer"]
    assert "Jan Aushadhi Paracetamol 650" in data["answer"] or (
        data["structured_medicines"] and len(data["structured_medicines"]) > 0
    )
    assert data["disclaimer"] is not None


def test_chat_hindi_response(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "Dolo 650 का जेनेरिक विकल्प क्या है?", "language": "hi"}
    )
    assert response.status_code == 200
    data = response.json()
    # Should include Hindi text or guidance
    assert "सत्यापित" in data["answer"] or "विकल्प" in data["answer"] or "Dolo 650" in data["answer"]


def test_chat_ambiguous_query_prompts_clarification(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "tell me about this medicine please", "language": "en"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "specify the name" in data["answer"].lower() or "clarification" in data["answer"].lower()
    assert len(data["follow_up_questions"]) > 0


def test_sources_endpoint(client):
    response = client.get("/api/v1/sources")
    assert response.status_code == 200
    sources = response.json()
    assert len(sources) >= 2
    names = [s["source_name"] for s in sources]
    assert any("PMBI Jan Aushadhi" in n for n in names)
    assert any("NPPA" in n or "Market" in n for n in names)
