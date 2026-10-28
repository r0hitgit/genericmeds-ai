from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class CataloguePreviewReport(BaseModel):
    status: str
    file_a_name: str
    file_a_rows: int
    file_a_priced_count: int
    file_a_unpriced_count: int
    file_b_name: str
    file_b_rows: int
    matched_primary_codes_count: int
    unmatched_primary_codes: List[str]
    duplicate_codes: List[str]
    savings_audit_matches: int
    savings_audit_discrepancies: List[Dict[str, Any]]
    validation_warnings: List[str]


class CatalogueImportReport(BaseModel):
    status: str
    is_dry_run: bool
    products_processed: int
    products_created: int
    products_updated: int
    prices_created: int
    aliases_created: int
    brand_lookups_processed: int
    brand_lookups_linked: int
    brand_lookups_unresolved: int
    unresolved_primary_codes: List[str]
    validation_warnings: List[str]
    imported_at: str


class CatalogueStatusReport(BaseModel):
    status: str
    total_products: int
    jan_aushadhi_products: int
    active_priced_products: int
    under_process_unpriced_products: int
    branded_market_reference_products: int
    total_brand_lookups: int
    linked_brand_lookups: int
    unresolved_brand_lookups: int
    total_aliases: int
    unresolved_codes_flagged: List[str]
    data_freshness_snapshot: Optional[str] = None
    last_imported_at: Optional[str] = None
    quality_warnings: List[str]
