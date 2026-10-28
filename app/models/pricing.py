from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class MedicinePrice(Base):
    __tablename__ = "medicine_prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("medicine_products.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_inr = Column(Float, nullable=True)  # Null if under rate contract/process; never 0
    price_type = Column(String(100), nullable=False)  # MRP, government_listed_price, ceiling_price, retailer_price
    pack_quantity = Column(Float, nullable=False)  # quantity of items/volume this price covers
    unit_of_measure = Column(String(50), nullable=False)  # tablet, capsule, ml, etc.
    source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True)
    source_url = Column(String(500), nullable=True)
    effective_date = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    verification_status = Column(String(50), default="verified", nullable=False)  # verified, unverified, outdated, under_process

    # Relationships
    product = relationship("MedicineProduct", back_populates="prices")
    source = relationship("DataSource", back_populates="prices")

    @property
    def unit_price_inr(self) -> float:
        """Calculates normalized per-unit price in INR."""
        if self.amount_inr is not None and self.pack_quantity and self.pack_quantity > 0:
            return round(self.amount_inr / self.pack_quantity, 2)
        elif self.amount_inr is not None:
            return round(self.amount_inr, 2)
        return None

    def __repr__(self):
        return f"<MedicinePrice ₹{self.amount_inr} ({self.price_type}) for Product {self.product_id}>"
