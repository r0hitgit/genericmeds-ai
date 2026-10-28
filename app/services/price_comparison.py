from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session, joinedload
from app.models.medicine import MedicineProduct
from app.models.ingredient import ProductIngredient
from app.models.pricing import MedicinePrice
from app.schemas.pricing import (
    PriceComparisonRequest,
    PriceComparisonResponse,
    PriceComparisonItem,
    PriceComparisonDifference,
)
from app.core.config import settings
from app.services.safety_validation import SafetyValidationService


class PriceComparisonService:
    @classmethod
    def compare_prices(
        cls, db: Session, req: PriceComparisonRequest
    ) -> PriceComparisonResponse:
        products = db.query(MedicineProduct).options(
            joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
            joinedload(MedicineProduct.prices).joinedload(MedicinePrice.source),
            joinedload(MedicineProduct.source),
        ).filter(MedicineProduct.id.in_(req.product_ids)).all()

        if len(products) < 2:
            return PriceComparisonResponse(
                items=[],
                comparisons=[],
                summary_notes=["At least two valid products must be provided for comparison."],
                safety_disclaimer=SafetyValidationService.get_standard_disclaimer(),
            )

        # Identify reference product
        ref_prod = None
        if req.reference_product_id:
            ref_prod = next((p for p in products if p.id == req.reference_product_id), None)
        if not ref_prod:
            # Default to the first non-Jan-Aushadhi (branded reference) or simply the first product
            non_jan = [p for p in products if not p.is_jan_aushadhi]
            ref_prod = non_jan[0] if non_jan else products[0]

        now = datetime.now(timezone.utc)
        stale_threshold = timedelta(days=settings.PRICE_STALE_DAYS)

        items: List[PriceComparisonItem] = []
        for p in products:
            latest_price = p.latest_verified_price
            comp_str = ", ".join([pi.ingredient.display_name for pi in p.ingredients if pi.ingredient])
            strength_str = ", ".join([f"{pi.strength_value} {pi.strength_unit}" for pi in p.ingredients])

            is_verified = False
            status_text = "Price not verified"
            last_ver_dt = None
            listed_price = None
            unit_price = None
            price_type_val = None
            source_nm = None
            source_u = None

            if latest_price:
                last_ver_dt = latest_price.verified_at
                listed_price = latest_price.amount_inr
                unit_price = latest_price.unit_price_inr
                price_type_val = latest_price.price_type
                source_nm = latest_price.source.source_name if latest_price.source else (p.source.source_name if p.source else None)
                source_u = latest_price.source_url or (latest_price.source.source_url if latest_price.source else None)

                # Check freshness
                price_dt = last_ver_dt
                if price_dt.tzinfo is None:
                    price_dt = price_dt.replace(tzinfo=timezone.utc)

                if now - price_dt > stale_threshold:
                    status_text = "Price data may be outdated"
                    is_verified = False
                elif latest_price.verification_status == "verified":
                    status_text = "Verified"
                    is_verified = True
                else:
                    status_text = "Price not verified"
                    is_verified = False

            items.append(
                PriceComparisonItem(
                    product_id=p.id,
                    brand_name=p.brand_name,
                    generic_name=p.generic_name,
                    manufacturer_name=p.manufacturer_name,
                    composition=comp_str,
                    strength=strength_str,
                    dosage_form=p.dosage_form,
                    administration_route=p.administration_route,
                    release_type=p.release_type,
                    pack_size=p.pack_size,
                    pack_unit=p.pack_unit,
                    listed_price_inr=listed_price,
                    unit_price_inr=unit_price,
                    price_type=price_type_val,
                    source_name=source_nm,
                    source_url=source_u,
                    last_verified=last_ver_dt,
                    verification_status=status_text,
                    is_jan_aushadhi=p.is_jan_aushadhi,
                    is_price_verified=is_verified,
                )
            )

        # Prepare reference attributes
        ref_ings = {
            pi.ingredient.normalized_name: (pi.strength_value, pi.strength_unit.lower())
            for pi in ref_prod.ingredients if pi.ingredient
        }
        ref_price_obj = ref_prod.latest_verified_price
        ref_unit_price = ref_price_obj.unit_price_inr if (ref_price_obj and ref_price_obj.verification_status == "verified") else None
        ref_pack_price = ref_price_obj.amount_inr if (ref_price_obj and ref_price_obj.verification_status == "verified") else None

        comparisons: List[PriceComparisonDifference] = []
        summary_notes: List[str] = []

        for p in products:
            if p.id == ref_prod.id:
                continue

            incompat_reasons = []

            # 1. Ingredient equivalence
            cand_ings = {
                pi.ingredient.normalized_name: (pi.strength_value, pi.strength_unit.lower())
                for pi in p.ingredients if pi.ingredient
            }
            if set(cand_ings.keys()) != set(ref_ings.keys()):
                incompat_reasons.append(
                    f"Different active ingredients: [{', '.join(cand_ings.keys())}] vs [{', '.join(ref_ings.keys())}]"
                )
            else:
                # 2. Strength equivalence
                for k, v in ref_ings.items():
                    cand_v = cand_ings.get(k)
                    if not cand_v or abs(cand_v[0] - v[0]) > 0.001 or cand_v[1] != v[1]:
                        incompat_reasons.append(
                            f"Different strength for {k}: {cand_v[0] if cand_v else 'N/A'}{cand_v[1] if cand_v else ''} vs {v[0]}{v[1]}"
                        )

            # 3. Dosage form and route
            if p.dosage_form.strip().lower() != ref_prod.dosage_form.strip().lower():
                incompat_reasons.append(f"Incompatible dosage form: {p.dosage_form} vs {ref_prod.dosage_form}")
            if p.administration_route.strip().lower() != ref_prod.administration_route.strip().lower():
                incompat_reasons.append(f"Incompatible route: {p.administration_route} vs {ref_prod.administration_route}")

            # 4. Release characteristics
            if (p.release_type or "immediate-release").strip().lower() != (ref_prod.release_type or "immediate-release").strip().lower():
                incompat_reasons.append(f"Incompatible release characteristics: {p.release_type} vs {ref_prod.release_type}")

            # 5. Price verification check
            cand_price_obj = p.latest_verified_price
            cand_unit_price = cand_price_obj.unit_price_inr if (cand_price_obj and cand_price_obj.verification_status == "verified") else None
            cand_pack_price = cand_price_obj.amount_inr if (cand_price_obj and cand_price_obj.verification_status == "verified") else None

            if not ref_unit_price:
                incompat_reasons.append(f"Reference product '{ref_prod.brand_name}' has unverified or missing price.")
            if not cand_unit_price:
                incompat_reasons.append(f"Product '{p.brand_name}' has unverified or missing price.")

            # Calculate savings only if strictly comparable
            is_comparable = len(incompat_reasons) == 0
            unit_savings = None
            savings_pct = None
            pack_savings = None
            notes = ""

            if is_comparable:
                unit_savings = round(ref_unit_price - cand_unit_price, 2)
                if ref_unit_price > 0:
                    savings_pct = round((unit_savings / ref_unit_price) * 100, 1)

                # Pack savings if pack sizes match
                if abs(p.pack_size - ref_prod.pack_size) < 0.001 and p.pack_unit.lower() == ref_prod.pack_unit.lower():
                    pack_savings = round(ref_pack_price - cand_pack_price, 2)
                    notes = f"Verified comparable. Same pack size ({p.pack_size} {p.pack_unit})."
                else:
                    normalized_ref_pack = round(ref_unit_price * p.pack_size, 2)
                    pack_savings = round(normalized_ref_pack - cand_pack_price, 2)
                    notes = (
                        f"Verified comparable. Pack sizes differ ({ref_prod.brand_name}: {ref_prod.pack_size} {ref_prod.pack_unit}, "
                        f"{p.brand_name}: {p.pack_size} {p.pack_unit}). Normalized unit price used."
                    )
            else:
                notes = f"Comparison invalid or non-equivalent: {'; '.join(incompat_reasons)}"

            comparisons.append(
                PriceComparisonDifference(
                    compared_product_id=p.id,
                    compared_brand_name=p.brand_name,
                    reference_product_id=ref_prod.id,
                    reference_brand_name=ref_prod.brand_name,
                    is_comparable=is_comparable,
                    incomparability_reasons=incompat_reasons,
                    reference_unit_price_inr=ref_unit_price,
                    alternative_unit_price_inr=cand_unit_price,
                    unit_savings_inr=unit_savings,
                    savings_percentage=savings_pct,
                    pack_savings_inr=pack_savings,
                    notes=notes,
                )
            )

        summary_notes.append(
            f"Reference baseline product: {ref_prod.brand_name} ({ref_prod.dosage_form}, {ref_prod.pack_size} {ref_prod.pack_unit})."
        )
        summary_notes.append("Unit prices are normalized per tablet/capsule/ml for fair packaging comparison.")
        summary_notes.append("Prices reflect official government ceilings or verified MRPs. Local retail prices may vary.")

        return PriceComparisonResponse(
            items=items,
            comparisons=comparisons,
            summary_notes=summary_notes,
            safety_disclaimer=SafetyValidationService.get_standard_disclaimer(),
        )
