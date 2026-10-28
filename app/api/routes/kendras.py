from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.core.security import verify_admin_key
from app.models.kendra import JanAushadhiKendra
from app.models.guideline import MoleculeGuideline
from app.models.medicine import MedicineProduct
from app.models.pricing import MedicinePrice
from app.schemas.kendra import (
    JanAushadhiKendraOut,
    KendraNearbyResponse,
    KendraSearchResponse,
    KendraImportResponse,
    MoleculeGuidelineOut,
    TherapeuticGroupSummary,
)
from app.services.kendra_search import KendraSearchService
from app.services.kendra_import import KendraImportService
from app.services.pincode_service import lookup_pincode

router = APIRouter(prefix="/api/v1/kendras", tags=["Jan Aushadhi Kendras & Guidelines"])


@router.get("/lookup-pin", status_code=status.HTTP_200_OK)
def lookup_pincode_locality(
    pincode: str = Query(..., description="6-digit Indian PIN code to resolve locality, city, district, state"),
    db: Session = Depends(get_db),
):
    """
    Auto-detect district/city and state from a 6-digit Indian PIN code.
    Used for instant auto-completion in Jan Aushadhi Kendra search.
    """
    return lookup_pincode(pincode=pincode, db=db)


@router.get("/nearby", response_model=KendraNearbyResponse, status_code=status.HTTP_200_OK)
def get_nearby_kendras(
    lat: float = Query(..., ge=-90.0, le=90.0, description="User current latitude (-90 to +90)"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="User current longitude (-180 to +180)"),
    radius_km: float = Query(10.0, ge=1.0, le=200.0, description="Search radius in kilometers (5, 10, 25, 50 km)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of nearby results to return"),
    db: Session = Depends(get_db),
):
    """
    Find verified Pradhan Mantri Bhartiya Janaushadhi Kendras within a given radius
    from the user's current coordinates.
    Results are sorted from nearest to farthest using the Haversine formula.
    """
    try:
        return KendraSearchService.find_nearby_kendras(
            db=db,
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/search", response_model=KendraSearchResponse, status_code=status.HTTP_200_OK)
def search_kendras(
    state: Optional[str] = Query(None, description="Filter by Indian State (e.g. Maharashtra, Delhi, Karnataka)"),
    district: Optional[str] = Query(None, description="Filter by District or City (e.g. Mumbai, New Delhi, Bengaluru)"),
    pincode: Optional[str] = Query(None, description="Filter by exact 6-digit Indian PIN code (e.g. 110029, 400012)"),
    q: Optional[str] = Query(None, description="General search query (hospital name, landmark, address)"),
    limit: int = Query(20, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """
    Search Jan Aushadhi Kendras manually without GPS permission.
    Allows searching by State, District, PIN code, or hospital name keyword.
    """
    try:
        return KendraSearchService.search_kendras(
            db=db,
            state=state,
            district=district,
            pincode=pincode,
            q=q,
            limit=limit,
            offset=offset,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/import", response_model=KendraImportResponse, status_code=status.HTTP_200_OK)
async def import_kendras_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_auth: bool = Depends(verify_admin_key),
):
    """
    Admin-only endpoint to import verified Jan Aushadhi Kendra directory (CSV format).
    Validates mandatory attributes, PIN codes, coordinates, and reports row-level errors.
    Protected by X-Admin-Key header.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files (.csv) are supported for Kendra directory import.",
        )

    content = await file.read()
    return KendraImportService.import_from_csv_bytes(db=db, content=content)


@router.get("/guidelines", response_model=List[MoleculeGuidelineOut], status_code=status.HTTP_200_OK)
def list_molecule_guidelines(
    therapeutic_class: Optional[str] = Query(None, description="Filter by therapeutic class"),
    db: Session = Depends(get_db),
):
    """
    List authoritative molecule dispensing rules, common strengths & forms,
    verified PMBI drug codes, and clinical safety referral guidelines.
    """
    query = db.query(MoleculeGuideline)
    if therapeutic_class:
        query = query.filter(MoleculeGuideline.therapeutic_class.ilike(f"%{therapeutic_class.strip()}%"))
    return query.order_by(MoleculeGuideline.lookup_id).all()


@router.get("/groups", response_model=List[TherapeuticGroupSummary], status_code=status.HTTP_200_OK)
def list_therapeutic_groups(
    db: Session = Depends(get_db),
):
    """
    Returns all 68 reconciled PMBI therapeutic groups with active priced and
    under-process item counts.
    """
    groups = (
        db.query(
            MedicineProduct.therapeutic_group,
            func.count(MedicineProduct.id).label("total"),
        )
        .filter(
            MedicineProduct.is_jan_aushadhi == True,
            MedicineProduct.therapeutic_group != None,
        )
        .group_by(MedicineProduct.therapeutic_group)
        .order_by(func.count(MedicineProduct.id).desc())
        .all()
    )

    summaries = []
    for grp_name, total in groups:
        priced_count = (
            db.query(func.count(MedicineProduct.id))
            .join(MedicineProduct.prices)
            .filter(
                MedicineProduct.is_jan_aushadhi == True,
                MedicineProduct.therapeutic_group == grp_name,
                MedicinePrice.verification_status == "verified",
                MedicinePrice.amount_inr != None,
            )
            .scalar()
            or 0
        )
        under_process_count = total - priced_count
        summaries.append(TherapeuticGroupSummary(
            name=grp_name,
            total_products=total,
            priced_products=priced_count,
            under_process_products=under_process_count,
        ))

    return summaries


@router.get("/{kendra_id}", response_model=JanAushadhiKendraOut, status_code=status.HTTP_200_OK)
def get_kendra_detail(
    kendra_id: int = Path(..., ge=1, description="Unique database Kendra ID"),
    db: Session = Depends(get_db),
):
    """
    Return a Kendra's full verified details, address, coordinates, source URL,
    and verification status.
    """
    kendra = KendraSearchService.get_kendra_by_id(db=db, kendra_id=kendra_id)
    if not kendra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jan Aushadhi Kendra with ID {kendra_id} not found in verified registry.",
        )
    return kendra


@router.get("", response_model=List[JanAushadhiKendraOut], status_code=status.HTTP_200_OK)
def list_all_kendras(
    q: Optional[str] = Query(None, description="Search by hospital name, city, or corridor location"),
    is_24x7: Optional[bool] = Query(None, description="Filter for 24x7 operational kendras"),
    limit: int = Query(50, ge=1, le=100, description="Result limit"),
    db: Session = Depends(get_db),
):
    """
    List verified Pan-India Jan Aushadhi Kendras, campus locations,
    operating hours, and dispensing guidelines.
    """
    query = db.query(JanAushadhiKendra)
    if is_24x7 is not None:
        query = query.filter(JanAushadhiKendra.is_24x7 == is_24x7)
    if q and q.strip():
        pat = f"%{q.strip()}%"
        query = query.filter(
            or_(
                JanAushadhiKendra.kendra_name.ilike(pat),
                JanAushadhiKendra.address.ilike(pat),
                JanAushadhiKendra.city.ilike(pat),
                JanAushadhiKendra.district.ilike(pat),
                JanAushadhiKendra.state.ilike(pat),
                JanAushadhiKendra.official_kendra_code.ilike(pat),
            )
        )
    kendras = query.order_by(JanAushadhiKendra.id).limit(limit).all()
    return [KendraSearchService.to_kendra_out(k) for k in kendras]
