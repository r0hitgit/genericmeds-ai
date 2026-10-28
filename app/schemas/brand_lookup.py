from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.medicine import MedicineProductSummary


class BrandGenericLookupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_lookup_id: str
    popular_brand_names: str
    popular_brand_names_normalized: Optional[str] = None
    phonetic_and_colloquial_aliases: Optional[str] = None
    market_reference_manufacturers: Optional[str] = None
    therapeutic_category: Optional[str] = None
    active_generic_composition: str
    primary_pmbi_drug_code: str
    all_matching_pmbi_codes_and_strengths: Optional[str] = None
    unit_pack_size: Optional[str] = None
    janaushadhi_mrp_inr: Optional[float] = None
    branded_market_reference_inr: Optional[float] = None
    indicative_savings_inr: Optional[float] = None
    indicative_savings_pct: Optional[str] = None
    indicative_savings_pct_numeric: Optional[float] = None
    pharmacist_and_doctor_verification_rule: Optional[str] = None
    reconciliation_status: str
    linked_product_id: Optional[int] = None
    linked_product: Optional[MedicineProductSummary] = None
    source_file: Optional[str] = None
    review_status: str


class BrandSearchResponse(BaseModel):
    query: str
    total: int
    limit: int
    offset: int
    items: List[BrandGenericLookupOut]
