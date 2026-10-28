from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.medicine import AlternativeSearchRequest, AlternativeSearchResponse
from app.services.alternatives import AlternativeMatchingService

router = APIRouter(prefix="/api/v1/alternatives", tags=["Alternatives"])


@router.post("/search", response_model=AlternativeSearchResponse, status_code=status.HTTP_200_OK)
def search_alternatives(
    req: AlternativeSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Search for verified generic alternatives and equivalent formulations.
    Requires exact active ingredient match, identical strengths, matching dosage forms,
    and release profiles before classifying as 'EXACT_COMPOSITION_MATCH'.
    """
    return AlternativeMatchingService.match_alternatives(db=db, req=req)
