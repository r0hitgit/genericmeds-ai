import re
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.medicine import MedicineProduct
from app.models.ingredient import ProductIngredient, ActiveIngredient
from app.schemas.medicine import (
    AlternativeSearchRequest,
    AlternativeSearchResponse,
    AlternativeCandidate,
    MedicineProductSummary,
)
from app.services.medicine_search import MedicineSearchService
from app.services.safety_validation import SafetyValidationService


class AlternativeMatchingService:
    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.strip().lower()

    @classmethod
    def clean_molecule_name(cls, name: str) -> str:
        """
        Strips formulation terms (e.g. gastro-resistant, sustained-release, enteric-coated)
        so that clinical active pharmaceutical ingredients match consistently across
        government catalogue and retail branded listings.
        """
        clean = name.strip().lower()
        clean = re.sub(
            r"\b(gastro-resistant|gastro resistant|gastro-resistance|enteric-coated|enteric coated|"
            r"sustained-release|sustained release|sustained-relase|prolonged-release|prolonged release|"
            r"extended-release|extended release|delayed-release|delayed release|controlled-release|"
            r"controlled release|tablets ip|capsules ip|injection ip|tablets|capsules|injection)\b",
            "",
            clean,
            flags=re.IGNORECASE,
        )
        clean = re.sub(r"[\(\)\.\,]", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @classmethod
    def match_alternatives(
        cls, db: Session, req: AlternativeSearchRequest
    ) -> AlternativeSearchResponse:
        ref_product: Optional[MedicineProduct] = None
        target_ingredients: List[Dict[str, any]] = []
        target_form: Optional[str] = req.dosage_form
        target_route: str = "Oral"
        target_release: Optional[str] = req.release_type

        # 1. Resolve reference product if ID or name is provided
        if req.medicine_id:
            ref_product = db.query(MedicineProduct).options(
                joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
                joinedload(MedicineProduct.prices),
            ).filter(MedicineProduct.id == req.medicine_id).first()
        elif req.name:
            ref_product = db.query(MedicineProduct).options(
                joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
                joinedload(MedicineProduct.prices),
            ).filter(MedicineProduct.brand_name.ilike(req.name.strip())).first()

        if ref_product:
            target_form = target_form or ref_product.dosage_form
            target_route = ref_product.administration_route
            target_release = target_release or ref_product.release_type
            target_ingredients = [
                {
                    "normalized_name": pi.ingredient.normalized_name if pi.ingredient else "",
                    "clean_name": cls.clean_molecule_name(pi.ingredient.normalized_name if pi.ingredient else ""),
                    "display_name": pi.ingredient.display_name if pi.ingredient else "",
                    "strength_value": pi.strength_value,
                    "strength_unit": pi.strength_unit.lower(),
                }
                for pi in ref_product.ingredients
            ]
        elif req.active_ingredients:
            target_ingredients = [
                {
                    "normalized_name": cls._normalize_name(item.name),
                    "clean_name": cls.clean_molecule_name(item.name),
                    "display_name": item.name.strip(),
                    "strength_value": item.strength_value,
                    "strength_unit": item.strength_unit.strip().lower(),
                }
                for item in req.active_ingredients
            ]

        # If we still do not have active ingredients, we cannot establish verified equivalence!
        if not target_ingredients or not target_form:
            return AlternativeSearchResponse(
                reference_product=MedicineSearchService._to_summary(ref_product) if ref_product else None,
                total_candidates=0,
                candidates=[],
                safety_notice=(
                    "Insufficient formulation details provided. Equivalence requires verified active ingredients, "
                    "exact strengths, and dosage forms. No equivalence claimed."
                ),
            )

        # 2. Query candidate products containing at least one of the active ingredients
        ing_names = [i["normalized_name"] for i in target_ingredients]
        clean_target_mols = [i["clean_name"] for i in target_ingredients if len(i.get("clean_name", "")) >= 3]

        filter_clauses = [ActiveIngredient.normalized_name.in_(ing_names)]
        for cm in clean_target_mols:
            filter_clauses.append(ActiveIngredient.normalized_name.ilike(f"%{cm}%"))

        candidate_prods = db.query(MedicineProduct).distinct().options(
            joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
            joinedload(MedicineProduct.prices),
        ).join(
            MedicineProduct.ingredients
        ).join(
            ProductIngredient.ingredient
        ).filter(
            or_(*filter_clauses)
        ).all()

        target_ing_map = {i.get("clean_name", i["normalized_name"]): i for i in target_ingredients}
        target_ing_count = len(target_ingredients)

        ref_unit_price: Optional[float] = None
        if ref_product and ref_product.latest_verified_price:
            ref_unit_price = ref_product.latest_verified_price.unit_price_inr

        matched_candidates: List[AlternativeCandidate] = []

        for cand in candidate_prods:
            if ref_product and cand.id == ref_product.id:
                continue  # Skip self

            cand_ings = cand.ingredients
            cand_ing_count = len(cand_ings)
            cand_ing_map = {}
            for pi in cand_ings:
                if pi.ingredient:
                    clean_cand_name = cls.clean_molecule_name(pi.ingredient.normalized_name)
                    cand_ing_map[clean_cand_name] = {
                        "strength_value": pi.strength_value,
                        "strength_unit": pi.strength_unit.lower(),
                        "display_name": pi.ingredient.display_name,
                    }

            # Check ingredient composition equivalence
            # Rule: Every active ingredient must match, and count must be identical
            is_same_ingredients = set(cand_ing_map.keys()) == set(target_ing_map.keys())

            if not is_same_ingredients:
                # Incompatible composition or partial ingredient match
                continue

            # Check strength equivalence for each ingredient
            strengths_match = True
            for norm_name, target_spec in target_ing_map.items():
                cand_spec = cand_ing_map.get(norm_name)
                if not cand_spec:
                    strengths_match = False
                    break
                if abs(cand_spec["strength_value"] - target_spec["strength_value"]) > 0.001:
                    strengths_match = False
                    break
                if cand_spec["strength_unit"] != target_spec["strength_unit"]:
                    strengths_match = False
                    break

            # Check dosage form, route, and release type
            form_match = cand.dosage_form.strip().lower() == target_form.strip().lower()
            route_match = cand.administration_route.strip().lower() == target_route.strip().lower()
            release_match = (
                (cand.release_type or "immediate-release").strip().lower()
                == (target_release or "immediate-release").strip().lower()
            )

            # Determine classification
            if is_same_ingredients and strengths_match and form_match and route_match and release_match:
                classification = "EXACT_COMPOSITION_MATCH"
                notes = (
                    "Exact active ingredient composition, strength, dosage form, route, and release profile match. "
                    "Clinical substitution must be confirmed with your doctor or pharmacist."
                )
            elif is_same_ingredients and (not form_match or not release_match):
                classification = "DIFFERENT_FORMULATION"
                reasons = []
                if not form_match:
                    reasons.append(f"Different form: {cand.dosage_form} vs {target_form}")
                if not release_match:
                    reasons.append(f"Different release profile: {cand.release_type} vs {target_release}")
                if not strengths_match:
                    reasons.append("Different strength")
                notes = f"Formulation differs ({', '.join(reasons)}). Not equivalent."
            elif is_same_ingredients and not strengths_match:
                classification = "DIFFERENT_STRENGTH"
                notes = "Same active ingredients, but strength differs. Not an equivalent dose."
            else:
                classification = "INCOMPATIBLE"
                notes = "Incompatible product characteristics."

            # High risk analysis
            cand_ing_displays = [pi.ingredient.display_name for pi in cand.ingredients if pi.ingredient]
            is_hr, hr_reasons = SafetyValidationService.check_high_risk_product(
                cand_ing_displays, cand.release_type, cand.dosage_form
            )

            # Pricing and potential savings
            cand_unit_price: Optional[float] = None
            if cand.latest_verified_price:
                cand_unit_price = cand.latest_verified_price.unit_price_inr

            unit_savings: Optional[float] = None
            savings_pct: Optional[float] = None

            if (
                classification == "EXACT_COMPOSITION_MATCH"
                and ref_unit_price is not None
                and cand_unit_price is not None
                and ref_unit_price > 0
            ):
                unit_savings = round(ref_unit_price - cand_unit_price, 2)
                savings_pct = round((unit_savings / ref_unit_price) * 100, 1)

            cand_summary = MedicineSearchService._to_summary(cand)

            matched_candidates.append(
                AlternativeCandidate(
                    product=cand_summary,
                    match_classification=classification,
                    match_notes=notes,
                    is_high_risk=is_hr,
                    high_risk_warnings=hr_reasons,
                    reference_unit_price=ref_unit_price,
                    alternative_unit_price=cand_unit_price,
                    unit_savings_inr=unit_savings,
                    savings_percentage=savings_pct,
                )
            )

        # Sort: EXACT_COMPOSITION_MATCH first, then by savings percentage desc or unit price asc
        def sort_key(c: AlternativeCandidate):
            score = 0
            if c.match_classification == "EXACT_COMPOSITION_MATCH":
                score -= 1000
            if c.product.is_jan_aushadhi:
                score -= 500
            savings = c.savings_percentage or 0.0
            return (score, -savings)

        matched_candidates.sort(key=sort_key)

        return AlternativeSearchResponse(
            reference_product=MedicineSearchService._to_summary(ref_product) if ref_product else None,
            total_candidates=len(matched_candidates),
            candidates=matched_candidates,
            safety_notice=(
                "A composition match indicates identical active ingredients and strengths, but is NOT a guarantee "
                "of clinical bioequivalence. Consult a qualified physician or licensed pharmacist before changing medicines."
            ),
        )
