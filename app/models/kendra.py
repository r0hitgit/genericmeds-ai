from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import synonym
from app.core.database import Base


class JanAushadhiKendra(Base):
    __tablename__ = "jan_aushadhi_kendras"

    id = Column(Integer, primary_key=True, index=True)
    official_kendra_code = Column(String(50), unique=True, nullable=True, index=True)
    kendra_name = Column(String(255), nullable=False, index=True)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    pincode = Column(String(10), nullable=False, index=True)
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    opening_hours = Column(String(100), nullable=True)
    is_24x7 = Column(Boolean, default=False, index=True)
    portfolio_scope = Column(String(500), nullable=True)
    dispensing_rules = Column(String(1000), nullable=True)
    source_name = Column(String(100), default="PMBI Jan Aushadhi (PMBJP)", nullable=False)
    source_url = Column(String(500), default="https://janaushadhi.gov.in/locate-kendra", nullable=False)
    verification_status = Column(String(50), default="verified", nullable=False)
    last_verified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Synonyms for backward compatibility
    kendra_code = synonym("official_kendra_code")
    hospital_name = synonym("kendra_name")
    location = synonym("address")

    @property
    def city_state(self) -> str:
        if self.city and self.state:
            return f"{self.city}, {self.state}"
        return self.city or self.state or ""

    @property
    def helpline_url(self) -> str:
        return self.source_url

    def __repr__(self):
        return f"<JanAushadhiKendra {self.official_kendra_code or self.id} - {self.kendra_name} ({self.pincode})>"
