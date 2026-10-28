import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.kendra_distance import (
    haversine_distance,
    validate_coordinates,
    validate_pincode,
    generate_directions_url,
)
from app.services.kendra_verification import KendraVerificationService

client = TestClient(app)


# 1. Haversine Distance & Coordinates Tests
def test_haversine_exact_calculation():
    # Identical coordinates
    assert haversine_distance(28.5672, 77.2100, 28.5672, 77.2100) == 0.0

    # Delhi AIIMS (28.5672, 77.2100) to Safdarjung (28.5694, 77.2067) ~ 0.4 km
    dist = haversine_distance(28.5672, 77.2100, 28.5694, 77.2067)
    assert 0.3 <= dist <= 0.6

    # Delhi to Mumbai ~ 1,140 to 1,160 km
    delhi_mumbai = haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
    assert 1140 <= delhi_mumbai <= 1160


def test_coordinate_validation():
    # Valid
    ok, err = validate_coordinates(28.5, 77.2)
    assert ok is True
    assert err is None

    # Invalid latitude
    ok, err = validate_coordinates(95.0, 77.0)
    assert ok is False
    assert "Latitude" in err

    # Invalid longitude
    ok, err = validate_coordinates(28.0, 190.0)
    assert ok is False
    assert "Longitude" in err

    # Null coordinates
    ok, err = validate_coordinates(None, 77.0)
    assert ok is False


def test_pincode_validation():
    # Valid 6-digit Indian PIN
    ok, val = validate_pincode("110029")
    assert ok is True
    assert val == "110029"

    # Invalid: 5 digits
    ok, err = validate_pincode("11002")
    assert ok is False

    # Invalid: starts with 0
    ok, err = validate_pincode("010029")
    assert ok is False

    # Invalid: non-numeric
    ok, err = validate_pincode("11002A")
    assert ok is False


def test_directions_url_generation():
    # Google Maps coordinate URL
    url_g = generate_directions_url(28.5672, 77.2100, "AIIMS New Delhi", provider="google")
    assert "https://www.google.com/maps/dir/?api=1&destination=28.567200,77.210000" == url_g

    # OpenStreetMap URL
    url_osm = generate_directions_url(28.5672, 77.2100, provider="osm")
    assert "https://www.openstreetmap.org/directions" in url_osm

    # Fallback to address when coordinates missing
    url_addr = generate_directions_url(None, None, "Ansari Nagar New Delhi")
    assert "https://www.google.com/maps/dir/?api=1&destination=Ansari%20Nagar%20New%20Delhi" == url_addr


# 2. Nearby Search Endpoint Tests
def test_nearby_search_valid_coordinates():
    # AIIMS Delhi coordinates
    res = client.get("/api/v1/kendras/nearby?lat=28.5672&lon=77.2100&radius_km=10")
    assert res.status_code == 200
    data = res.json()

    assert data["user_latitude"] == 28.5672
    assert data["user_longitude"] == 77.2100
    assert data["radius_km"] == 10.0
    assert data["total_found"] >= 2
    assert len(data["kendras"]) >= 2

    # Verify sorting from nearest to farthest
    distances = [k["distance_km"] for k in data["kendras"] if k["distance_km"] is not None]
    assert distances == sorted(distances)

    first = data["kendras"][0]
    assert first["distance_km"] <= 1.0  # Should be AIIMS or Safdarjung
    assert first["stock_status"] == "Medicine stock not confirmed"
    assert first["directions_url"] is not None


def test_nearby_search_radius_filter():
    # Tight radius 1 km around AIIMS Delhi
    res_tight = client.get("/api/v1/kendras/nearby?lat=28.5672&lon=77.2100&radius_km=1")
    assert res_tight.status_code == 200
    tight_data = res_tight.json()

    # Wide radius 25 km around AIIMS Delhi
    res_wide = client.get("/api/v1/kendras/nearby?lat=28.5672&lon=77.2100&radius_km=25")
    assert res_wide.status_code == 200
    wide_data = res_wide.json()

    assert wide_data["total_found"] >= tight_data["total_found"]


