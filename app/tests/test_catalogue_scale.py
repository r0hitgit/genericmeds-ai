import os
import pytest
from fastapi.testclient import TestClient
from app.services.catalogue_import import CatalogueImportService
from app.models.medicine import MedicineProduct
from app.models.pricing import MedicinePrice
from app.models.brand_lookup import BrandGenericLookup
from app.models.alias import MedicineAlias

FILE_A = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/imports/pmbjp_janaushadhi_medicine_database.csv"))
FILE_B = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/imports/pmbjp_popular_indian_brands_to_generic.csv"))


def test_catalogue_preview_direct():
    """Verify preview logic directly on actual CSV files."""
    report = CatalogueImportService.preview_import(FILE_A, FILE_B)
    assert report.file_a_rows == 2439
    assert report.file_a_priced_count == 2052
    assert report.file_a_unpriced_count == 387
    assert report.file_b_rows == 172
    assert report.matched_primary_codes_count == 170
    assert sorted(report.unmatched_primary_codes) == ["PMBI-1126", "PMBI-292"]
    assert report.duplicate_codes == []
    assert report.savings_audit_matches == 172
    assert len(report.savings_audit_discrepancies) == 0


def test_catalogue_preview_endpoint_auth(client: TestClient):
    """Test that preview endpoint enforces admin authentication."""
    # No auth header -> 401
    resp = client.post("/api/v1/admin/catalogue/import/preview")
    assert resp.status_code == 401

    # Invalid auth header -> 403
    resp = client.post(
        "/api/v1/admin/catalogue/import/preview",
        headers={"X-Admin-Key": "wrong-key"},
    )
    assert resp.status_code == 403

    # Valid auth header -> 200
    resp = client.post(
        "/api/v1/admin/catalogue/import/preview",
        headers={"X-Admin-Key": "test-admin-secret-key"},
        data={"file_a_path": FILE_A, "file_b_path": FILE_B},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["file_a_rows"] == 2439
    assert data["file_a_priced_count"] == 2052
    assert data["file_a_unpriced_count"] == 387
    assert data["file_b_rows"] == 172
    assert data["matched_primary_codes_count"] == 170
    assert "PMBI-292" in data["unmatched_primary_codes"]
    assert "PMBI-1126" in data["unmatched_primary_codes"]


def test_catalogue_import_endpoint_dry_run(client: TestClient):
    """Test dry run import via endpoint."""
    resp = client.post(
        "/api/v1/admin/catalogue/import",
        headers={"X-Admin-Key": "test-admin-secret-key"},
        data={"is_dry_run": "true", "file_a_path": FILE_A, "file_b_path": FILE_B},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "dry_run_success"
    assert data["is_dry_run"] is True
    assert data["products_processed"] == 2439
    assert data["brand_lookups_processed"] == 172


def test_catalogue_full_ingestion_and_idempotency(db_session):
    """Test full ingestion and verify idempotency and database constraints."""
    # Run first import
    report1 = CatalogueImportService.import_catalogue(
        db=db_session,
        file_a_path=FILE_A,
        file_b_path=FILE_B,
        is_dry_run=False,
    )
    assert report1.status == "import_success"
    assert report1.products_processed == 2439
    assert report1.products_created == 2439
    assert report1.brand_lookups_processed == 172
    assert report1.brand_lookups_linked == 170
    assert report1.brand_lookups_unresolved == 2

    # Verify unpriced products have SQL NULL in prices, never 0
    unpriced_prods = db_session.query(MedicineProduct).filter(
        MedicineProduct.pricing_status.like("%Under Rate%")
    ).all()
    assert len(unpriced_prods) == 387
    for p in unpriced_prods[:10]:
        price = db_session.query(MedicinePrice).filter(MedicinePrice.product_id == p.id).first()
        assert price is not None
        assert price.amount_inr is None
        assert price.verification_status == "under_process"

    # Verify priced products have non-zero MRP
    priced_prods = db_session.query(MedicineProduct).filter(
        MedicineProduct.pricing_status.like("%Active Priced%")
    ).all()
    assert len(priced_prods) == 2052
    for p in priced_prods[:10]:
        price = db_session.query(MedicinePrice).filter(MedicinePrice.product_id == p.id).first()
        assert price is not None
        assert price.amount_inr is not None
        assert price.amount_inr > 0

    # Verify unmatched codes in brand lookup table
    unmatched_lookups = db_session.query(BrandGenericLookup).filter(
        BrandGenericLookup.reconciliation_status == "UNRESOLVED_CODE"
    ).all()
    assert len(unmatched_lookups) == 2
    unmatched_codes = {b.primary_pmbi_drug_code for b in unmatched_lookups}
    assert unmatched_codes == {"PMBI-292", "PMBI-1126"}
    for b in unmatched_lookups:
        assert b.linked_product_id is None

    # Run second import (idempotency check)
    report2 = CatalogueImportService.import_catalogue(
        db=db_session,
        file_a_path=FILE_A,
        file_b_path=FILE_B,
        is_dry_run=False,
    )
    assert report2.status == "import_success"
    assert report2.products_created == 0
    assert report2.products_updated == 2439
    assert report2.aliases_created == 0


def test_brand_search_endpoints(client: TestClient, db_session):
    """Test brand search and lookup by ID endpoints after importing data."""
    # Ingest data into the isolated test db
    CatalogueImportService.import_catalogue(
        db=db_session,
        file_a_path=FILE_A,
        file_b_path=FILE_B,
        is_dry_run=False,
    )

    # Search for Amlong
    resp = client.get("/api/v1/brands/search?q=Amlong")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    item = data["items"][0]
    assert "Amlong" in item["popular_brand_names"]
    assert item["primary_pmbi_drug_code"].startswith("PMBI-")
    assert item["indicative_savings_pct"] is not None
    assert item["linked_product"] is not None

    # Get specific brand lookup
    resp = client.get(f"/api/v1/brands/{item['brand_lookup_id']}")
    assert resp.status_code == 200
    single = resp.json()
    assert single["brand_lookup_id"] == item["brand_lookup_id"]
    assert single["active_generic_composition"] is not None

    # Test 404 for nonexistent brand lookup
    resp = client.get("/api/v1/brands/NONEXISTENT-999")
    assert resp.status_code == 404


def test_medicine_search_layered(client: TestClient, db_session):
    """Test layered search by exact drug code, brand alias, and generic name."""
    CatalogueImportService.import_catalogue(
        db=db_session,
        file_a_path=FILE_A,
        file_b_path=FILE_B,
        is_dry_run=False,
    )

    # Search by exact PMBI drug code
    resp = client.get("/api/v1/medicines/search?q=PMBI-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert data["items"][0]["pmbi_code"] == "PMBI-1"

    # Search by brand alias from File A (e.g. Zerodol-P)
    resp = client.get("/api/v1/medicines/search?q=Zerodol-P")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    # Check that PMBI-1 (Aceclofenac + Paracetamol) is returned
    codes = [item["pmbi_code"] for item in data["items"]]
    assert "PMBI-1" in codes


def test_catalogue_status_endpoint(client: TestClient, db_session):
    """Test public status report endpoint."""
    CatalogueImportService.import_catalogue(
        db=db_session,
        file_a_path=FILE_A,
        file_b_path=FILE_B,
        is_dry_run=False,
    )

    resp = client.get("/api/v1/catalogue/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["active_priced_products"] == 2052
    assert data["under_process_unpriced_products"] == 387
    assert data["total_brand_lookups"] == 172
    assert data["linked_brand_lookups"] == 170
    assert data["unresolved_brand_lookups"] == 2
    assert "PMBI-292" in data["unresolved_codes_flagged"]
    assert "PMBI-1126" in data["unresolved_codes_flagged"]


def test_ai_chat_with_brand_rag(client: TestClient, db_session):
    """Test AI assistant chat RAG retrieving popular brand lookup information."""
    CatalogueImportService.import_catalogue(
        db=db_session,
        file_a_path=FILE_A,
        file_b_path=FILE_B,
        is_dry_run=False,
    )

    payload = {
        "message": "What is the generic alternative to Amlong?",
        "language": "en",
    }
    resp = client.post("/api/v1/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "Amlong" in data["answer"] or "Amlodipine" in data["answer"]
    assert "PMBJP" in data["answer"] or "Jan Aushadhi" in data["answer"]
    assert "disclaimer" in data and len(data["disclaimer"]) > 0
