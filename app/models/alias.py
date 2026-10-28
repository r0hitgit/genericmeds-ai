from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class MedicineAlias(Base):
    __tablename__ = "medicine_aliases"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("medicine_products.id", ondelete="CASCADE"), nullable=False, index=True)
    alias = Column(String(500), nullable=False)
    alias_normalized = Column(String(500), nullable=False, index=True)
    alias_type = Column(String(100), nullable=False, default="brand", index=True)  # brand, colloquial, phonetic, generic_synonym, search_keyword
    source_file = Column(String(255), nullable=True)
    verification_status = Column(String(50), default="verified", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_alias_norm_type", "alias_normalized", "alias_type"),
    )

    # Relationship
    product = relationship("MedicineProduct", back_populates="aliases")

    def __repr__(self):
        return f"<MedicineAlias {self.alias} ({self.alias_type}) for Product {self.product_id}>"
