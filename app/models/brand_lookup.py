from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class BrandGenericLookup(Base):
    __tablename__ = "brand_generic_lookups"

    id = Column(Integer, primary_key=True, index=True)
    brand_lookup_id = Column(String(50), unique=True, nullable=False, index=True)  # BRD-001 ...
    popular_brand_names = Column(String(500), nullable=False)
    popular_brand_names_normalized = Column(String(500), nullable=False, index=True)
    phonetic_and_colloquial_aliases = Column(Text, nullable=True)
    market_reference_manufacturers = Column(String(500), nullable=True)
    therapeutic_category = Column(String(255), nullable=True, index=True)
    active_generic_composition = Column(String(500), nullable=False)
    primary_pmbi_drug_code = Column(String(50), nullable=False, index=True)  # Normalized e.g. "PMBI-264"
    all_matching_pmbi_codes_and_strengths = Column(Text, nullable=True)
    unit_pack_size = Column(String(100), nullable=True)
    janaushadhi_mrp_inr = Column(Float, nullable=True)
    branded_market_reference_inr = Column(Float, nullable=True)
    indicative_savings_inr = Column(Float, nullable=True)
    indicative_savings_pct = Column(String(50), nullable=True)  # Raw string e.g. "89.7%"
    indicative_savings_pct_numeric = Column(Float, nullable=True)  # 89.7
    recalculated_savings_inr = Column(Float, nullable=True)
    recalculated_savings_pct = Column(Float, nullable=True)
    savings_audit_status = Column(String(50), default="MATCH", nullable=False)  # MATCH, DISCREPANCY
    pharmacist_and_doctor_verification_rule = Column(Text, nullable=True)
    reconciliation_status = Column(String(50), default="LINKED", nullable=False, index=True)  # LINKED, UNRESOLVED_CODE
    linked_product_id = Column(Integer, ForeignKey("medicine_products.id", ondelete="SET NULL"), nullable=True, index=True)
    source_file = Column(String(255), default="pmbjp_popular_indian_brands_to_generic.csv")
    import_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    review_status = Column(String(50), default="reviewed", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    linked_product = relationship("MedicineProduct", back_populates="brand_lookups")

    def __repr__(self):
        return f"<BrandGenericLookup {self.brand_lookup_id}: {self.popular_brand_names} -> {self.primary_pmbi_drug_code}>"
