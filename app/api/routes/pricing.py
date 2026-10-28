from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.pricing import PriceComparisonRequest, PriceComparisonResponse
from app.services.price_comparison import PriceComparisonService

router = APIRouter(prefix="/api/v1/prices", tags=["Price Comparison"])


@router.post("/compare", response_model=PriceComparisonResponse, status_code=status.HTTP_200_OK)
def compare_prices(
    req: PriceComparisonRequest,
    db: Session = Depends(get_db),
):
    """
    Compare two or more specified catalogue products.
    Calculates comparable unit prices, package-price differences, and potential savings.
    Rejects or clearly flags comparisons involving incompatible strengths, formulations,
    package sizes, or unverified prices.
    """
    return PriceComparisonService.compare_prices(db=db, req=req)
