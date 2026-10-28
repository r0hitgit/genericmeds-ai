import re
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.models.brand_lookup import BrandGenericLookup
from app.models.medicine import MedicineProduct
from app.models.ingredient import ProductIngredient
from app.schemas.brand_lookup import BrandGenericLookupOut, BrandSearchResponse
from app.services.medicine_search import MedicineSearchService


class BrandSearchService:
    @staticmethod
    def _to_lookup_out(b: BrandGenericLookup) -> BrandGenericLookupOut:
        linked_summary = None
        if b.linked_product:
            linked_summary = MedicineSearchService._to_summary(b.linked_product)

        return BrandGenericLookupOut(
            id=b.id,
            brand_lookup_id=b.brand_lookup_id,
            popular_brand_names=b.popular_brand_names,
            popular_brand_names_normalized=b.popular_brand_names_normalized,
            phonetic_and_colloquial_aliases=b.phonetic_and_colloquial_aliases,
            market_reference_manufacturers=b.market_reference_manufacturers,
            therapeutic_category=b.therapeutic_category,
            active_generic_composition=b.active_generic_composition,
            primary_pmbi_drug_code=b.primary_pmbi_drug_code,
            all_matching_pmbi_codes_and_strengths=b.all_matching_pmbi_codes_and_strengths,
            unit_pack_size=b.unit_pack_size,
            janaushadhi_mrp_inr=b.janaushadhi_mrp_inr,
            branded_market_reference_inr=b.branded_market_reference_inr,
            indicative_savings_inr=b.indicative_savings_inr,
            indicative_savings_pct=b.indicative_savings_pct,
            indicative_savings_pct_numeric=b.indicative_savings_pct_numeric,
            pharmacist_and_doctor_verification_rule=b.pharmacist_and_doctor_verification_rule,
            reconciliation_status=b.reconciliation_status,
            linked_product_id=b.linked_product_id,
            linked_product=linked_summary,
            source_file=b.source_file,
            review_status=b.review_status,
        )

    @classmethod
    def search_brands(
        cls,
        db: Session,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> BrandSearchResponse:
        q_clean = query.strip()
        if not q_clean:
            return BrandSearchResponse(
                query="",
                total=0,
                limit=limit,
                offset=offset,
                items=[],
            )

        pattern = f"%{q_clean}%"
        q_low = q_clean.lower()

        base_query = db.query(BrandGenericLookup).options(
            joinedload(BrandGenericLookup.linked_product).joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
            joinedload(BrandGenericLookup.linked_product).joinedload(MedicineProduct.prices),
        ).filter(
            or_(
                BrandGenericLookup.brand_lookup_id.ilike(pattern),
                BrandGenericLookup.popular_brand_names.ilike(pattern),
                BrandGenericLookup.popular_brand_names_normalized.ilike(pattern),
                BrandGenericLookup.phonetic_and_colloquial_aliases.ilike(pattern),
                BrandGenericLookup.market_reference_manufacturers.ilike(pattern),
                BrandGenericLookup.therapeutic_category.ilike(pattern),
                BrandGenericLookup.active_generic_composition.ilike(pattern),
                BrandGenericLookup.primary_pmbi_drug_code.ilike(pattern),
            )
        )

        total = base_query.count()
        items = base_query.offset(offset).limit(limit).all()

        return BrandSearchResponse(
            query=q_clean,
            total=total,
            limit=limit,
            offset=offset,
            items=[cls._to_lookup_out(b) for b in items],
        )

    @classmethod
    def get_brand_by_id(cls, db: Session, brand_lookup_id: str) -> Optional[BrandGenericLookupOut]:
        clean_id = brand_lookup_id.strip().upper()
        b = db.query(BrandGenericLookup).options(
            joinedload(BrandGenericLookup.linked_product).joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
            joinedload(BrandGenericLookup.linked_product).joinedload(MedicineProduct.prices),
        ).filter(
            or_(
                BrandGenericLookup.brand_lookup_id == clean_id,
                func.upper(BrandGenericLookup.brand_lookup_id) == clean_id,
            )
        ).first()

        if not b and brand_lookup_id.isdigit():
            b = db.query(BrandGenericLookup).options(
                joinedload(BrandGenericLookup.linked_product).joinedload(MedicineProduct.ingredients).joinedload(ProductIngredient.ingredient),
                joinedload(BrandGenericLookup.linked_product).joinedload(MedicineProduct.prices),
            ).filter(BrandGenericLookup.id == int(brand_lookup_id)).first()

        if not b:
            return None

        return cls._to_lookup_out(b)
