from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.source import DataSourceOut
from app.services.source_verification import SourceVerificationService

router = APIRouter(prefix="/api/v1/sources", tags=["Data Sources"])


@router.get("", response_model=List[DataSourceOut], status_code=status.HTTP_200_OK)
def list_data_sources(db: Session = Depends(get_db)):
    """
    List supported sources (PMBI Jan Aushadhi, NPPA Pharma Sahi Daam, CDSCO),
    source URLs, last synchronization dates, and data freshness status.
    """
    return SourceVerificationService.list_sources(db=db)
