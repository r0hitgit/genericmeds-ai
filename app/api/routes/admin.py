import io
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd
from app.core.database import get_db
from app.core.security import verify_admin_key
from app.schemas.source import AdminImportReport
from app.services.data_ingestion import DataIngestionService

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Operations"])


@router.post(
    "/import-medicines",
    response_model=AdminImportReport,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_admin_key)],
)
async def import_medicine_catalog(
    file: UploadFile = File(..., description="CSV or Excel file containing medicine catalogue"),
    source_name: str = Form("PMBI Jan Aushadhi (PMBJP)", description="Official source identifier"),
    source_url: str = Form("https://www.pmbi.co.in/ProductList.aspx", description="Official portal link"),
    db: Session = Depends(get_db),
):
    """
    Import a validated CSV or Excel medicine catalogue.
    Requires administrator authentication ('X-Admin-Key' header).
    Records import date, source, validation results, and errors.
    Prevents silent overwriting of trusted data.
    """
    filename = (file.filename or "").lower()
    contents = await file.read()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload a .csv or .xlsx file.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)}",
        )

    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file contains no data rows.",
        )

    report = DataIngestionService.ingest_catalog_dataframe(
        db=db,
        df=df,
        source_name=source_name,
        source_url=source_url,
    )
    return report
