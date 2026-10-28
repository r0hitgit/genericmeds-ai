from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class JanAushadhiKendraOut(BaseModel):
    id: int
    official_kendra_code: Optional[str] = Field(None, description="Official PMBI Jan Aushadhi Kendra code")
    kendra_code: Optional[str] = Field(None, description="Alias for official_kendra_code")
    kendra_name: str = Field(..., description="Kendra store name or hospital campus branch name")
    hospital_name: Optional[str] = Field(None, description="Alias for kendra_name")
    address: str = Field(..., description="Full verified address and landmark")
    location: Optional[str] = Field(None, description="Alias for address")
    city: str
    district: str
    state: str
    pincode: str
    city_state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    opening_hours: Optional[str] = None
    is_24x7: bool = False
    distance_km: Optional[float] = Field(None, description="Calculated distance in km from user coordinates")
    is_distance_approximate: bool = False
    directions_url: Optional[str] = Field(None, description="Direct navigation link")
    stock_status: str = Field("Medicine stock not confirmed", description="Inventory disclaimer status")
    portfolio_scope: Optional[str] = None
    dispensing_rules: Optional[str] = None
    source_name: str
    source_url: str
    helpline_url: Optional[str] = None
    verification_status: str
    last_verified_at: datetime

    class Config:
        from_attributes = True


class KendraNearbyResponse(BaseModel):
    user_latitude: float
    user_longitude: float
    radius_km: float
    total_found: int
    kendras: List[JanAushadhiKendraOut]
    stock_disclaimer: str
    official_locator_url: str
    wider_radius_suggested: Optional[float] = None


class KendraSearchResponse(BaseModel):
    total_found: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    kendras: List[JanAushadhiKendraOut]
    stock_disclaimer: str
    official_locator_url: str


class KendraImportRowError(BaseModel):
    row_index: int
    official_kendra_code: Optional[str] = None
    error_message: str


class KendraImportResponse(BaseModel):
    total_rows_processed: int
    records_created: int
    records_updated: int
    records_rejected: int
    row_errors: List[KendraImportRowError] = []
    status: str = Field(..., description="'success', 'partial_success', 'failed'")


class MoleculeGuidelineOut(BaseModel):
    id: int
    lookup_id: str
    therapeutic_class: str
    active_ingredient: str
    strengths_forms: Optional[str] = None
    pmbi_codes: Optional[str] = None
    pack_sizes: Optional[str] = None
    pmbi_mrp: Optional[str] = None
    branded_mrp: Optional[str] = None
    price_diff_pct: Optional[str] = None
    dispensing_rule: str
    reference_url: Optional[str] = None

    class Config:
        from_attributes = True


class TherapeuticGroupSummary(BaseModel):
    name: str
    total_products: int
    priced_products: int
    under_process_products: int
