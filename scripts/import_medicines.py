#!/usr/bin/env python3
"""
CLI tool to import validated CSV or Excel medicine catalogs into GenericMeds AI.
Usage:
    python scripts/import_medicines.py --file data/imports/my_catalog.csv --source "PMBI Jan Aushadhi (PMBJP)"
"""
import os
import sys
import argparse
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, init_db
from app.services.data_ingestion import DataIngestionService


def main():
    parser = argparse.ArgumentParser(description="Import medicine catalog into GenericMeds AI")
    parser.add_argument("--file", required=True, help="Path to CSV or Excel file")
    parser.add_argument("--source", default="Manual Admin Import", help="Data source identifier")
    parser.add_argument("--url", default="https://genericmeds.gov.in", help="Data source URL")

    args = parser.parse_args()
    file_path = os.path.abspath(args.file)

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    print(f"Reading {file_path}...")
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
    else:
        print("Error: Unsupported file format. Use .csv or .xlsx")
        sys.exit(1)

    init_db()
    with SessionLocal() as db:
        report = DataIngestionService.ingest_catalog_dataframe(
            db=db,
            df=df,
            source_name=args.source,
            source_url=args.url,
        )
        print(f"Import Status: {report.status}")
        print(f"Processed: {report.records_processed}")
        print(f"Created: {report.records_created}")
        print(f"Updated: {report.records_updated}")
        if report.validation_errors:
            print("Validation Errors/Warnings:")
            for err in report.validation_errors:
                print(f"  - {err}")


if __name__ == "__main__":
    main()
