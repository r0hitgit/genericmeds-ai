from sqlalchemy import Column, Integer, String
from app.core.database import Base


class MoleculeGuideline(Base):
    __tablename__ = "molecule_guidelines"

    id = Column(Integer, primary_key=True, index=True)
    lookup_id = Column(String(50), unique=True, nullable=False, index=True)
    therapeutic_class = Column(String(255), nullable=False, index=True)
    active_ingredient = Column(String(255), nullable=False, index=True)
    strengths_forms = Column(String(255), nullable=True)
    pmbi_codes = Column(String(255), nullable=True)
    pack_sizes = Column(String(255), nullable=True)
    pmbi_mrp = Column(String(255), nullable=True)
    branded_mrp = Column(String(255), nullable=True)
    price_diff_pct = Column(String(50), nullable=True)
    dispensing_rule = Column(String(1000), nullable=False)
    reference_url = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<MoleculeGuideline {self.lookup_id} - {self.active_ingredient}>"
