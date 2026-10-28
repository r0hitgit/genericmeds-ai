#!/usr/bin/env python3
"""
Master data generator and loader for GenericMeds AI.
Ingests:
1. Complete PMBI basket medicines (with pricing or under-process status)
2. Flagship branded market references (39 products for instant price comparisons)
3. Active-ingredient clinical references
4. Pan-India Hospital Jan Aushadhi Kendra Directory
"""

import os
import sys
import re
import csv
import pandas as pd
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, init_db
from app.models.source import DataSource
from app.models.ingredient import ActiveIngredient, ProductIngredient
from app.models.medicine import MedicineProduct
from app.models.pricing import MedicinePrice
from app.models.kendra import JanAushadhiKendra
from app.services.source_verification import SourceVerificationService
from app.services.data_ingestion import DataIngestionService
from scripts.process_all_pmbjp_data import clean_number, parse_pack_info, parse_dosage_form, parse_release_type, parse_prescription_status
from scripts.build_datasets import KENDRA_DATA, FLAGSHIP_COMPARISONS


def load_master_catalogue_rows():
    """Returns all rows from the user-supplied PMBI master catalogue."""
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "imports", "pmbjp_reconciled_master_catalogue.csv"))
    if not os.path.exists(data_file):
        print(f"File not found: {data_file}")
        return []

    rows = []
    with open(data_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if not r.get("PMBI Drug Code"):
                continue
            rows.append(r)
    return rows


def ingest_all_master_data():
    init_db()
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    try:
        # 1. Sources
        SourceVerificationService.ensure_default_sources(db)
        src_jan = db.query(DataSource).filter(DataSource.source_name == "PMBI Jan Aushadhi (PMBJP)").first()
        src_market = db.query(DataSource).filter(DataSource.source_name == "Verified Branded Market Retail").first()

        # 2. Kendras
        print("1. Ingesting Pan-India Jan Aushadhi Kendra Directory...")
        k_created = 0
        k_updated = 0
        for k in KENDRA_DATA:
            existing = db.query(JanAushadhiKendra).filter(JanAushadhiKendra.kendra_code == k["kendra_code"]).first()
            if existing:
                for attr, val in k.items():
                    setattr(existing, attr, val)
                k_updated += 1
            else:
                db.add(JanAushadhiKendra(**k))
                k_created += 1
        db.commit()
        print(f"   -> Kendras: {k_created} created, {k_updated} updated.")

        # 3. Flagship Branded References
        print("2. Ingesting 39 Flagship Branded Market Reference Comparisons...")
        b_created = 0
        b_updated = 0
        for item in FLAGSHIP_COMPARISONS:
            b_name = item["brand_ref"].split("/")[0].strip()
            g_name = item["name"]
            p_size, p_unit = parse_pack_info(item["pack"])
            d_form, a_route = parse_dosage_form(g_name, item["category"])
            r_type = parse_release_type(g_name)
            rx_status = parse_prescription_status(item["category"], g_name)

            existing_prod = db.query(MedicineProduct).filter(
                MedicineProduct.brand_name.ilike(b_name),
                MedicineProduct.is_jan_aushadhi == False,
            ).first()

            if existing_prod:
                existing_prod.generic_name = g_name
                existing_prod.pack_size = p_size
                existing_prod.pack_unit = p_unit
                prod = existing_prod
                b_updated += 1
            else:
                prod = MedicineProduct(
                    brand_name=b_name,
                    generic_name=g_name,
                    manufacturer_name="Market Reference Manufacturer",
                    dosage_form=d_form,
                    administration_route=a_route,
                    release_type=r_type,
                    pack_size=p_size,
                    pack_unit=p_unit,
                    prescription_status=rx_status,
                    is_jan_aushadhi=False,
                    therapeutic_group=item["category"],
                    source_id=src_market.id,
                    created_at=now,
                    updated_at=now,
                )
                db.add(prod)
                db.flush()
                b_created += 1

                # Ingredients
                parsed_ings = DataIngestionService.parse_ingredients_field(g_name)
                seen_flagship_ings = set()
                for ing in parsed_ings:
                    disp, norm = DataIngestionService.normalize_ingredient_name(ing["name"])
                    if not norm or norm in seen_flagship_ings:
                        continue
                    seen_flagship_ings.add(norm)
                    act = db.query(ActiveIngredient).filter(ActiveIngredient.normalized_name == norm).first()
                    if not act:
                        act = ActiveIngredient(normalized_name=norm, display_name=disp)
                        db.add(act)
                        db.flush()
                    pi = ProductIngredient(
                        product_id=prod.id,
                        ingredient_id=act.id,
                        strength_value=ing["strength_value"],
                        strength_unit=ing["strength_unit"],
                    )
                    db.add(pi)

            # Price record
            mrp_val = item["market_price"]
            ex_price = db.query(MedicinePrice).filter(
                MedicinePrice.product_id == prod.id,
                MedicinePrice.price_type == "MRP"
            ).first()
            if not ex_price:
                db.add(MedicinePrice(
                    product_id=prod.id,
                    amount_inr=mrp_val,
                    price_type="MRP",
                    pack_quantity=p_size,
                    unit_of_measure=p_unit,
                    source_id=src_market.id,
                    source_url="https://nppaipdms.gov.in/NPPA/PharmaSahiDaam/searchMedicine",
                    verified_at=now,
                    verification_status="verified",
                ))
        db.commit()
        print(f"   -> Flagship Branded References: {b_created} created, {b_updated} updated.")

        # 4. Ingest All Master Catalogue Rows
        print("3. Ingesting PMBJP Master Catalogue Medicines...")
        pmbi_rows = load_master_catalogue_rows()
        print(f"   Total rows to ingest from master catalogue: {len(pmbi_rows)}")

        p_created = 0
        p_updated = 0

        for r in pmbi_rows:
            code = r.get("PMBI Drug Code", "").strip()
            raw_name = r.get("Generic Medicine / Surgical Product Name (IP / BP / USP)", "").strip()
            pack_raw = r.get("Unit Pack Size", "").strip()
            price_raw = r.get("Official MRP (INR)", "")
            status_raw = r.get("Pricing & Availability Status", "").strip()
            group_raw = r.get("Therapeutic Group (68 Official Groups)", "").strip()
            source_url = r.get("Product Source URL", "https://janaushadhi.gov.in/").strip()

            if not raw_name:
                continue

            # Standardized brand name for Jan Aushadhi
            brand_name = raw_name if raw_name.lower().startswith("jan") else f"Jan Aushadhi {raw_name}"
            # Shorten if over 250 chars
            brand_name = brand_name[:250]
            generic_name = raw_name[:490]

            pack_size, pack_unit = parse_pack_info(pack_raw)
            d_form, a_route = parse_dosage_form(raw_name, group_raw)
            r_type = parse_release_type(raw_name)
            rx_status = parse_prescription_status(group_raw, raw_name)
            price_val = clean_number(price_raw)

            # Check existing product by pmbi_code or brand_name + pack_size
            prod = db.query(MedicineProduct).filter(
                (MedicineProduct.pmbi_code == code) |
                ((MedicineProduct.brand_name == brand_name) & (MedicineProduct.pack_size == pack_size))
            ).first()

            if prod:
                prod.generic_name = generic_name
                prod.pmbi_code = code
                prod.therapeutic_group = group_raw
                prod.dosage_form = d_form
                prod.administration_route = a_route
                prod.release_type = r_type
                prod.pack_size = pack_size
                prod.pack_unit = pack_unit
                prod.is_jan_aushadhi = True
                prod.updated_at = now
                p_updated += 1
            else:
                prod = MedicineProduct(
                    brand_name=brand_name,
                    generic_name=generic_name,
                    manufacturer_name="PMBI Jan Aushadhi",
                    dosage_form=d_form,
                    administration_route=a_route,
                    release_type=r_type,
                    pack_size=pack_size,
                    pack_unit=pack_unit,
                    prescription_status=rx_status,
                    is_jan_aushadhi=True,
                    pmbi_code=code,
                    therapeutic_group=group_raw,
                    source_id=src_jan.id,
                    created_at=now,
                    updated_at=now,
                )
                db.add(prod)
                db.flush()
                p_created += 1

                # Parse ingredients
                parsed_ings = DataIngestionService.parse_ingredients_field(raw_name)
                seen_norm_ings = set()
                for ing in parsed_ings:
                    disp, norm = DataIngestionService.normalize_ingredient_name(ing["name"])
                    if not norm or norm in seen_norm_ings:
                        continue
                    seen_norm_ings.add(norm)

                    act = db.query(ActiveIngredient).filter(ActiveIngredient.normalized_name == norm).first()
                    if not act:
                        act = ActiveIngredient(normalized_name=norm, display_name=disp)
                        db.add(act)
                        db.flush()

                    pi = ProductIngredient(
                        product_id=prod.id,
                        ingredient_id=act.id,
                        strength_value=ing["strength_value"],
                        strength_unit=ing["strength_unit"],
                    )
                    db.add(pi)

            # Price record
            if price_val is not None and price_val > 0:
                ex_price = db.query(MedicinePrice).filter(
                    MedicinePrice.product_id == prod.id,
                    MedicinePrice.price_type == "government_listed_price"
                ).first()
                if ex_price:
                    ex_price.amount_inr = price_val
                    ex_price.verified_at = now
                    ex_price.verification_status = "verified"
                else:
                    db.add(MedicinePrice(
                        product_id=prod.id,
                        amount_inr=price_val,
                        price_type="government_listed_price",
                        pack_quantity=pack_size,
                        unit_of_measure=pack_unit,
                        source_id=src_jan.id,
                        source_url=source_url,
                        verified_at=now,
                        verification_status="verified",
                    ))
            elif "under process" in status_raw.lower() or "pending" in status_raw.lower() or price_val is None:
                # Mark as under_process
                ex_price = db.query(MedicinePrice).filter(MedicinePrice.product_id == prod.id).first()
                if not ex_price:
                    db.add(MedicinePrice(
                        product_id=prod.id,
                        amount_inr=None,
                        price_type="government_listed_price",
                        pack_quantity=pack_size,
                        unit_of_measure=pack_unit,
                        source_id=src_jan.id,
                        source_url=source_url,
                        verified_at=now,
                        verification_status="under_process",
                    ))

        src_jan.last_checked_at = now
        src_jan.last_successful_sync_at = now
        db.commit()
        print(f"   -> PMBI Master Basket: {p_created} created, {p_updated} updated.")
        print("Data integration completed successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    ingest_all_master_data()
