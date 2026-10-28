from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class MedicineProduct(Base):
    __tablename__ = "medicine_products"

    id = Column(Integer, primary_key=True, index=True)
    drug_code = Column(Integer, nullable=True, index=True)
    drug_code_label = Column(String(50), nullable=True, index=True)  # e.g. "PMBI-1"
    brand_name = Column(String(255), nullable=False, index=True)
    name_normalized = Column(String(255), nullable=True, index=True)
    generic_name = Column(String(500), nullable=False, index=True)
    generic_name_normalized = Column(String(500), nullable=True, index=True)
    manufacturer_name = Column(String(255), nullable=True, index=True)
    dosage_form = Column(String(100), nullable=False, index=True)  # Tablet, Capsule, Syrup, Injection, Cream, etc.
    administration_route = Column(String(100), nullable=False, default="Oral", index=True)  # Oral, Topical, IV, etc.
    release_type = Column(String(100), nullable=False, default="immediate-release", index=True)  # immediate-release, modified-release, sustained-release, extended-release
    pack_size = Column(Float, nullable=False, default=10.0)  # Quantity in pack (e.g. 10 tablets, 100 ml)
    pack_unit = Column(String(50), nullable=False, default="tablets")  # tablets, capsules, ml, etc.
    unit_size = Column(String(100), nullable=True)  # raw catalogue package text e.g. "10's", "15 g", "3 ml"
    mrp_display = Column(String(100), nullable=True)  # raw formatted MRP e.g. "INR 10.32"
    pricing_status = Column(String(150), nullable=True, index=True)  # Active Priced in PMBI Basket vs Under Rate Contract / Process
    prescription_status = Column(String(100), nullable=False, default="Schedule H")  # Schedule H, Schedule H1, OTC, etc.
    is_jan_aushadhi = Column(Boolean, default=False, index=True)
    pmbi_code = Column(String(50), nullable=True, index=True)  # Normalized PMBI code e.g. "PMBI-1"
    therapeutic_group = Column(String(255), nullable=True, index=True)
    reconciliation_cohort = Column(String(255), nullable=True)
    source_authority = Column(String(255), nullable=True)
    source_url = Column(String(500), nullable=True)
    source_snapshot_date = Column(String(50), nullable=True)
    verification_method = Column(String(255), nullable=True)
    individual_verification_date = Column(String(50), nullable=True)
    verification_status = Column(String(50), default="verified", nullable=False, index=True)
    clinical_safety_notice = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True)

    imported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    source = relationship("DataSource", back_populates="medicines")
    ingredients = relationship("ProductIngredient", back_populates="product", cascade="all, delete-orphan", order_by="ProductIngredient.id")
    prices = relationship("MedicinePrice", back_populates="product", cascade="all, delete-orphan", order_by="desc(MedicinePrice.verified_at)")
    aliases = relationship("MedicineAlias", back_populates="product", cascade="all, delete-orphan", order_by="MedicineAlias.id")
    brand_lookups = relationship("BrandGenericLookup", back_populates="linked_product", order_by="BrandGenericLookup.id")

    @property
    def latest_verified_price(self):
        for p in self.prices:
            if p.verification_status == "verified":
                return p
        return None

    def __repr__(self):
        return f"<MedicineProduct {self.pmbi_code or self.id} - {self.brand_name} ({self.generic_name})>"
