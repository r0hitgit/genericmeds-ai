from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.brand_lookup import BrandSearchResponse, BrandGenericLookupOut
from app.services.brand_search import BrandSearchService

router = APIRouter(prefix="/api/v1/brands", tags=["Brand Lookups"])


@router.get("/search", response_model=BrandSearchResponse)
def search_brands(
    q: str = Query(..., min_length=1, max_length=200, description="Brand name, alias, manufacturer, or generic active composition"),
    limit: int = Query(20, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """
    Search popular Indian brand medicines and their verified Jan Aushadhi generic equivalents.
    Displays indicative market prices, Jan Aushadhi MRPs, indicative savings, and dispensing rules.
    """
    return BrandSearchService.search_brands(
        db=db,
        query=q,
        limit=limit,
        offset=offset,
    )


@router.get("/{brand_lookup_id}", response_model=BrandGenericLookupOut)
def get_brand_lookup(
    brand_lookup_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve full details for a specific brand lookup record (e.g. 'BRD-001') including
    reconciliation status and linked Jan Aushadhi medicine product.
    """
    lookup = BrandSearchService.get_brand_by_id(db=db, brand_lookup_id=brand_lookup_id)
    if not lookup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand lookup record '{brand_lookup_id}' not found.",
        )
    return lookup
