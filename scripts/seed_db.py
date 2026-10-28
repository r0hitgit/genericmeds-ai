#!/usr/bin/env python3
"""
Seed script for GenericMeds AI database.
Populates initial verified PMBI Jan Aushadhi and market reference catalogues.
"""
import os
import sys
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import init_db, SessionLocal
from app.services.source_verification import SourceVerificationService
from app.services.data_ingestion import DataIngestionService


def main():
    print("Initializing GenericMeds AI Database Schema...")
    init_db()

    with SessionLocal() as db:
        print("Registering Official Data Sources...")
        SourceVerificationService.ensure_default_sources(db)

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        jan_aushadhi_csv = os.path.join(base_dir, "data", "imports", "pmbi_jan_aushadhi_sample.csv")
        branded_csv = os.path.join(base_dir, "data", "imports", "branded_medicines_sample.csv")

        if os.path.exists(jan_aushadhi_csv):
            print(f"Ingesting PMBI Jan Aushadhi catalog from {jan_aushadhi_csv}...")
            df_jan = pd.read_csv(jan_aushadhi_csv)
            rep_jan = DataIngestionService.ingest_catalog_dataframe(
                db=db,
                df=df_jan,
                source_name="PMBI Jan Aushadhi (PMBJP)",
                source_url="https://www.pmbi.co.in/ProductList.aspx",
            )
            print(f"Jan Aushadhi Ingestion: {rep_jan.status} - Created: {rep_jan.records_created}, Updated: {rep_jan.records_updated}")
            if rep_jan.validation_errors:
                print(f"Validation warnings: {rep_jan.validation_errors}")

        if os.path.exists(branded_csv):
            print(f"Ingesting Branded Market catalog from {branded_csv}...")
            df_brand = pd.read_csv(branded_csv)
            rep_brand = DataIngestionService.ingest_catalog_dataframe(
                db=db,
                df=df_brand,
                source_name="Verified Branded Market Retail",
                source_url="https://nppaipdms.gov.in/NPPA/PharmaSahiDaam/searchMedicine",
            )
            print(f"Branded Ingestion: {rep_brand.status} - Created: {rep_brand.records_created}, Updated: {rep_brand.records_updated}")
            if rep_brand.validation_errors:
                print(f"Validation warnings: {rep_brand.validation_errors}")

        print("Database seed completed successfully.")


if __name__ == "__main__":
    main()