def test_nearby_search_no_results_suggests_wider_radius():
    # Middle of Arabian Sea (no Kendras)
    res = client.get("/api/v1/kendras/nearby?lat=15.0000&lon=65.0000&radius_km=5")
    assert res.status_code == 200
    data = res.json()

    assert data["total_found"] == 0
    assert len(data["kendras"]) == 0
    assert data["wider_radius_suggested"] is not None
    assert "janaushadhi.gov.in" in data["official_locator_url"]


def test_nearby_search_invalid_coordinates_rejected():
    # Latitude > 90
    res = client.get("/api/v1/kendras/nearby?lat=95.0&lon=77.0")
    assert res.status_code in (400, 422)

    # Longitude > 180
    res = client.get("/api/v1/kendras/nearby?lat=28.0&lon=200.0")
    assert res.status_code in (400, 422)


def test_nearby_search_invalid_radius_or_limit():
    # Invalid negative radius
    res = client.get("/api/v1/kendras/nearby?lat=28.0&lon=77.0&radius_km=-5")
    assert res.status_code == 422 or res.status_code == 400

    # Limit > 100
    res = client.get("/api/v1/kendras/nearby?lat=28.0&lon=77.0&limit=150")
    assert res.status_code == 422 or res.status_code == 400


# 3. Manual Search Endpoint Tests
def test_manual_search_by_pincode():
    res = client.get("/api/v1/kendras/search?pincode=110029")
    assert res.status_code == 200
    data = res.json()
    assert data["total_found"] >= 2
    for k in data["kendras"]:
        assert k["pincode"] == "110029"
        assert k["stock_status"] == "Medicine stock not confirmed"


def test_manual_search_by_state():
    res = client.get("/api/v1/kendras/search?state=Maharashtra")
    assert res.status_code == 200
    data = res.json()
    assert data["total_found"] >= 2
    for k in data["kendras"]:
        assert "Maharashtra" in k["state"]


def test_manual_search_by_district():
    res = client.get("/api/v1/kendras/search?district=Bengaluru")
    assert res.status_code == 200
    data = res.json()
    assert data["total_found"] >= 2
    for k in data["kendras"]:
        assert "Bengaluru" in k["district"] or "Bengaluru" in k["city"]


def test_manual_search_invalid_pincode():
    res = client.get("/api/v1/kendras/search?pincode=123")
    assert res.status_code == 400
    assert "Invalid PIN code" in res.json()["detail"]


