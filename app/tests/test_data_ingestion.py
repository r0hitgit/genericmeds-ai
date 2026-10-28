import io
import pandas as pd
from app.services.data_ingestion import DataIngestionService


def test_malformed_csv_validation_errors(db_session):
    # Dataframe with malformed values
    bad_data = {
        "brand_name": ["", "Valid Med", "Negative Price Med"],
        "generic_name": ["Generic 1", "", "Paracetamol 500mg"],
        "dosage_form": ["Tablet", "Tablet", "Tablet"],
        "pack_size": [-5, 10, 10],  # row 1 has negative pack size
        "price_inr": [10.0, 20.0, -50.0],  # row 3 has negative price
        "composition": ["Paracetamol 500mg", "Paracetamol 500mg", "Paracetamol 500mg"],
    }
    df = pd.DataFrame(bad_data)
    report = DataIngestionService.ingest_catalog_dataframe(
        db=db_session,
        df=df,
        source_name="Test Source",
    )
    assert len(report.validation_errors) >= 2
    assert any("Missing brand" in err for err in report.validation_errors)
    assert any("Price must be positive" in err or "Malformed price" in err for err in report.validation_errors)


def test_admin_import_endpoint_auth_required(client):
    csv_content = b"brand_name,generic_name,dosage_form,pack_size,price_inr,composition\nTestBrand,TestGeneric,Tablet,10,25.0,Paracetamol 500mg\n"

    # 1. No key -> 401
    resp_no_auth = client.post(
        "/api/v1/admin/import-medicines",
        files={"file": ("test.csv", csv_content, "text/csv")},
    )
    assert resp_no_auth.status_code == 401

    # 2. Wrong key -> 403
    resp_bad_auth = client.post(
        "/api/v1/admin/import-medicines",
        files={"file": ("test.csv", csv_content, "text/csv")},
        headers={"X-Admin-Key": "wrong-secret"},
    )
    assert resp_bad_auth.status_code == 403

    # 3. Valid key -> 200
    resp_valid = client.post(
        "/api/v1/admin/import-medicines",
        files={"file": ("test.csv", csv_content, "text/csv")},
        headers={"X-Admin-Key": "test-admin-secret-key"},
    )
    assert resp_valid.status_code == 200
    report = resp_valid.json()
    assert report["records_processed"] == 1
    assert report["records_created"] == 1
    assert report["status"] == "success"
