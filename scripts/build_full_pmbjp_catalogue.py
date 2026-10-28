#!/usr/bin/env python3
"""
Full parser and database loader for PMBJP Reconciled Master Catalogue,
Flagship Comparisons, and Hospital Jan Aushadhi Kendra Directory.
"""

import os
import sys
import re
import pandas as pd
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, init_db, engine
from app.models.source import DataSource
from app.models.ingredient import ActiveIngredient, ProductIngredient
from app.models.medicine import MedicineProduct
from app.models.pricing import MedicinePrice
from app.models.kendra import JanAushadhiKendra
from app.services.source_verification import SourceVerificationService
from app.services.data_ingestion import DataIngestionService
from scripts.process_all_pmbjp_data import clean_number, parse_pack_info, parse_dosage_form, parse_release_type, parse_prescription_status
from scripts.build_datasets import KENDRA_DATA, FLAGSHIP_COMPARISONS


def ingest_kendras(db):
    print("Ingesting Jan Aushadhi Kendra Directory...")
    created = 0
    updated = 0
    for k in KENDRA_DATA:
        existing = db.query(JanAushadhiKendra).filter(JanAushadhiKendra.kendra_code == k["kendra_code"]).first()
        if existing:
            existing.hospital_name = k["hospital_name"]
            existing.city_state = k["city_state"]
            existing.location = k["location"]
            existing.operating_hours = k["operating_hours"]
            existing.portfolio_scope = k["portfolio_scope"]
            existing.dispensing_rules = k["dispensing_rules"]
            existing.helpline_url = k["helpline_url"]
            existing.is_24x7 = k["is_24x7"]
            updated += 1
        else:
            new_k = JanAushadhiKendra(**k)
            db.add(new_k)
            created += 1
    db.commit()
    print(f"Kendra Hubs: Created {created}, Updated {updated}.")


def ingest_flagship_branded_references(db, src_market):
    print("Ingesting 39 Flagship Branded Market References...")
    now = datetime.now(timezone.utc)
    created = 0
    for item in FLAGSHIP_COMPARISONS:
        brand_name = item["brand_ref"].split("/")[0].strip()
        generic_name = item["name"]
        pack_size, pack_unit = parse_pack_info(item["pack"])
        form, route = parse_dosage_form(generic_name, item["category"])
        release = parse_release_type(generic_name)
        rx_status = parse_prescription_status(item["category"], generic_name)

        existing = db.query(MedicineProduct).filter(
            MedicineProduct.brand_name.ilike(brand_name),
            MedicineProduct.is_jan_aushadhi == False,
        ).first()

        if not existing:
            prod = MedicineProduct(
                brand_name=brand_name,
                generic_name=generic_name,
                manufacturer_name="Market Branded Manufacturer",
                dosage_form=form,
                administration_route=route,
                release_type=release,
                pack_size=pack_size,
                pack_unit=pack_unit,
                prescription_status=rx_status,
                is_jan_aushadhi=False,
                therapeutic_group=item["category"],
                source_id=src_market.id,
                created_at=now,
                updated_at=now,
            )
            db.add(prod)
            db.flush()

            # Ingredients
            parsed_ings = DataIngestionService.parse_ingredients_field(generic_name)
            for ing in parsed_ings:
                disp, norm = DataIngestionService.normalize_ingredient_name(ing["name"])
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

            # Branded MRP
            price = MedicinePrice(
                product_id=prod.id,
                amount_inr=item["market_price"],
                price_type="MRP",
                pack_quantity=pack_size,
                unit_of_measure=pack_unit,
                source_id=src_market.id,
                source_url="https://nppaipdms.gov.in/NPPA/PharmaSahiDaam/searchMedicine",
                verified_at=now,
                verification_status="verified",
            )
            db.add(price)
            created += 1

    db.commit()
    print(f"Flagship Branded Products: Created {created}.")
