from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class IngredientSchema(BaseModel):
    name: str = Field(..., description="Active ingredient display name")
    normalized_name: str = Field(..., description="Normalized active ingredient name")
    strength_value: float = Field(..., description="Strength value, e.g. 500")
    strength_unit: str = Field(..., description="Strength unit, e.g. mg, ml, %")

    class Config:
        from_attributes = True


class MedicinePriceSchema(BaseModel):
    id: int
    amount_inr: Optional[float] = Field(None, description="Total price in INR for the pack")
    price_type: str = Field(..., description="MRP, government_listed_price, ceiling_price, retailer_price")
    pack_quantity: float = Field(..., description="Quantity covered by this price, e.g. 10 tablets")
    unit_of_measure: str = Field(..., description="Unit of measure, e.g. tablet, capsule, ml")
    unit_price_inr: Optional[float] = Field(None, description="Normalized per-unit price in INR")
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    effective_date: Optional[datetime] = None
    verified_at: datetime
    verification_status: str = Field(..., description="verified, unverified, outdated, under_process")

    class Config:
        from_attributes = True


class DataSourceInfo(BaseModel):
    id: int
    source_name: str
    source_url: str
    source_type: str
    data_status: str

    class Config:
        from_attributes = True


class MedicineProductSummary(BaseModel):
    id: int
    brand_name: str
    generic_name: str
    manufacturer_name: Optional[str] = None
    dosage_form: str
    administration_route: str
    release_type: str
    pack_size: float
    pack_unit: str
    prescription_status: str
    is_jan_aushadhi: bool
    pmbi_code: Optional[str] = None
    therapeutic_group: Optional[str] = None
    ingredients: List[IngredientSchema] = []
    latest_price: Optional[MedicinePriceSchema] = None

    class Config:
        from_attributes = True


class MedicineProductDetail(MedicineProductSummary):
    source: Optional[DataSourceInfo] = None
    price_history: List[MedicinePriceSchema] = []
    high_risk_flag: bool = False
    high_risk_reasons: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicineSearchResponse(BaseModel):
    query: str
    match_type: str = Field(..., description="'exact' or 'partial'")
    total: int
    items: List[MedicineProductSummary]


class AlternativeSearchIngredientFilter(BaseModel):
    name: str
    strength_value: float
    strength_unit: str


class AlternativeSearchRequest(BaseModel):
    medicine_id: Optional[int] = Field(None, description="Catalogue medicine ID to find alternatives for")
    name: Optional[str] = Field(None, description="Medicine or brand name query if ID is not known")
    active_ingredients: Optional[List[AlternativeSearchIngredientFilter]] = Field(
        None, description="Explicit list of ingredients and strengths to match"
    )
    dosage_form: Optional[str] = Field(None, description="Tablet, Capsule, Syrup, etc.")
    release_type: Optional[str] = Field(None, description="immediate-release, sustained-release, etc.")


class AlternativeCandidate(BaseModel):
    product: MedicineProductSummary
    match_classification: str = Field(
        ...,
        description="'EXACT_COMPOSITION_MATCH', 'DIFFERENT_STRENGTH', 'DIFFERENT_FORMULATION', 'INSUFFICIENT_DETAILS'"
    )
    match_notes: str
    is_high_risk: bool
    high_risk_warnings: List[str] = []
    reference_unit_price: Optional[float] = None
    alternative_unit_price: Optional[float] = None
    unit_savings_inr: Optional[float] = None
    savings_percentage: Optional[float] = None


class AlternativeSearchResponse(BaseModel):
    reference_product: Optional[MedicineProductSummary] = None
    total_candidates: int
    candidates: List[AlternativeCandidate]
    safety_notice: str