# 4. Kendra Detail Endpoint Tests
def test_kendra_detail_by_id():
    res = client.get("/api/v1/kendras/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["kendra_name"] is not None
    assert data["address"] is not None
    assert data["stock_status"] == "Medicine stock not confirmed"
    assert "janaushadhi.gov.in" in data["source_url"]


def test_kendra_detail_not_found():
    res = client.get("/api/v1/kendras/999999")
    assert res.status_code == 404


# 5. Admin CSV Import Endpoint & Security
def test_admin_import_auth_required():
    csv_data = "official_kendra_code,kendra_name,address,city,district,state,pincode\nPMBJK-T1,Test,Address,City,Dist,Delhi,110001\n"
    # No header
    res_no = client.post("/api/v1/kendras/import", files={"file": ("test.csv", csv_data, "text/csv")})
    assert res_no.status_code == 401

    # Wrong header
    res_bad = client.post(
        "/api/v1/kendras/import",
        files={"file": ("test.csv", csv_data, "text/csv")},
        headers={"X-Admin-Key": "wrong-key"}
    )
    assert res_bad.status_code == 403


def test_admin_import_validation_and_deduplication():
    # Row 1: Valid
    # Row 2: Missing mandatory name
    # Row 3: Invalid PIN code
    # Row 4: Invalid coordinates
    csv_data = """official_kendra_code,kendra_name,address,city,district,state,pincode,latitude,longitude
PMBJK-UNIT-01,Unit Test Kendra 1,Main Road,New Delhi,Central Delhi,Delhi,110001,28.6139,77.2090
PMBJK-UNIT-02,,Missing Name Address,New Delhi,Central Delhi,Delhi,110001,28.6139,77.2090
PMBJK-UNIT-03,Unit Test Kendra 3,Main Road,New Delhi,Central Delhi,Delhi,000000,28.6139,77.2090
PMBJK-UNIT-04,Unit Test Kendra 4,Main Road,New Delhi,Central Delhi,Delhi,110001,999.0,77.2090
"""
    res = client.post(
        "/api/v1/kendras/import",
        files={"file": ("test.csv", csv_data, "text/csv")},
        headers={"X-Admin-Key": settings.ADMIN_API_KEY}
    )
    assert res.status_code == 200
    report = res.json()
    assert report["total_rows_processed"] == 4
    assert report["records_created"] == 1
    assert report["records_rejected"] == 3
    assert len(report["row_errors"]) == 3

    # Test De-duplication on re-import
    csv_reimport = """official_kendra_code,kendra_name,address,city,district,state,pincode,latitude,longitude
PMBJK-UNIT-01,Unit Test Kendra 1 Updated,Updated Address,New Delhi,Central Delhi,Delhi,110001,28.6139,77.2090
"""
    res_dup = client.post(
        "/api/v1/kendras/import",
        files={"file": ("test.csv", csv_reimport, "text/csv")},
        headers={"X-Admin-Key": settings.ADMIN_API_KEY}
    )
    assert res_dup.status_code == 200
    report_dup = res_dup.json()
    assert report_dup["records_created"] == 0
    assert report_dup["records_updated"] == 1

    # Cleanup test record
    from app.core.database import SessionLocal
    from app.models.kendra import JanAushadhiKendra
    db = SessionLocal()
    db.query(JanAushadhiKendra).filter(JanAushadhiKendra.official_kendra_code == "PMBJK-UNIT-01").delete()
    db.commit()
    db.close()


# 6. Safety & Scope Enforcement Tests
def test_mandatory_disclaimer_in_responses():
    disclaimer = KendraVerificationService.get_stock_disclaimer()
    assert "Kendra listings help you find nearby Jan Aushadhi stores" in disclaimer
    assert "not guarantee that a particular medicine is in stock" in disclaimer


def test_no_online_pharmacy_leakage():
    # Verify no online pharmacy / commercial ordering endpoints exist
    assert client.get("/api/v1/pharmacies").status_code == 404
    assert client.get("/api/v1/delivery").status_code == 404
    assert client.get("/api/v1/order").status_code == 404
    assert client.get("/api/v1/cart").status_code == 404

    # Verify no commercial pharmacy names in Kendra search response
    res = client.get("/api/v1/kendras?limit=50")
    assert res.status_code == 200
    content = str(res.json()).lower()
    for forbidden in ["1mg", "apollopharmacy", "pharmeasy", "netmeds", "truemeds"]:
        assert forbidden not in content


# 7. Greater Noida & Sector 151/Expressway GPS Discovery Tests
def test_nearby_search_greater_noida_expressway_corridor():
    # User coordinates near Sector 151 / Greater Noida entrance
    user_lat = 28.4550
    user_lon = 77.4950

    # Within 5 km
    res5 = client.get(f"/api/v1/kendras/nearby?lat={user_lat}&lon={user_lon}&radius_km=5.0")
    assert res5.status_code == 200
    data5 = res5.json()
    assert data5["total_found"] >= 5
    store_names = [k["kendra_name"] for k in data5["kendras"]]
    assert any("Alpha 1" in name or "ALPHA 1" in name for name in store_names)
    assert any("Omega 1" in name for name in store_names)
    assert any("Alpha 2" in name for name in store_names)

    # Within 10 km
    res10 = client.get(f"/api/v1/kendras/nearby?lat={user_lat}&lon={user_lon}&radius_km=10.0")
    assert res10.status_code == 200
    data10 = res10.json()
    assert data10["total_found"] >= 10
    assert data10["kendras"][0]["distance_km"] <= data10["kendras"][-1]["distance_km"]


def test_manual_search_greater_noida_sectors_and_pincodes():
    # PIN 201308 (Alpha 1, Alpha 2, Beta 1, Delta 1, Jagat Farm)
    res_pin = client.get("/api/v1/kendras/search?pincode=201308")
    assert res_pin.status_code == 200
    data_pin = res_pin.json()
    assert data_pin["total_found"] >= 5
    names = [k["kendra_name"] for k in data_pin["kendras"]]
    assert any("Alpha 2" in n for n in names)
    assert any("Alpha 1" in n or "ALPHA 1" in n for n in names)

    # City / District search
    res_dist = client.get("/api/v1/kendras/search?district=Greater+Noida")
    assert res_dist.status_code == 200
    assert res_dist.json()["total_found"] >= 10

