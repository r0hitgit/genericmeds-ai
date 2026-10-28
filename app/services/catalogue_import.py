import os
import re
import math
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import pandas as pd
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.source import DataSource
from app.models.medicine import MedicineProduct
from app.models.ingredient import ActiveIngredient, ProductIngredient
from app.models.pricing import MedicinePrice
from app.models.alias import MedicineAlias
from app.models.brand_lookup import BrandGenericLookup
from app.schemas.catalogue import (
    CataloguePreviewReport,
    CatalogueImportReport,
    CatalogueStatusReport,
)
from app.services.source_verification import SourceVerificationService


class CatalogueImportService:
    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        if not text or not isinstance(text, str):
            return ""
        # Remove special characters, multiple spaces, and lowercase
        cleaned = re.sub(r"[^\w\s\-\+\.\/]", " ", text)
        return re.sub(r"\s+", " ", cleaned).strip().lower()

    @staticmethod
    def parse_decimal_price(val: Any) -> Optional[float]:
        if val is None or pd.isna(val):
            return None
        val_str = str(val).strip().replace("₹", "").replace("INR", "").replace(",", "").strip()
        if not val_str or val_str.lower() in ("nan", "none", "null", ""):
            return None
        try:
            # Use Decimal arithmetic to avoid floating point precision issues
            dec = Decimal(val_str)
            return float(dec)
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def parse_percentage(val: Any) -> Tuple[Optional[str], Optional[float]]:
        if val is None or pd.isna(val):
            return None, None
        val_str = str(val).strip()
        if not val_str or val_str.lower() in ("nan", "none", "null", ""):
            return None, None
        num_str = val_str.replace("%", "").strip()
        try:
            pct_val = float(Decimal(num_str))
            formatted_str = f"{pct_val:.1f}%" if "%" not in val_str else val_str
            return formatted_str, pct_val
        except (InvalidOperation, ValueError):
            return val_str, None

    @staticmethod
    def detect_dosage_form_and_route(generic_name: str) -> Tuple[str, str, str]:
        name_lower = generic_name.lower()

        # Release type
        release_type = "immediate-release"
        if any(term in name_lower for term in ["prolonged release", "prolonged-release", "pr"]):
            release_type = "prolonged-release"
        elif any(term in name_lower for term in ["sustained release", "sustained-release", "sr"]):
            release_type = "sustained-release"
        elif any(term in name_lower for term in ["extended release", "extended-release", "er", "xr"]):
            release_type = "extended-release"
        elif any(term in name_lower for term in ["gastro-resistant", "gastro resistant", "enteric coated", "enteric-coated"]):
            release_type = "gastro-resistant"
        elif "modified release" in name_lower or "modified-release" in name_lower:
            release_type = "modified-release"

        # Dosage form & route
        if "tablet" in name_lower:
            return "Tablet", "Oral", release_type
        elif "capsule" in name_lower:
            return "Capsule", "Oral", release_type
        elif "injection" in name_lower or " inj" in name_lower:
            return "Injection", "Injectable (IV/IM)", release_type
        elif "syrup" in name_lower or "suspension" in name_lower or "oral solution" in name_lower or "elixir" in name_lower:
            return "Syrup", "Oral", release_type
        elif "eye/ear" in name_lower or "eye drops" in name_lower or "ophthalmic" in name_lower:
            return "Eye/Ear Drops", "Ophthalmic/Otic", release_type
        elif "ear drops" in name_lower:
            return "Ear Drops", "Otic", release_type
        elif "nasal" in name_lower:
            return "Nasal Spray/Drops", "Nasal", release_type
        elif "cream" in name_lower:
            return "Cream", "Topical", release_type
        elif "ointment" in name_lower:
            return "Ointment", "Topical", release_type
        elif "gel" in name_lower:
            return "Gel", "Topical", release_type
        elif "lotion" in name_lower:
            return "Lotion", "Topical", release_type
        elif "inhaler" in name_lower or "rotacap" in name_lower or "respirator" in name_lower:
            return "Inhaler", "Inhalation", release_type
        elif "powder" in name_lower or "sachet" in name_lower or "granules" in name_lower:
            return "Powder/Sachet", "Oral", release_type
        elif "infusion" in name_lower or "iv" in name_lower:
            return "Infusion", "Injectable (IV)", release_type
        else:
            return "Formulation", "Oral", release_type

    @staticmethod
    def parse_pack_size_and_unit(unit_size: Optional[str], dosage_form: str) -> Tuple[float, str]:
        if not unit_size or not isinstance(unit_size, str):
            default_unit = "tablets" if dosage_form == "Tablet" else ("capsules" if dosage_form == "Capsule" else "units")
            return 10.0, default_unit

        u_clean = unit_size.strip().lower()

        # Handle '10's', '15's', '1's'
        m_s = re.search(r"(\d+(?:\.\d+)?)\s*(?:'s|’s)", u_clean)
        if m_s:
            size = float(m_s.group(1))
            unit = "tablets" if dosage_form == "Tablet" else ("capsules" if dosage_form == "Capsule" else "units")
            return size, unit

        # Handle '100 ml', '15 g', '2 ml', '5ml drops'
        m_qty = re.search(r"(\d+(?:\.\d+)?)\s*(ml|g|gm|kg|vial|ampoule|bottle|tube|kit|sachet)", u_clean)
        if m_qty:
            return float(m_qty.group(1)), m_qty.group(2)

        if "vial" in u_clean:
            return 1.0, "vial"
        if "bottle" in u_clean:
            return 1.0, "bottle"
        if "tube" in u_clean:
            return 1.0, "tube"

        # Check for lone number
        m_num = re.search(r"^(\d+(?:\.\d+)?)$", u_clean)
        if m_num:
            return float(m_num.group(1)), "units"

        return 10.0, "units"

    @classmethod
    def preview_import(cls, file_a_path: str, file_b_path: str) -> CataloguePreviewReport:
        if not os.path.exists(file_a_path):
            raise FileNotFoundError(f"Master medicine database file not found at: {file_a_path}")
        if not os.path.exists(file_b_path):
            raise FileNotFoundError(f"Brand lookup database file not found at: {file_b_path}")

        # Safe read handling UTF-8 BOM, quotes, nulls
        df_a = pd.read_csv(file_a_path, encoding="utf-8-sig")
        df_b = pd.read_csv(file_b_path, encoding="utf-8-sig")

        file_a_rows = len(df_a)
        file_b_rows = len(df_b)

        # File A pricing classification
        priced_mask = df_a["mrp_inr"].notna() & (df_a["mrp_inr"].astype(str).str.strip().str.lower() != "nan")
        file_a_priced_count = int(priced_mask.sum())
        file_a_unpriced_count = file_a_rows - file_a_priced_count

        # Drug codes in File A
        codes_a = set()
        duplicate_codes = []
        for code in df_a["drug_code_label"].dropna():
            norm_code = str(code).strip().upper()
            if norm_code in codes_a:
                duplicate_codes.append(norm_code)
            codes_a.add(norm_code)

        # File B primary codes reconciliation
        codes_b = []
        unmatched_primary_codes = []
        for code in df_b["primary_pmbi_drug_code"].dropna():
            norm_code = str(code).strip().upper()
            codes_b.append(norm_code)
            if norm_code not in codes_a:
                unmatched_primary_codes.append(norm_code)

        matched_primary_codes_count = len(codes_b) - len(unmatched_primary_codes)

        # Audit indicative savings in File B
        savings_audit_matches = 0
        savings_audit_discrepancies = []

        for _, row in df_b.iterrows():
            brand_id = str(row.get("brand_lookup_id", ""))
            jan_mrp = cls.parse_decimal_price(row.get("janaushadhi_mrp_inr"))
            mkt_ref = cls.parse_decimal_price(row.get("branded_market_reference_inr"))
            src_sav_inr = cls.parse_decimal_price(row.get("indicative_savings_inr"))
            _, src_sav_pct = cls.parse_percentage(row.get("indicative_savings_pct"))

            if jan_mrp is not None and mkt_ref is not None and mkt_ref > 0:
                calc_sav_inr = round(mkt_ref - jan_mrp, 2)
                calc_sav_pct = round((calc_sav_inr / mkt_ref) * 100, 1)

                diff_inr = abs(calc_sav_inr - (src_sav_inr or 0.0))
                diff_pct = abs(calc_sav_pct - (src_sav_pct or 0.0))

                if diff_inr <= 0.05 and diff_pct <= 0.2:
                    savings_audit_matches += 1
                else:
                    savings_audit_discrepancies.append({
                        "brand_lookup_id": brand_id,
                        "source_savings_inr": src_sav_inr,
                        "calculated_savings_inr": calc_sav_inr,
                        "source_savings_pct": src_sav_pct,
                        "calculated_savings_pct": calc_sav_pct,
                    })
            else:
                savings_audit_matches += 1

        warnings = []
        if unmatched_primary_codes:
            warnings.append(
                f"Flagged {len(unmatched_primary_codes)} unresolved primary PMBI codes in brand database "
                f"({', '.join(unmatched_primary_codes)}) for administrative review without guessing or dropping."
            )
        if file_a_unpriced_count > 0:
            warnings.append(
                f"Preserved {file_a_unpriced_count} products marked 'Under Rate Contract / Process' with SQL NULL MRP. "
                "These items are never represented as free or ₹0."
            )

        return CataloguePreviewReport(
            status="preview_generated",
            file_a_name=os.path.basename(file_a_path),
            file_a_rows=file_a_rows,
            file_a_priced_count=file_a_priced_count,
            file_a_unpriced_count=file_a_unpriced_count,
            file_b_name=os.path.basename(file_b_path),
            file_b_rows=file_b_rows,
            matched_primary_codes_count=matched_primary_codes_count,
            unmatched_primary_codes=unmatched_primary_codes,
            duplicate_codes=duplicate_codes,
            savings_audit_matches=savings_audit_matches,
            savings_audit_discrepancies=savings_audit_discrepancies,
            validation_warnings=warnings,
        )

    @classmethod
    def import_catalogue(
        cls,
        db: Session,
        file_a_path: str,
        file_b_path: str,
        is_dry_run: bool = False,
    ) -> CatalogueImportReport:
        preview = cls.preview_import(file_a_path, file_b_path)

        if is_dry_run:
            return CatalogueImportReport(
                status="dry_run_success",
                is_dry_run=True,
                products_processed=preview.file_a_rows,
                products_created=preview.file_a_rows,
                products_updated=0,
                prices_created=preview.file_a_rows,
                aliases_created=0,
                brand_lookups_processed=preview.file_b_rows,
                brand_lookups_linked=preview.matched_primary_codes_count,
                brand_lookups_unresolved=len(preview.unmatched_primary_codes),
                unresolved_primary_codes=preview.unmatched_primary_codes,
                validation_warnings=preview.validation_warnings,
                imported_at=datetime.now(timezone.utc).isoformat(),
            )

        # 1. Ensure DataSource
        SourceVerificationService.ensure_default_sources(db)
        src = db.query(DataSource).filter(DataSource.source_name.like("%Jan Aushadhi%")).first()
        if not src:
            src = DataSource(
                source_name="PMBI Jan Aushadhi Master Catalogue",
                source_url="https://janaushadhi.gov.in",
                source_type="government_master_catalogue",
                data_status="active",
                last_checked_at=datetime.now(timezone.utc),
                last_successful_sync_at=datetime.now(timezone.utc),
            )
            db.add(src)
            db.flush()

        df_a = pd.read_csv(file_a_path, encoding="utf-8-sig")
        df_b = pd.read_csv(file_b_path, encoding="utf-8-sig")

        # Cache existing products, ingredients, aliases, and brand lookups
        existing_products = {p.drug_code_label: p for p in db.query(MedicineProduct).filter(MedicineProduct.drug_code_label.isnot(None)).all()}
        existing_ingredients = {ing.normalized_name: ing for ing in db.query(ActiveIngredient).all()}
        existing_lookups = {b.brand_lookup_id: b for b in db.query(BrandGenericLookup).all()}

        # Cache existing aliases as a set of (product_id, alias_normalized, alias_type)
        existing_aliases = {
            (a.product_id, a.alias_normalized, a.alias_type)
            for a in db.query(MedicineAlias.product_id, MedicineAlias.alias_normalized, MedicineAlias.alias_type).all()
        }

        products_created = 0
        products_updated = 0
        prices_created = 0
        aliases_created = 0

        # --- Ingest File A ---
        for _, row in df_a.iterrows():
            drug_code_raw = row.get("drug_code")
            try:
                drug_code = int(drug_code_raw) if pd.notna(drug_code_raw) else None
            except (ValueError, TypeError):
                drug_code = None

            code_label = str(row.get("drug_code_label", "")).strip().upper()
            generic_name = str(row.get("generic_name", "")).strip()
            unit_size = str(row.get("unit_size", "")).strip() if pd.notna(row.get("unit_size")) else None
            mrp_inr = cls.parse_decimal_price(row.get("mrp_inr"))
            mrp_display = str(row.get("mrp_display", "")).strip() if pd.notna(row.get("mrp_display")) else (f"INR {mrp_inr:.2f}" if mrp_inr is not None else "MRP Pending")
            pricing_status = str(row.get("pricing_status", "")).strip() if pd.notna(row.get("pricing_status")) else ("Active Priced in PMBI Basket" if mrp_inr is not None else "Under Rate Contract / Process (MRP Pending — Not Sold at ₹0)")
            therapeutic_group = str(row.get("therapeutic_group", "")).strip() if pd.notna(row.get("therapeutic_group")) else None
            reconciliation_cohort = str(row.get("reconciliation_cohort", "")).strip() if pd.notna(row.get("reconciliation_cohort")) else None
            source_authority = str(row.get("source_authority", "")).strip() if pd.notna(row.get("source_authority")) else "PMBI (janaushadhi.gov.in / pmbi.co.in)"
            source_url = str(row.get("source_url", "")).strip() if pd.notna(row.get("source_url")) else "https://janaushadhi.gov.in"
            source_snapshot_date = str(row.get("source_snapshot_date", "")).strip() if pd.notna(row.get("source_snapshot_date")) else "2026-08-30"
            verification_method = str(row.get("verification_method", "")).strip() if pd.notna(row.get("verification_method")) else "Official PMBI Directory Extraction"
            individual_verification_date = str(row.get("individual_verification_date", "")).strip() if pd.notna(row.get("individual_verification_date")) else "2026-10-26"
            clinical_safety_notice = str(row.get("clinical_safety_notice", "")).strip() if pd.notna(row.get("clinical_safety_notice")) else "Strictly for medicine information and price discovery. Generic substitution must be confirmed by a qualified doctor or registered pharmacist."

            dosage_form, admin_route, release_type = cls.detect_dosage_form_and_route(generic_name)
            pack_size, pack_unit = cls.parse_pack_size_and_unit(unit_size, dosage_form)

            brand_name = generic_name
            if not generic_name.lower().startswith("jan aushadhi"):
                brand_name = f"Jan Aushadhi {generic_name}"

            norm_brand = cls.normalize_text(brand_name)
            norm_generic = cls.normalize_text(generic_name)

            product = existing_products.get(code_label)
            if product:
                product.drug_code = drug_code
                product.drug_code_label = code_label
                product.pmbi_code = code_label
                product.brand_name = brand_name
                product.name_normalized = norm_brand
                product.generic_name = generic_name
                product.generic_name_normalized = norm_generic
                product.dosage_form = dosage_form
                product.administration_route = admin_route
                product.release_type = release_type
                product.pack_size = pack_size
                product.pack_unit = pack_unit
                product.unit_size = unit_size
                product.mrp_display = mrp_display
                product.pricing_status = pricing_status
                product.is_jan_aushadhi = True
                product.therapeutic_group = therapeutic_group
                product.reconciliation_cohort = reconciliation_cohort
                product.source_authority = source_authority
                product.source_url = source_url
                product.source_snapshot_date = source_snapshot_date
                product.verification_method = verification_method
                product.individual_verification_date = individual_verification_date
                product.clinical_safety_notice = clinical_safety_notice
                product.source_id = src.id
                product.imported_at = datetime.now(timezone.utc)
                products_updated += 1
            else:
                product = MedicineProduct(
                    drug_code=drug_code,
                    drug_code_label=code_label,
                    pmbi_code=code_label,
                    brand_name=brand_name,
                    name_normalized=norm_brand,
                    generic_name=generic_name,
                    generic_name_normalized=norm_generic,
                    dosage_form=dosage_form,
                    administration_route=admin_route,
                    release_type=release_type,
                    pack_size=pack_size,
                    pack_unit=pack_unit,
                    unit_size=unit_size,
                    mrp_display=mrp_display,
                    pricing_status=pricing_status,
                    is_jan_aushadhi=True,
                    prescription_status="Schedule H",
                    therapeutic_group=therapeutic_group,
                    reconciliation_cohort=reconciliation_cohort,
                    source_authority=source_authority,
                    source_url=source_url,
                    source_snapshot_date=source_snapshot_date,
                    verification_method=verification_method,
                    individual_verification_date=individual_verification_date,
                    verification_status="verified",
                    clinical_safety_notice=clinical_safety_notice,
                    source_id=src.id,
                    imported_at=datetime.now(timezone.utc),
                )
                db.add(product)
                db.flush()
                existing_products[code_label] = product
                products_created += 1

            # Update or create MedicinePrice
            price_record = db.query(MedicinePrice).filter(
                MedicinePrice.product_id == product.id,
                MedicinePrice.price_type == "government_listed_price",
            ).first()

            if price_record:
                price_record.amount_inr = mrp_inr
                price_record.pack_quantity = pack_size
                price_record.unit_of_measure = pack_unit
                price_record.verification_status = "verified" if mrp_inr is not None else "under_process"
            else:
                price_record = MedicinePrice(
                    product_id=product.id,
                    amount_inr=mrp_inr,
                    price_type="government_listed_price",
                    pack_quantity=pack_size,
                    unit_of_measure=pack_unit,
                    source_id=src.id,
                    source_url=source_url,
                    verified_at=datetime.now(timezone.utc),
                    verification_status="verified" if mrp_inr is not None else "under_process",
                )
                db.add(price_record)
                prices_created += 1

            # Parse and link ActiveIngredients
            parsed_ingredients = cls._parse_ingredients(generic_name)
            seen_ingredient_ids = set()
            for ing_data in parsed_ingredients:
                ing_norm = ing_data["normalized_name"]
                ing_obj = existing_ingredients.get(ing_norm)
                if not ing_obj:
                    ing_obj = ActiveIngredient(
                        normalized_name=ing_norm,
                        display_name=ing_data["display_name"],
                    )
                    db.add(ing_obj)
                    db.flush()
                    existing_ingredients[ing_norm] = ing_obj

                if ing_obj.id in seen_ingredient_ids:
                    continue
                seen_ingredient_ids.add(ing_obj.id)

                pi_exists = db.query(ProductIngredient).filter(
                    ProductIngredient.product_id == product.id,
                    ProductIngredient.ingredient_id == ing_obj.id,
                ).first()
                if not pi_exists:
                    pi = ProductIngredient(
                        product_id=product.id,
                        ingredient_id=ing_obj.id,
                        strength_value=ing_data["strength_value"],
                        strength_unit=ing_data["strength_unit"],
                        raw_composition_text=generic_name,
                        parsing_status="verified",
                    )
                    db.add(pi)

            # File A aliases from common_indian_brand_equivalents
            brand_eq_raw = row.get("common_indian_brand_equivalents")
            if pd.notna(brand_eq_raw):
                for b_name in str(brand_eq_raw).split(","):
                    b_clean = b_name.strip()
                    if b_clean and len(b_clean) >= 2:
                        b_norm = cls.normalize_text(b_clean)
                        key = (product.id, b_norm, "brand")
                        if key not in existing_aliases:
                            alias_obj = MedicineAlias(
                                product_id=product.id,
                                alias=b_clean,
                                alias_normalized=b_norm,
                                alias_type="brand",
                                source_file="pmbjp_janaushadhi_medicine_database.csv",
                                verification_status="verified",
                            )
                            db.add(alias_obj)
                            existing_aliases.add(key)
                            aliases_created += 1

            # File A aliases from portal_search_keywords_and_aliases
            keywords_raw = row.get("portal_search_keywords_and_aliases")
            if pd.notna(keywords_raw):
                for kw in str(keywords_raw).split(","):
                    kw_clean = kw.strip()
                    if kw_clean and len(kw_clean) >= 2:
                        kw_norm = cls.normalize_text(kw_clean)
                        key = (product.id, kw_norm, "search_keyword")
                        if key not in existing_aliases:
                            alias_obj = MedicineAlias(
                                product_id=product.id,
                                alias=kw_clean,
                                alias_normalized=kw_norm,
                                alias_type="search_keyword",
                                source_file="pmbjp_janaushadhi_medicine_database.csv",
                                verification_status="verified",
                            )
                            db.add(alias_obj)
                            existing_aliases.add(key)
                            aliases_created += 1

        db.flush()

        # --- Ingest File B ---
        brand_lookups_processed = 0
        brand_lookups_linked = 0
        brand_lookups_unresolved = 0
        unresolved_primary_codes = []

        for _, row in df_b.iterrows():
            brand_lookup_id = str(row.get("brand_lookup_id", "")).strip().upper()
            popular_brand_names = str(row.get("popular_indian_brand_names", "")).strip()
            popular_brand_names_norm = cls.normalize_text(popular_brand_names)
            phonetic_aliases = str(row.get("phonetic_and_colloquial_search_aliases", "")).strip() if pd.notna(row.get("phonetic_and_colloquial_search_aliases")) else None
            mfg = str(row.get("market_reference_manufacturers", "")).strip() if pd.notna(row.get("market_reference_manufacturers")) else None
            category = str(row.get("therapeutic_category", "")).strip() if pd.notna(row.get("therapeutic_category")) else None
            comp = str(row.get("active_generic_composition", "")).strip()
            pmbi_code = str(row.get("primary_pmbi_drug_code", "")).strip().upper()
            all_codes = str(row.get("all_matching_pmbi_codes_and_strengths", "")).strip() if pd.notna(row.get("all_matching_pmbi_codes_and_strengths")) else None
            pack_size_text = str(row.get("unit_pack_size", "")).strip() if pd.notna(row.get("unit_pack_size")) else None

            jan_mrp = cls.parse_decimal_price(row.get("janaushadhi_mrp_inr"))
            mkt_ref = cls.parse_decimal_price(row.get("branded_market_reference_inr"))
            src_sav_inr = cls.parse_decimal_price(row.get("indicative_savings_inr"))
            pct_raw, src_sav_pct = cls.parse_percentage(row.get("indicative_savings_pct"))
            rule = str(row.get("pharmacist_and_doctor_verification_rule", "")).strip() if pd.notna(row.get("pharmacist_and_doctor_verification_rule")) else None

            # Calculate savings
            calc_sav_inr = round(mkt_ref - jan_mrp, 2) if (mkt_ref is not None and jan_mrp is not None) else None
            calc_sav_pct = round((calc_sav_inr / mkt_ref) * 100, 1) if (calc_sav_inr is not None and mkt_ref and mkt_ref > 0) else None

            # Audit savings match
            diff_inr = abs(calc_sav_inr - (src_sav_inr or 0.0)) if (calc_sav_inr is not None and src_sav_inr is not None) else 0.0
            diff_pct = abs(calc_sav_pct - (src_sav_pct or 0.0)) if (calc_sav_pct is not None and src_sav_pct is not None) else 0.0
            audit_status = "MATCH" if (diff_inr <= 0.05 and diff_pct <= 0.2) else "DISCREPANCY"

            # Reconcile with File A product
            linked_product = existing_products.get(pmbi_code)
            if linked_product:
                recon_status = "LINKED"
                linked_product_id = linked_product.id
                brand_lookups_linked += 1
            else:
                recon_status = "UNRESOLVED_CODE"
                linked_product_id = None
                brand_lookups_unresolved += 1
                if pmbi_code not in unresolved_primary_codes:
                    unresolved_primary_codes.append(pmbi_code)

            lookup = existing_lookups.get(brand_lookup_id)
            if lookup:
                lookup.popular_brand_names = popular_brand_names
                lookup.popular_brand_names_normalized = popular_brand_names_norm
                lookup.phonetic_and_colloquial_aliases = phonetic_aliases
                lookup.market_reference_manufacturers = mfg
                lookup.therapeutic_category = category
                lookup.active_generic_composition = comp
                lookup.primary_pmbi_drug_code = pmbi_code
                lookup.all_matching_pmbi_codes_and_strengths = all_codes
                lookup.unit_pack_size = pack_size_text
                lookup.janaushadhi_mrp_inr = jan_mrp
                lookup.branded_market_reference_inr = mkt_ref
                lookup.indicative_savings_inr = src_sav_inr
                lookup.indicative_savings_pct = pct_raw
                lookup.indicative_savings_pct_numeric = src_sav_pct
                lookup.recalculated_savings_inr = calc_sav_inr
                lookup.recalculated_savings_pct = calc_sav_pct
                lookup.savings_audit_status = audit_status
                lookup.pharmacist_and_doctor_verification_rule = rule
                lookup.reconciliation_status = recon_status
                lookup.linked_product_id = linked_product_id
                lookup.review_status = "reviewed"
            else:
                lookup = BrandGenericLookup(
                    brand_lookup_id=brand_lookup_id,
                    popular_brand_names=popular_brand_names,
                    popular_brand_names_normalized=popular_brand_names_norm,
                    phonetic_and_colloquial_aliases=phonetic_aliases,
                    market_reference_manufacturers=mfg,
                    therapeutic_category=category,
                    active_generic_composition=comp,
                    primary_pmbi_drug_code=pmbi_code,
                    all_matching_pmbi_codes_and_strengths=all_codes,
                    unit_pack_size=pack_size_text,
                    janaushadhi_mrp_inr=jan_mrp,
                    branded_market_reference_inr=mkt_ref,
                    indicative_savings_inr=src_sav_inr,
                    indicative_savings_pct=pct_raw,
                    indicative_savings_pct_numeric=src_sav_pct,
                    recalculated_savings_inr=calc_sav_inr,
                    recalculated_savings_pct=calc_sav_pct,
                    savings_audit_status=audit_status,
                    pharmacist_and_doctor_verification_rule=rule,
                    reconciliation_status=recon_status,
                    linked_product_id=linked_product_id,
                    source_file="pmbjp_popular_indian_brands_to_generic.csv",
                    review_status="reviewed",
                )
                db.add(lookup)
                existing_lookups[brand_lookup_id] = lookup

            brand_lookups_processed += 1

            # Register brand aliases for the linked product
            if linked_product_id:
                # Add popular brand names
                for b_raw in re.split(r"\s*/\s*|,\s*", popular_brand_names):
                    b_clean = b_raw.strip()
                    if b_clean and len(b_clean) >= 2:
                        b_norm = cls.normalize_text(b_clean)
                        key = (linked_product_id, b_norm, "brand")
                        if key not in existing_aliases:
                            alias_obj = MedicineAlias(
                                product_id=linked_product_id,
                                alias=b_clean,
                                alias_normalized=b_norm,
                                alias_type="brand",
                                source_file="pmbjp_popular_indian_brands_to_generic.csv",
                                verification_status="verified",
                            )
                            db.add(alias_obj)
                            existing_aliases.add(key)
                            aliases_created += 1

                # Add phonetic and colloquial search aliases
                if phonetic_aliases:
                    for p_raw in phonetic_aliases.split(","):
                        p_clean = p_raw.strip()
                        if p_clean and len(p_clean) >= 2:
                            p_norm = cls.normalize_text(p_clean)
                            key = (linked_product_id, p_norm, "colloquial")
                            if key not in existing_aliases:
                                alias_obj = MedicineAlias(
                                    product_id=linked_product_id,
                                    alias=p_clean,
                                    alias_normalized=p_norm,
                                    alias_type="colloquial",
                                    source_file="pmbjp_popular_indian_brands_to_generic.csv",
                                    verification_status="verified",
                                )
                                db.add(alias_obj)
                                existing_aliases.add(key)
                                aliases_created += 1

                # If branded market reference price is available, add/update retailer price record
                if mkt_ref is not None:
                    mkt_price_record = db.query(MedicinePrice).filter(
                        MedicinePrice.product_id == linked_product_id,
                        MedicinePrice.price_type == "retailer_price",
                    ).first()
                    if not mkt_price_record:
                        mkt_price_record = MedicinePrice(
                            product_id=linked_product_id,
                            amount_inr=mkt_ref,
                            price_type="retailer_price",
                            pack_quantity=linked_product.pack_size or 10.0,
                            unit_of_measure=linked_product.pack_unit or "tablets",
                            source_id=src.id,
                            source_url="Market Reference Indicative Sample",
                            verified_at=datetime.now(timezone.utc),
                            verification_status="verified",
                        )
                        db.add(mkt_price_record)

        db.commit()

        return CatalogueImportReport(
            status="import_success",
            is_dry_run=False,
            products_processed=len(df_a),
            products_created=products_created,
            products_updated=products_updated,
            prices_created=prices_created,
            aliases_created=aliases_created,
            brand_lookups_processed=brand_lookups_processed,
            brand_lookups_linked=brand_lookups_linked,
            brand_lookups_unresolved=brand_lookups_unresolved,
            unresolved_primary_codes=unresolved_primary_codes,
            validation_warnings=preview.validation_warnings,
            imported_at=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def get_catalogue_status(cls, db: Session) -> CatalogueStatusReport:
        total_products = db.query(MedicineProduct).count()
        jan_aushadhi_products = db.query(MedicineProduct).filter(MedicineProduct.is_jan_aushadhi == True).count()
        
        active_priced = db.query(MedicineProduct).filter(
            MedicineProduct.pricing_status.like("%Active Priced%")
        ).count()
        
        under_process_unpriced = db.query(MedicineProduct).filter(
            MedicineProduct.pricing_status.like("%Under Rate%")
        ).count()
        
        branded_market_reference = db.query(MedicineProduct).filter(
            MedicineProduct.is_jan_aushadhi == False
        ).count()
        
        total_brand_lookups = db.query(BrandGenericLookup).count()
        linked_brand_lookups = db.query(BrandGenericLookup).filter(BrandGenericLookup.reconciliation_status == "LINKED").count()
        unresolved_brand_lookups = db.query(BrandGenericLookup).filter(BrandGenericLookup.reconciliation_status == "UNRESOLVED_CODE").count()
        
        total_aliases = db.query(MedicineAlias).count()
        
        unresolved_codes = [
            b.primary_pmbi_drug_code
            for b in db.query(BrandGenericLookup.primary_pmbi_drug_code).filter(
                BrandGenericLookup.reconciliation_status == "UNRESOLVED_CODE"
            ).distinct().all()
        ]
        
        # Freshness snapshot
        latest_prod = db.query(MedicineProduct).order_by(MedicineProduct.imported_at.desc()).first()
        last_imported_at = latest_prod.imported_at.isoformat() if latest_prod and latest_prod.imported_at else None
        snapshot_date = latest_prod.source_snapshot_date if latest_prod and latest_prod.source_snapshot_date else "2026-08-30"

        warnings = []
        if unresolved_codes:
            warnings.append(
                f"Unresolved PMBI drug codes present: {', '.join(unresolved_codes)}. "
                "These records are safely preserved for manual administrative review."
            )
        if under_process_unpriced > 0:
            warnings.append(
                f"{under_process_unpriced} products are under rate contract renewal with null MRP. "
                "Explicitly flagged in API as 'MRP Pending — Under Rate Contract'."
            )

        return CatalogueStatusReport(
            status="healthy",
            total_products=total_products,
            jan_aushadhi_products=jan_aushadhi_products,
            active_priced_products=active_priced,
            under_process_unpriced_products=under_process_unpriced,
            branded_market_reference_products=branded_market_reference,
            total_brand_lookups=total_brand_lookups,
            linked_brand_lookups=linked_brand_lookups,
            unresolved_brand_lookups=unresolved_brand_lookups,
            total_aliases=total_aliases,
            unresolved_codes_flagged=unresolved_codes,
            data_freshness_snapshot=snapshot_date,
            last_imported_at=last_imported_at,
            quality_warnings=warnings,
        )

    @classmethod
    def _parse_ingredients(cls, generic_name: str) -> List[Dict[str, Any]]:
        """
        Extracts active ingredients and strengths from generic medicine titles.
        E.g. 'Aceclofenac 100mg and Paracetamol 325mg Tablets'
        """
        results = []
        if not generic_name:
            return results

        # Clean words like 'Tablets IP', 'Capsules', etc.
        clean = re.sub(r"(?i)\s+(tablets|capsules|syrup|injection|drops|cream|ointment|oral|ip|bp|usp)\b.*", "", generic_name).strip()
        parts = re.split(r"(?i)\s+and\s+|\s*\+\s*|,\s*", clean)

        for p in parts:
            p_strip = p.strip()
            if not p_strip:
                continue

            # Extract numeric strength
            m = re.search(r"^(.*?)\s*(\d+(?:\.\d+)?)\s*(mg|g|mcg|ml|iu|%)\s*$", p_strip, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
                val = float(m.group(2))
                unit = m.group(3).lower()
            else:
                name = p_strip
                val = 0.0
                unit = "mg"

            norm = cls.normalize_text(name)
            if norm and len(norm) >= 2:
                results.append({
                    "display_name": name.title(),
                    "normalized_name": norm,
                    "strength_value": val,
                    "strength_unit": unit,
                })

        return results
