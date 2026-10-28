from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PriceComparisonRequest(BaseModel):
    product_ids: List[int] = Field(..., min_length=2, description="List of at least two product IDs to compare")
    reference_product_id: Optional[int] = Field(None, description="Product ID to use as baseline reference for savings calculation")


class PriceComparisonItem(BaseModel):
    product_id: int
    brand_name: str
    generic_name: str
    manufacturer_name: Optional[str] = None
    composition: str
    strength: str
    dosage_form: str
    administration_route: str
    release_type: str
    pack_size: float
    pack_unit: str
    listed_price_inr: Optional[float] = None
    unit_price_inr: Optional[float] = None
    price_type: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    last_verified: Optional[datetime] = None
    verification_status: str
    is_jan_aushadhi: bool
    is_price_verified: bool


class PriceComparisonDifference(BaseModel):
    compared_product_id: int
    compared_brand_name: str
    reference_product_id: int
    reference_brand_name: str
    is_comparable: bool
    incomparability_reasons: List[str] = []
    reference_unit_price_inr: Optional[float] = None
    alternative_unit_price_inr: Optional[float] = None
    unit_savings_inr: Optional[float] = None
    savings_percentage: Optional[float] = None
    pack_savings_inr: Optional[float] = None
    notes: str


class PriceComparisonResponse(BaseModel):
    items: List[PriceComparisonItem]
    comparisons: List[PriceComparisonDifference]
    summary_notes: List[str]
    safety_disclaimer: str
