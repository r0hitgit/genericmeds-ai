import os
import shutil
import tempfile
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_admin_key
from app.schemas.catalogue import (
    CataloguePreviewReport,
    CatalogueImportReport,
    CatalogueStatusReport,
)
from app.services.catalogue_import import CatalogueImportService

router = APIRouter(tags=["Catalogue Management"])

DEFAULT_FILE_A = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/imports/pmbjp_janaushadhi_medicine_database.csv"))
DEFAULT_FILE_B = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/imports/pmbjp_popular_indian_brands_to_generic.csv"))


def _resolve_import_files(
    file_a: Optional[UploadFile],
    file_b: Optional[UploadFile],
    file_a_path: Optional[str],
    file_b_path: Optional[str],
) -> tuple[str, str, list[str]]:
    temp_files = []

    # Resolve File A
    if file_a and file_a.filename:
        tmp_a = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        shutil.copyfileobj(file_a.file, tmp_a)
        tmp_a.close()
        temp_files.append(tmp_a.name)
        resolved_a = tmp_a.name
    elif file_a_path and os.path.exists(file_a_path):
        resolved_a = file_a_path
    elif os.path.exists(DEFAULT_FILE_A):
        resolved_a = DEFAULT_FILE_A
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Master medicine database file (File A) not found. Checked default: {DEFAULT_FILE_A}",
        )

    # Resolve File B
    if file_b and file_b.filename:
        tmp_b = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        shutil.copyfileobj(file_b.file, tmp_b)
        tmp_b.close()
        temp_files.append(tmp_b.name)
        resolved_b = tmp_b.name
    elif file_b_path and os.path.exists(file_b_path):
        resolved_b = file_b_path
    elif os.path.exists(DEFAULT_FILE_B):
        resolved_b = DEFAULT_FILE_B
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Popular brands lookup file (File B) not found. Checked default: {DEFAULT_FILE_B}",
        )

    return resolved_a, resolved_b, temp_files


@router.post(
    "/api/v1/admin/catalogue/import/preview",
    response_model=CataloguePreviewReport,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_admin_key)],
)
async def preview_catalogue_import(
    file_a: Optional[UploadFile] = File(None, description="Optional upload of master medicine database CSV"),
    file_b: Optional[UploadFile] = File(None, description="Optional upload of brand lookup CSV"),
    file_a_path: Optional[str] = Form(None, description="Filesystem path to File A"),
    file_b_path: Optional[str] = Form(None, description="Filesystem path to File B"),
):
    """
    Dry-run validation preview for the PMBJP Jan Aushadhi master catalogue and brand lookup datasets.
    Audits indicative savings, checks code reconciliations, flags unresolved codes, and preserves SQL NULL for unpriced items.
    Requires administrator authentication ('X-Admin-Key' header).
    """
    resolved_a, resolved_b, temp_files = _resolve_import_files(file_a, file_b, file_a_path, file_b_path)
    try:
        report = CatalogueImportService.preview_import(resolved_a, resolved_b)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to generate catalogue preview: {str(e)}",
        )
    finally:
        for tmp in temp_files:
            if os.path.exists(tmp):
                os.remove(tmp)


@router.post(
    "/api/v1/admin/catalogue/import",
    response_model=CatalogueImportReport,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_admin_key)],
)
async def import_catalogue(
    is_dry_run: bool = Form(False, description="Simulate import without committing database changes"),
    file_a: Optional[UploadFile] = File(None, description="Optional upload of master medicine database CSV"),
    file_b: Optional[UploadFile] = File(None, description="Optional upload of brand lookup CSV"),
    file_a_path: Optional[str] = Form(None, description="Filesystem path to File A"),
    file_b_path: Optional[str] = Form(None, description="Filesystem path to File B"),
    db: Session = Depends(get_db),
):
    """
    Idempotent transactional ingestion of PMBJP Jan Aushadhi master catalogue and brand lookup datasets.
    - File A: 2,439 rows (2,052 active priced, 387 unpriced preserved with SQL NULL MRP).
    - File B: 172 rows (170 linked by primary PMBI code, 2 flagged for administrative review).
    Requires administrator authentication ('X-Admin-Key' header).
    """
    resolved_a, resolved_b, temp_files = _resolve_import_files(file_a, file_b, file_a_path, file_b_path)
    try:
        report = CatalogueImportService.import_catalogue(
            db=db,
            file_a_path=resolved_a,
            file_b_path=resolved_b,
            is_dry_run=is_dry_run,
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to import catalogue: {str(e)}",
        )
    finally:
        for tmp in temp_files:
            if os.path.exists(tmp):
                os.remove(tmp)


@router.get(
    "/api/v1/catalogue/status",
    response_model=CatalogueStatusReport,
    status_code=status.HTTP_200_OK,
)
def get_catalogue_status(db: Session = Depends(get_db)):
    """
    Public data freshness, verification status, and quality report for the medicine knowledge base.
    """
    return CatalogueImportService.get_catalogue_status(db)
