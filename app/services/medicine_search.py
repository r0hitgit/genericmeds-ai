from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from app.models.medicine import MedicineProduct
from app.models.ingredient import ProductIngredient, ActiveIngredient
from app.models.pricing import MedicinePrice
from app.models.alias import MedicineAlias
from app.models.brand_lookup import BrandGenericLookup
from app.schemas.medicine import (
    MedicineProductSummary,
    MedicineProductDetail,
    IngredientSchema,
    MedicinePriceSchema,
    DataSourceInfo,
    MedicineSearchResponse,
)
from app.services.safety_validation import SafetyValidationService


class MedicineSearchService:
    @staticmethod
    def _to_summary(prod: MedicineProduct) -> MedicineProductSummary:
        ingredients_list = []
        for pi in prod.ingredients:
            ingredients_list.append(
                IngredientSchema(
                    name=pi.ingredient.display_name if pi.ingredient else "Unknown",
                    normalized_name=pi.ingredient.normalized_name if pi.ingredient else "unknown",
                    strength_value=pi.strength_value,
                    strength_unit=pi.strength_unit,
                )
            )

        latest_price_schema = None
        latest_p = prod.latest_verified_price
        if latest_p:
            latest_price_schema = MedicinePriceSchema(
                id=latest_p.id,
                amount_inr=latest_p.amount_inr,
                price_type=latest_p.price_type,
                pack_quantity=latest_p.pack_quantity,
                unit_of_measure=latest_p.unit_of_measure,
                unit_price_inr=latest_p.unit_price_inr,
                source_name=latest_p.source.source_name if latest_p.source else None,
                source_url=latest_p.source_url or (latest_p.source.source_url if latest_p.source else None),
                effective_date=latest_p.effective_date,
                verified_at=latest_p.verified_at,
                verification_status=latest_p.verification_status,
            )

        return MedicineProductSummary(
            id=prod.id,
            brand_name=prod.brand_name,
            generic_name=prod.generic_name,
            manufacturer_name=prod.manufacturer_name,
            dosage_form=prod.dosage_form,
            administration_route=prod.administration_route,
            release_type=prod.release_type,
            pack_size=prod.pack_size,
            pack_unit=prod.pack_unit,
            prescription_status=prod.prescription_status,
            is_jan_aushadhi=prod.is_jan_aushadhi,
            pmbi_code=prod.pmbi_code,
            therapeutic_group=prod.therapeutic_group,
            ingredients=ingredients_list,
            latest_price=latest_price_schema,
        )

    @classmethod
    def search_medicines(
        cls,
        db: Session,
        query: str,
        limit: int = 20,
        offset: int = 0,
        jan_aushadhi_only: bool = False,
    ) -> MedicineSearchResponse:
        q_clean = query.strip()
        if not q_clean:
            return MedicineSearchResponse(
                query="",
                match_type="partial",
                total=0,
                items=[]
            )

        # Layer 1 & 2: Exact code, brand, generic, alias, or brand lookup match
        exact_filters = [
            func.lower(MedicineProduct.brand_name) == q_clean.lower(),
            func.lower(MedicineProduct.generic_name) == q_clean.lower(),
            func.lower(MedicineProduct.pmbi_code) == q_clean.lower(),
            func.lower(MedicineProduct.drug_code_label) == q_clean.lower(),
        ]
        if q_clean.isdigit():
            exact_filters.append(MedicineProduct.drug_code == int(q_clean))

        exact_query = db.query(MedicineProduct).options(
            joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
            joinedload(MedicineProduct.prices),
        ).filter(or_(*exact_filters))

        if jan_aushadhi_only:
            exact_query = exact_query.filter(MedicineProduct.is_jan_aushadhi == True)

        exact_results = exact_query.all()

        # Check exact alias match
        alias_product_ids = [
            a.product_id
            for a in db.query(MedicineAlias.product_id).filter(
                func.lower(MedicineAlias.alias_normalized) == q_clean.lower()
            ).all()
        ]

        # Check BrandGenericLookup match
        brand_lookup_product_ids = [
            b.linked_product_id
            for b in db.query(BrandGenericLookup.linked_product_id).filter(
                BrandGenericLookup.linked_product_id.isnot(None),
                or_(
                    func.lower(BrandGenericLookup.popular_brand_names_normalized) == q_clean.lower(),
                    func.lower(BrandGenericLookup.primary_pmbi_drug_code) == q_clean.lower(),
                    BrandGenericLookup.popular_brand_names.ilike(f"%{q_clean}%"),
                )
            ).all()
        ]

        extra_ids = set(alias_product_ids + [pid for pid in brand_lookup_product_ids if pid])
        if extra_ids:
            alias_products = db.query(MedicineProduct).options(
                joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
                joinedload(MedicineProduct.prices),
            ).filter(MedicineProduct.id.in_(extra_ids))
            if jan_aushadhi_only:
                alias_products = alias_products.filter(MedicineProduct.is_jan_aushadhi == True)

            seen_ids = {p.id for p in exact_results}
            for p in alias_products.all():
                if p.id not in seen_ids:
                    exact_results.append(p)
                    seen_ids.add(p.id)

        if exact_results:
            total_count = len(exact_results)
            paged = exact_results[offset : offset + limit]
            return MedicineSearchResponse(
                query=q_clean,
                match_type="exact",
                total=total_count,
                items=[cls._to_summary(p) for p in paged],
            )

        # Fallback to broader search (brand, generic, code, therapeutic group, ingredients, or aliases)
        search_pattern = f"%{q_clean}%"
        base_query = db.query(MedicineProduct).distinct().options(
            joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
            joinedload(MedicineProduct.prices),
        ).outerjoin(
            MedicineProduct.ingredients
        ).outerjoin(
            ProductIngredient.ingredient
        ).outerjoin(
            MedicineProduct.aliases
        ).filter(
            or_(
                MedicineProduct.brand_name.ilike(search_pattern),
                MedicineProduct.generic_name.ilike(search_pattern),
                MedicineProduct.pmbi_code.ilike(search_pattern),
                MedicineProduct.drug_code_label.ilike(search_pattern),
                MedicineProduct.therapeutic_group.ilike(search_pattern),
                ActiveIngredient.display_name.ilike(search_pattern),
                ActiveIngredient.normalized_name.ilike(search_pattern),
                MedicineAlias.alias.ilike(search_pattern),
                MedicineAlias.alias_normalized.ilike(search_pattern),
            )
        )

        if jan_aushadhi_only:
            base_query = base_query.filter(MedicineProduct.is_jan_aushadhi == True)

        total_count = base_query.count()
        results = base_query.offset(offset).limit(limit).all()

        if not results:
            # Token-based multi-term fallback for brand + strength queries (e.g. 'omee 500', 'folvite 5mg')
            import re
            tokens = [t.strip() for t in re.split(r"[\s\-_,]+", q_clean) if len(t.strip()) >= 2]
            alpha_tokens = [t for t in tokens if not t.isdigit()]

            # Prioritize alphabetical brand/ingredient tokens (e.g. 'omee')
            search_tokens = alpha_tokens if alpha_tokens else tokens
            collected_fuzzy = []
            seen_ids = set()

            for tok in search_tokens:
                tok_pat = f"%{tok}%"
                tok_query = db.query(MedicineProduct).distinct().options(
                    joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
                    joinedload(MedicineProduct.prices),
                ).outerjoin(
                    MedicineProduct.ingredients
                ).outerjoin(
                    ProductIngredient.ingredient
                ).outerjoin(
                    MedicineProduct.aliases
                ).filter(
                    or_(
                        MedicineProduct.brand_name.ilike(tok_pat),
                        MedicineProduct.generic_name.ilike(tok_pat),
                        ActiveIngredient.display_name.ilike(tok_pat),
                        ActiveIngredient.normalized_name.ilike(tok_pat),
                        MedicineAlias.alias.ilike(tok_pat),
                        MedicineAlias.alias_normalized.ilike(tok_pat),
                    )
                )
                if jan_aushadhi_only:
                    tok_query = tok_query.filter(MedicineProduct.is_jan_aushadhi == True)
                for item in tok_query.limit(limit).all():
                    if item.id not in seen_ids:
                        seen_ids.add(item.id)
                        collected_fuzzy.append(item)

            if collected_fuzzy:
                return MedicineSearchResponse(
                    query=q_clean,
                    match_type="fuzzy",
                    total=len(collected_fuzzy),
                    items=[cls._to_summary(p) for p in collected_fuzzy[:limit]],
                )

        return MedicineSearchResponse(
            query=q_clean,
            match_type="partial",
            total=total_count,
            items=[cls._to_summary(p) for p in results],
        )

    @classmethod
    def get_medicine_by_id(cls, db: Session, medicine_id: int) -> Optional[MedicineProductDetail]:
        prod = db.query(MedicineProduct).options(
            joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
            joinedload(MedicineProduct.prices),
            joinedload(MedicineProduct.source),
        ).filter(MedicineProduct.id == medicine_id).first()

        if not prod:
            return None

        summary = cls._to_summary(prod)

        # Build price history
        price_history = []
        for p in prod.prices:
            price_history.append(
                MedicinePriceSchema(
                    id=p.id,
                    amount_inr=p.amount_inr,
                    price_type=p.price_type,
                    pack_quantity=p.pack_quantity,
                    unit_of_measure=p.unit_of_measure,
                    unit_price_inr=p.unit_price_inr,
                    source_name=p.source.source_name if p.source else None,
                    source_url=p.source_url or (p.source.source_url if p.source else None),
                    effective_date=p.effective_date,
                    verified_at=p.verified_at,
                    verification_status=p.verification_status,
                )
            )

        # Source info
        source_info = None
        if prod.source:
            source_info = DataSourceInfo(
                id=prod.source.id,
                source_name=prod.source.source_name,
                source_url=prod.source.source_url,
                source_type=prod.source.source_type,
                data_status=prod.source.data_status,
            )

        # Check high risk
        ing_names = [pi.ingredient.display_name for pi in prod.ingredients if pi.ingredient]
        is_hr, hr_reasons = SafetyValidationService.check_high_risk_product(
            ing_names, prod.release_type, prod.dosage_form
        )

        return MedicineProductDetail(
            **summary.model_dump(),
            source=source_info,
            price_history=price_history,
            high_risk_flag=is_hr,
            high_risk_reasons=hr_reasons,
            created_at=prod.created_at,
            updated_at=prod.updated_at,
        )
