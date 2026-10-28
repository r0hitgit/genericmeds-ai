def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "GenericMeds AI"
    assert data["database"] == "healthy"
    assert data["ready"] is True
