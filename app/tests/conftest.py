import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure test environment settings
os.environ["ENVIRONMENT"] = "testing"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["ADMIN_API_KEY"] = "test-admin-secret-key"

from app.core.database import Base, get_db
from app.main import app
from app.models.source import DataSource
from app.models.ingredient import ActiveIngredient, ProductIngredient
from app.models.medicine import MedicineProduct
from app.models.pricing import MedicinePrice
from datetime import datetime, timezone, timedelta

# In-memory SQLite for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Seed core test records
    now = datetime.now(timezone.utc)
    stale_date = now - timedelta(days=120)

    # Sources
    src_jan = DataSource(
        id=1,
        source_name="PMBI Jan Aushadhi (PMBJP)",
        source_url="https://www.pmbi.co.in/ProductList.aspx",
        source_type="government_procurement",
        last_checked_at=now,
        last_successful_sync_at=now,
        data_status="active",
    )
    src_market = DataSource(
        id=2,
        source_name="Verified Branded Market Retail",
        source_url="https://nppaipdms.gov.in/NPPA/PharmaSahiDaam/searchMedicine",
        source_type="market_mrp",
        last_checked_at=now,
        last_successful_sync_at=now,
        data_status="active",
    )
    session.add_all([src_jan, src_market])
    session.flush()

    # Active Ingredients
    ing_para = ActiveIngredient(id=1, display_name="Paracetamol", normalized_name="paracetamol")
    ing_amox = ActiveIngredient(id=2, display_name="Amoxicillin", normalized_name="amoxicillin")
    ing_clav = ActiveIngredient(id=3, display_name="Potassium Clavulanate", normalized_name="potassium clavulanate")
    ing_met = ActiveIngredient(id=4, display_name="Metformin", normalized_name="metformin")
    ing_warf = ActiveIngredient(id=5, display_name="Warfarin", normalized_name="warfarin")
    ing_ins = ActiveIngredient(id=6, display_name="Insulin", normalized_name="insulin")
    ing_folic = ActiveIngredient(id=7, display_name="Folic Acid", normalized_name="folic acid")
    ing_omep = ActiveIngredient(id=8, display_name="Omeprazole", normalized_name="omeprazole")
    session.add_all([ing_para, ing_amox, ing_clav, ing_met, ing_warf, ing_ins, ing_folic, ing_omep])
    session.flush()

    # 1. Dolo 650 (Branded Paracetamol 650mg)
    p_dolo = MedicineProduct(
        id=1,
        brand_name="Dolo 650",
        generic_name="Paracetamol Tablets IP",
        manufacturer_name="Micro Labs Ltd",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=15.0,
        pack_unit="tablets",
        prescription_status="OTC",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_dolo)
    session.flush()
    session.add(ProductIngredient(product_id=p_dolo.id, ingredient_id=ing_para.id, strength_value=650.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_dolo.id,
        amount_inr=30.0,
        price_type="MRP",
        pack_quantity=15.0,
        unit_of_measure="tablets",
        source_id=src_market.id,
        source_url="https://nppaipdms.gov.in",
        verified_at=now,
        verification_status="verified",
    ))

    # 2. Jan Aushadhi Paracetamol 650 (Generic equivalent of Dolo 650)
    p_jan_para650 = MedicineProduct(
        id=2,
        brand_name="Jan Aushadhi Paracetamol 650",
        generic_name="Paracetamol Tablets IP",
        manufacturer_name="PMBI Jan Aushadhi",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=10.0,
        pack_unit="tablets",
        prescription_status="OTC",
        is_jan_aushadhi=True,
        source_id=src_jan.id,
    )
    session.add(p_jan_para650)
    session.flush()
    session.add(ProductIngredient(product_id=p_jan_para650.id, ingredient_id=ing_para.id, strength_value=650.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_jan_para650.id,
        amount_inr=10.0,
        price_type="government_listed_price",
        pack_quantity=10.0,
        unit_of_measure="tablets",
        source_id=src_jan.id,
        source_url="https://www.pmbi.co.in/ProductList.aspx",
        verified_at=now,
        verification_status="verified",
    ))

    # 3. Calpol 500 (Different strength: 500mg vs 650mg)
    p_calpol500 = MedicineProduct(
        id=3,
        brand_name="Calpol 500",
        generic_name="Paracetamol Tablets IP",
        manufacturer_name="GSK",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=15.0,
        pack_unit="tablets",
        prescription_status="OTC",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_calpol500)
    session.flush()
    session.add(ProductIngredient(product_id=p_calpol500.id, ingredient_id=ing_para.id, strength_value=500.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_calpol500.id,
        amount_inr=20.0,
        price_type="MRP",
        pack_quantity=15.0,
        unit_of_measure="tablets",
        source_id=src_market.id,
        verified_at=now,
        verification_status="verified",
    ))

    # 4. Paracetamol Syrup 250mg/5ml (Incompatible dosage form: Syrup vs Tablet)
    p_para_syp = MedicineProduct(
        id=4,
        brand_name="Calpol Paediatric Syrup",
        generic_name="Paracetamol Paediatric Suspension",
        manufacturer_name="GSK",
        dosage_form="Syrup",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=60.0,
        pack_unit="ml",
        prescription_status="OTC",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_para_syp)
    session.flush()
    session.add(ProductIngredient(product_id=p_para_syp.id, ingredient_id=ing_para.id, strength_value=250.0, strength_unit="mg"))

    # 5. Augmentin 625 Duo (Combination product: Amoxicillin 500mg + Potassium Clavulanate 125mg)
    p_aug = MedicineProduct(
        id=5,
        brand_name="Augmentin 625 Duo",
        generic_name="Amoxicillin and Potassium Clavulanate Tablets IP",
        manufacturer_name="GSK",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=10.0,
        pack_unit="tablets",
        prescription_status="Schedule H",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_aug)
    session.flush()
    session.add(ProductIngredient(product_id=p_aug.id, ingredient_id=ing_amox.id, strength_value=500.0, strength_unit="mg"))
    session.add(ProductIngredient(product_id=p_aug.id, ingredient_id=ing_clav.id, strength_value=125.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_aug.id,
        amount_inr=200.0,
        price_type="MRP",
        pack_quantity=10.0,
        unit_of_measure="tablets",
        source_id=src_market.id,
        verified_at=now,
        verification_status="verified",
    ))

    # 6. Jan Aushadhi Amoxyclav 625 (Combination product match)
    p_jan_amox = MedicineProduct(
        id=6,
        brand_name="Jan Aushadhi Amoxyclav 625",
        generic_name="Amoxicillin and Potassium Clavulanate Tablets IP",
        manufacturer_name="PMBI Jan Aushadhi",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=10.0,
        pack_unit="tablets",
        prescription_status="Schedule H",
        is_jan_aushadhi=True,
        source_id=src_jan.id,
    )
    session.add(p_jan_amox)
    session.flush()
    session.add(ProductIngredient(product_id=p_jan_amox.id, ingredient_id=ing_amox.id, strength_value=500.0, strength_unit="mg"))
    session.add(ProductIngredient(product_id=p_jan_amox.id, ingredient_id=ing_clav.id, strength_value=125.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_jan_amox.id,
        amount_inr=50.0,
        price_type="government_listed_price",
        pack_quantity=10.0,
        unit_of_measure="tablets",
        source_id=src_jan.id,
        source_url="https://www.pmbi.co.in/ProductList.aspx",
        verified_at=now,
        verification_status="verified",
    ))

    # 7. Glycomet 500 SR (Sustained Release)
    p_glyco = MedicineProduct(
        id=7,
        brand_name="Glycomet 500 SR",
        generic_name="Metformin Hydrochloride Prolonged-Release Tablets IP",
        manufacturer_name="USV",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="sustained-release",
        pack_size=20.0,
        pack_unit="tablets",
        prescription_status="Schedule H",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_glyco)
    session.flush()
    session.add(ProductIngredient(product_id=p_glyco.id, ingredient_id=ing_met.id, strength_value=500.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_glyco.id,
        amount_inr=40.0,
        price_type="MRP",
        pack_quantity=20.0,
        unit_of_measure="tablets",
        source_id=src_market.id,
        verified_at=now,
        verification_status="verified",
    ))

    # 8. Metformin 500 Immediate-Release (Incompatible release profile with Glycomet SR)
    p_met_ir = MedicineProduct(
        id=8,
        brand_name="Metformin 500 Plain",
        generic_name="Metformin Hydrochloride Tablets IP",
        manufacturer_name="Generic Pharma",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=10.0,
        pack_unit="tablets",
        prescription_status="Schedule H",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_met_ir)
    session.flush()
    session.add(ProductIngredient(product_id=p_met_ir.id, ingredient_id=ing_met.id, strength_value=500.0, strength_unit="mg"))

    # 9. Stale Price Product (verified_at > 90 days ago)
    p_stale = MedicineProduct(
        id=9,
        brand_name="Stale Price Med 650",
        generic_name="Paracetamol Tablets IP",
        manufacturer_name="Old Pharma",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=10.0,
        pack_unit="tablets",
        prescription_status="OTC",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_stale)
    session.flush()
    session.add(ProductIngredient(product_id=p_stale.id, ingredient_id=ing_para.id, strength_value=650.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_stale.id,
        amount_inr=15.0,
        price_type="MRP",
        pack_quantity=10.0,
        unit_of_measure="tablets",
        source_id=src_market.id,
        verified_at=stale_date,
        verification_status="verified",
    ))

    # 10. High-Risk Warfarin Product
    p_warf = MedicineProduct(
        id=10,
        brand_name="Warf 5",
        generic_name="Warfarin Tablets IP",
        manufacturer_name="Cipla Ltd",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=10.0,
        pack_unit="tablets",
        prescription_status="Schedule H",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_warf)
    session.flush()
    session.add(ProductIngredient(product_id=p_warf.id, ingredient_id=ing_warf.id, strength_value=5.0, strength_unit="mg"))

    # 11. High-Risk Injectable Insulin
    p_ins = MedicineProduct(
        id=11,
        brand_name="Mixtard 30/70",
        generic_name="Biphasic Isophane Insulin Injection IP",
        manufacturer_name="Novo Nordisk",
        dosage_form="Injection",
        administration_route="Subcutaneous",
        release_type="immediate-release",
        pack_size=10.0,
        pack_unit="ml",
        prescription_status="Schedule H",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_ins)
    session.flush()
    session.add(ProductIngredient(product_id=p_ins.id, ingredient_id=ing_ins.id, strength_value=100.0, strength_unit="iu"))

    # 12. Folvite (Branded Folic Acid 5mg)
    p_folvite = MedicineProduct(
        id=12,
        brand_name="Folvite",
        generic_name="Folic Acid Tablets IP",
        manufacturer_name="Pfizer Ltd",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=15.0,
        pack_unit="tablets",
        prescription_status="Prescription",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_folvite)
    session.flush()
    session.add(ProductIngredient(product_id=p_folvite.id, ingredient_id=ing_folic.id, strength_value=5.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_folvite.id,
        amount_inr=78.50,
        price_type="MRP",
        pack_quantity=15.0,
        unit_of_measure="tablets",
        source_id=src_market.id,
        verified_at=now,
        verification_status="verified",
    ))

    # 13. Jan Aushadhi Folic Acid 5mg (Generic Equivalent)
    p_jan_folic = MedicineProduct(
        id=13,
        brand_name="Jan Aushadhi Folic Acid",
        generic_name="Folic Acid Tablets IP 5 mg",
        manufacturer_name="PMBI Jan Aushadhi",
        dosage_form="Tablet",
        administration_route="Oral",
        release_type="immediate-release",
        pack_size=15.0,
        pack_unit="tablets",
        prescription_status="Prescription",
        is_jan_aushadhi=True,
        source_id=src_jan.id,
    )
    session.add(p_jan_folic)
    session.flush()
    session.add(ProductIngredient(product_id=p_jan_folic.id, ingredient_id=ing_folic.id, strength_value=5.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_jan_folic.id,
        amount_inr=4.54,
        price_type="government_listed_price",
        pack_quantity=15.0,
        unit_of_measure="tablets",
        source_id=src_jan.id,
        verified_at=now,
        verification_status="verified",
    ))

    # 14. Omee 20 (Branded Omeprazole 20mg)
    p_omee = MedicineProduct(
        id=14,
        brand_name="Omee 20",
        generic_name="Omeprazole Capsules IP",
        manufacturer_name="Alkem Laboratories",
        dosage_form="Capsule",
        administration_route="Oral",
        release_type="modified-release",
        pack_size=20.0,
        pack_unit="capsules",
        prescription_status="Schedule H",
        is_jan_aushadhi=False,
        source_id=src_market.id,
    )
    session.add(p_omee)
    session.flush()
    session.add(ProductIngredient(product_id=p_omee.id, ingredient_id=ing_omep.id, strength_value=20.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_omee.id,
        amount_inr=72.0,
        price_type="MRP",
        pack_quantity=20.0,
        unit_of_measure="capsules",
        source_id=src_market.id,
        verified_at=now,
        verification_status="verified",
    ))

    # 15. Jan Aushadhi Omeprazole 20mg (Generic Equivalent)
    p_jan_omee = MedicineProduct(
        id=15,
        brand_name="Jan Aushadhi Omeprazole",
        generic_name="Omeprazole Gastro-resistant Capsules IP 20 mg",
        manufacturer_name="PMBI Jan Aushadhi",
        dosage_form="Capsule",
        administration_route="Oral",
        release_type="modified-release",
        pack_size=10.0,
        pack_unit="capsules",
        prescription_status="Schedule H",
        is_jan_aushadhi=True,
        source_id=src_jan.id,
    )
    session.add(p_jan_omee)
    session.flush()
    session.add(ProductIngredient(product_id=p_jan_omee.id, ingredient_id=ing_omep.id, strength_value=20.0, strength_unit="mg"))
    session.add(MedicinePrice(
        product_id=p_jan_omee.id,
        amount_inr=10.21,
        price_type="government_listed_price",
        pack_quantity=10.0,
        unit_of_measure="capsules",
        source_id=src_jan.id,
        verified_at=now,
        verification_status="verified",
    ))

    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
