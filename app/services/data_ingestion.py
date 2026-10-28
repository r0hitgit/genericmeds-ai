import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.source import DataSource
from app.models.ingredient import ActiveIngredient, ProductIngredient
from app.models.medicine import MedicineProduct
from app.models.pricing import MedicinePrice
from app.schemas.source import AdminImportReport
from app.services.source_verification import SourceVerificationService


class DataIngestionService:
    @staticmethod
    def normalize_ingredient_name(name: str) -> Tuple[str, str]:
        """
        Normalizes ingredient name for indexing and matching.
        Returns (display_name, normalized_name).
        """
        clean = name.strip()
        # Remove trailing salts or common qualifiers if needed, or normalize formatting
        display = clean.title()
        normalized = clean.lower()
        return display, normalized

    @staticmethod
    def parse_ingredients_field(composition_text: str) -> List[Dict[str, Any]]:
        """
        Parses complex composition strings like:
        'Amoxicillin (500mg) + Clavulanic Acid (125mg)' or 'Paracetamol 650 mg'
        or 'Metformin Hydrochloride 500mg + Glimepiride 2mg'
        """
        results = []
        if not composition_text or not isinstance(composition_text, str):
            return results

        # Split on +, /, or comma
        parts = re.split(r"\s*\+\s*|\s*/\s*|,\s*", composition_text.strip())
        pattern = re.compile(
            r"^(?P<name>[A-Za-z0-9\s\.\(\)\-]+?)\s*(?:\(?\s*(?P<val>[0-9]+(?:\.[0-9]+)?)\s*(?P<unit>mg|g|mcg|ml|iu|%|w/w|w/v|v/v)\s*\)?)?$",
            re.IGNORECASE,
        )

        for p in parts:
            p = p.strip()
            if not p:
                continue

            match = pattern.search(p)
            if match and match.group("val"):
                name = match.group("name").strip(" ()")
                val = float(match.group("val"))
                unit = match.group("unit").strip().lower()
                results.append({
                    "name": name,
                    "strength_value": val,
                    "strength_unit": unit,
                })
            else:
                # If no numeric strength found inside part, treat as 0 or require explicit column
                results.append({
                    "name": p.strip(" ()"),
                    "strength_value": 0.0,
                    "strength_unit": "mg",
                })
        return results

    @classmethod
    def ingest_catalog_dataframe(
        cls, db: Session, df: pd.DataFrame, source_name: str, source_url: Optional[str] = None
    ) -> AdminImportReport:
        """
        Validates and ingests a catalog dataframe.
        Expected columns (or flexible mappings):
        - brand_name
        - generic_name
        - dosage_form (e.g. Tablet, Capsule, Syrup)
        - administration_route (optional, default Oral)
        - release_type (optional, default immediate-release)
        - pack_size (e.g. 10)
        - pack_unit (e.g. tablets)
        - price_inr (e.g. 24.50)
        - price_type (e.g. MRP, government_listed_price)
        - manufacturer (optional)
        - is_jan_aushadhi (optional boolean)
        - composition (or ingredient_1_name, ingredient_1_strength, etc.)
        """
        SourceVerificationService.ensure_default_sources(db)
        src = db.query(DataSource).filter(DataSource.source_name == source_name).first()
        if not src:
            src = DataSource(
                source_name=source_name,
                source_url=source_url or "https://genericmeds.gov.in",
                source_type="catalog_import",
                data_status="active",
                last_checked_at=datetime.now(timezone.utc),
                last_successful_sync_at=datetime.now(timezone.utc),
            )
            db.add(src)
            db.flush()

        records_processed = 0
        records_created = 0
        records_updated = 0
        validation_errors: List[str] = []

        now = datetime.now(timezone.utc)

        # Map column names to standard lowercased
        col_map = {str(c).strip().lower(): c for c in df.columns}

        def get_val(row, *aliases, default=None):
            for a in aliases:
                if a in col_map:
                    v = row[col_map[a]]
                    if pd.notna(v):
                        return v
            return default

        for idx, row in df.iterrows():
            row_idx = idx + 1
            records_processed += 1

            brand_name = get_val(row, "brand_name", "brand", "product_name", "medicine_name")
            generic_name = get_val(row, "generic_name", "generic", "salt_name", "formulation")
            dosage_form = get_val(row, "dosage_form", "form", "type", default="Tablet")
            administration_route = get_val(row, "administration_route", "route", default="Oral")
            release_type = get_val(row, "release_type", "release", default="immediate-release")
            pack_size_raw = get_val(row, "pack_size", "pack", "quantity", default=10)
            pack_unit = get_val(row, "pack_unit", "unit", default="tablets")
            price_raw = get_val(row, "price_inr", "price", "mrp", "cost", default=None)
            price_type = get_val(row, "price_type", "type_of_price", default="MRP")
            manufacturer = get_val(row, "manufacturer", "manufacturer_name", "company", default=None)
            is_jan_aushadhi_raw = get_val(row, "is_jan_aushadhi", "jan_aushadhi", "pmbjp", default=False)
            composition_str = get_val(row, "composition", "active_ingredients", "ingredients", default="")

            # 1. Validation checks
            if not brand_name or not str(brand_name).strip():
                validation_errors.append(f"Row {row_idx}: Missing brand/product name.")
                continue

            if not generic_name or not str(generic_name).strip():
                validation_errors.append(f"Row {row_idx}: Missing generic name.")
                continue

            try:
                pack_size = float(pack_size_raw)
                if pack_size <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                validation_errors.append(f"Row {row_idx}: Invalid pack size '{pack_size_raw}'. Must be > 0.")
                continue

            price_inr = None
            if price_raw is not None:
                try:
                    price_inr = float(price_raw)
                    if price_inr <= 0:
                        validation_errors.append(f"Row {row_idx}: Price must be positive, got {price_raw}.")
                        continue
                except (ValueError, TypeError):
                    validation_errors.append(f"Row {row_idx}: Malformed price '{price_raw}'.")
                    continue

            is_jan_aushadhi = False
            if isinstance(is_jan_aushadhi_raw, bool):
                is_jan_aushadhi = is_jan_aushadhi_raw
            elif str(is_jan_aushadhi_raw).strip().lower() in ("true", "1", "yes", "y"):
                is_jan_aushadhi = True

            # Parse ingredients
            parsed_ings = cls.parse_ingredients_field(str(composition_str))
            if not parsed_ings:
                # If no composition column, try extracting from generic name
                parsed_ings = cls.parse_ingredients_field(str(generic_name))

            if not parsed_ings:
                validation_errors.append(f"Row {row_idx}: No active ingredients could be parsed.")
                continue

            # Check duplicate / existing product
            brand_str = str(brand_name).strip()
            generic_str = str(generic_name).strip()
            form_str = str(dosage_form).strip().title()

            existing_prod = db.query(MedicineProduct).filter(
                func.lower(MedicineProduct.brand_name) == brand_str.lower(),
                func.lower(MedicineProduct.dosage_form) == form_str.lower(),
                MedicineProduct.pack_size == pack_size,
            ).first()

            if existing_prod:
                # Update existing record
                existing_prod.generic_name = generic_str
                existing_prod.manufacturer_name = str(manufacturer).strip() if manufacturer else existing_prod.manufacturer_name
                existing_prod.is_jan_aushadhi = is_jan_aushadhi
                existing_prod.updated_at = now
                prod = existing_prod
                records_updated += 1
            else:
                # Create product
                prod = MedicineProduct(
                    brand_name=brand_str,
                    generic_name=generic_str,
                    manufacturer_name=str(manufacturer).strip() if manufacturer else None,
                    dosage_form=form_str,
                    administration_route=str(administration_route).strip().title(),
                    release_type=str(release_type).strip().lower(),
                    pack_size=pack_size,
                    pack_unit=str(pack_unit).strip().lower(),
                    prescription_status=str(get_val(row, "prescription_status", default="Schedule H")),
                    is_jan_aushadhi=is_jan_aushadhi,
                    source_id=src.id,
                    created_at=now,
                    updated_at=now,
                )
                db.add(prod)
                db.flush()
                records_created += 1

                # Add ingredients
                for ing_data in parsed_ings:
                    disp_name, norm_name = cls.normalize_ingredient_name(ing_data["name"])
                    act_ing = db.query(ActiveIngredient).filter(ActiveIngredient.normalized_name == norm_name).first()
                    if not act_ing:
                        act_ing = ActiveIngredient(
                            normalized_name=norm_name,
                            display_name=disp_name,
                        )
                        db.add(act_ing)
                        db.flush()

                    pi = ProductIngredient(
                        product_id=prod.id,
                        ingredient_id=act_ing.id,
                        strength_value=ing_data["strength_value"],
                        strength_unit=ing_data["strength_unit"],
                    )
                    db.add(pi)

            # Ingest price if provided
            if price_inr is not None:
                # Check latest price to avoid duplicate identical dated price
                existing_price = db.query(MedicinePrice).filter(
                    MedicinePrice.product_id == prod.id,
                    MedicinePrice.price_type == str(price_type).strip(),
                    MedicinePrice.amount_inr == price_inr,
                ).first()

                if not existing_price:
                    new_price = MedicinePrice(
                        product_id=prod.id,
                        amount_inr=price_inr,
                        price_type=str(price_type).strip(),
                        pack_quantity=pack_size,
                        unit_of_measure=str(pack_unit).strip().lower(),
                        source_id=src.id,
                        source_url=source_url or src.source_url,
                        effective_date=now,
                        verified_at=now,
                        verification_status="verified",
                    )
                    db.add(new_price)

        src.last_checked_at = now
        src.last_successful_sync_at = now
        db.commit()

        status = "success"
        if validation_errors and records_created == 0 and records_updated == 0:
            status = "failed"
        elif validation_errors:
            status = "partial_success"

        return AdminImportReport(
            source_name=source_name,
            source_url=source_url,
            records_processed=records_processed,
            records_created=records_created,
            records_updated=records_updated,
            validation_errors=validation_errors,
            status=status,
        )
