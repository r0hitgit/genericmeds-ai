from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.medicine import MedicineSearchResponse, MedicineProductDetail
from app.services.medicine_search import MedicineSearchService

router = APIRouter(prefix="/api/v1/medicines", tags=["Medicines"])


@router.get("/search", response_model=MedicineSearchResponse)
def search_medicines(
    q: str = Query(..., min_length=1, max_length=200, description="Search query: brand, generic name, or active ingredient"),
    limit: int = Query(20, ge=1, le=100, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    jan_aushadhi_only: bool = Query(False, description="Filter only Pradhan Mantri Jan Aushadhi products"),
    db: Session = Depends(get_db),
):
    """
    Search medicines by brand name, generic name, active ingredient, or drug code.
    Supports pagination and clearly distinguishes exact matches from partial matches.
    """
    return MedicineSearchService.search_medicines(
        db=db,
        query=q,
        limit=limit,
        offset=offset,
        jan_aushadhi_only=jan_aushadhi_only,
    )


@router.get("/{medicine_id}", response_model=MedicineProductDetail)
def get_medicine_detail(
    medicine_id: int,
    db: Session = Depends(get_db),
):
    """
    Returns the complete verified medicine record, active ingredients, dosage forms,
    source metadata, and historical price records.
    """
    detail = MedicineSearchService.get_medicine_by_id(db=db, medicine_id=medicine_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found in verified catalogue.",
        )
    return detail
