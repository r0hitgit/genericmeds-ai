from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(255), unique=True, nullable=False, index=True)
    source_url = Column(String(500), nullable=False)
    source_type = Column(String(100), nullable=False)  # government_procurement, ceiling_price, cdsco_approval, etc.
    last_checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_successful_sync_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    data_status = Column(String(50), default="active", nullable=False)  # active, stale, offline

    # Relationships
    medicines = relationship("MedicineProduct", back_populates="source", cascade="all, delete-orphan")
    prices = relationship("MedicinePrice", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DataSource {self.source_name} ({self.source_type})>"
