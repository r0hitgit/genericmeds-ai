from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    if settings.DATABASE_URL.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                from sqlalchemy import text
                res = conn.execute(text("PRAGMA table_info(medicine_products);")).fetchall()
                cols = [r[1] for r in res]
                new_cols = [
                    ("drug_code", "INTEGER"),
                    ("drug_code_label", "VARCHAR(50)"),
                    ("name_normalized", "VARCHAR(255)"),
                    ("generic_name_normalized", "VARCHAR(500)"),
                    ("unit_size", "VARCHAR(100)"),
                    ("mrp_display", "VARCHAR(100)"),
                    ("pricing_status", "VARCHAR(150)"),
                    ("reconciliation_cohort", "VARCHAR(255)"),
                    ("source_authority", "VARCHAR(255)"),
                    ("source_url", "VARCHAR(500)"),
                    ("source_snapshot_date", "VARCHAR(50)"),
                    ("verification_method", "VARCHAR(255)"),
                    ("individual_verification_date", "VARCHAR(50)"),
                    ("verification_status", "VARCHAR(50) DEFAULT 'verified'"),
                    ("clinical_safety_notice", "TEXT"),
                    ("imported_at", "DATETIME")
                ]
                for c_name, c_type in new_cols:
                    if c_name not in cols:
                        conn.execute(text(f"ALTER TABLE medicine_products ADD COLUMN {c_name} {c_type};"))
                
                res_pi = conn.execute(text("PRAGMA table_info(product_ingredients);")).fetchall()
                cols_pi = [r[1] for r in res_pi]
                if "raw_composition_text" not in cols_pi:
                    conn.execute(text("ALTER TABLE product_ingredients ADD COLUMN raw_composition_text VARCHAR(500);"))
                if "parsing_status" not in cols_pi:
                    conn.execute(text("ALTER TABLE product_ingredients ADD COLUMN parsing_status VARCHAR(50) DEFAULT 'verified';"))
                conn.commit()
        except Exception:
            pass
