from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.source import DataSource
from app.models.medicine import MedicineProduct
from app.schemas.source import DataSourceOut

OFFICIAL_SOURCES = [
    {
        "source_name": "PMBI Jan Aushadhi (PMBJP)",
        "source_url": "https://www.pmbi.co.in/ProductList.aspx",
        "source_type": "government_procurement",
        "portal_url": "https://janaushadhi.gov.in/",
        "notes": "Pharmaceuticals & Medical Devices Bureau of India official PMBJP generic medicine list.",
    },
    {
        "source_name": "NPPA Pharma Sahi Daam",
        "source_url": "https://nppaipdms.gov.in/NPPA/PharmaSahiDaam/searchMedicine",
        "source_type": "statutory_ceiling",
        "portal_url": "https://www.nppaindia.nic.in/",
        "notes": "National Pharmaceutical Pricing Authority statutory ceiling prices for scheduled formulations.",
    },
    {
        "source_name": "CDSCO Drug Approvals",
        "source_url": "https://www.cdscoonline.gov.in/CDSCO/cdscoDrugs",
        "source_type": "regulatory_approval",
        "portal_url": "https://cdsco.gov.in/",
        "notes": "Central Drugs Standard Control Organisation regulatory approval register.",
    },
    {
        "source_name": "Verified Branded Market Retail",
        "source_url": "https://nppaipdms.gov.in/NPPA/PharmaSahiDaam/searchMedicine",
        "source_type": "market_mrp",
        "portal_url": "https://www.nppaindia.nic.in/",
        "notes": "Verified branded medicine Maximum Retail Price (MRP) from statutory price filings.",
    },
]


class SourceVerificationService:
    @classmethod
    def ensure_default_sources(cls, db: Session):
        """Ensures that official statutory and government sources exist in the database."""
        for src in OFFICIAL_SOURCES:
            existing = db.query(DataSource).filter(DataSource.source_name == src["source_name"]).first()
            if not existing:
                new_src = DataSource(
                    source_name=src["source_name"],
                    source_url=src["source_url"],
                    source_type=src["source_type"],
                    data_status="active",
                    last_checked_at=datetime.now(timezone.utc),
                    last_successful_sync_at=datetime.now(timezone.utc),
                )
                db.add(new_src)
        db.commit()

    @classmethod
    def list_sources(cls, db: Session) -> List[DataSourceOut]:
        cls.ensure_default_sources(db)
        sources = db.query(DataSource).all()
        result = []
        for s in sources:
            count = db.query(func.count(MedicineProduct.id)).filter(MedicineProduct.source_id == s.id).scalar() or 0
            result.append(
                DataSourceOut(
                    id=s.id,
                    source_name=s.source_name,
                    source_url=s.source_url,
                    source_type=s.source_type,
                    last_checked_at=s.last_checked_at,
                    last_successful_sync_at=s.last_successful_sync_at,
                    data_status=s.data_status,
                    medicine_count=count,
                )
            )
        return result
