import abc
import json
import logging
import re
from typing import Optional, List, Dict, Any, Tuple
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.ai.system_prompt import SYSTEM_PROMPT, MANDATORY_DISCLAIMER
from app.schemas.chat import ChatMessage, ChatExtractedEntity, ChatResponse
from app.schemas.medicine import AlternativeSearchRequest
from app.schemas.pricing import PriceComparisonRequest
from app.services.medicine_search import MedicineSearchService
from app.services.brand_search import BrandSearchService
from app.services.alternatives import AlternativeMatchingService
from app.services.price_comparison import PriceComparisonService
from app.services.safety_validation import SafetyValidationService

logger = logging.getLogger(__name__)


class BaseLLMProvider(abc.ABC):
    @abc.abstractmethod
    async def extract_query_entities(self, message: str) -> ChatExtractedEntity:
        """Extracts medicine names, active ingredients, strength, dosage form, and intent."""
        pass

    @abc.abstractmethod
    async def generate_grounded_response(
        self,
        user_message: str,
        language: str,
        extracted: ChatExtractedEntity,
        context_data: Dict[str, Any],
        conversation_history: List[ChatMessage],
    ) -> str:
        """Generates grounded explanation of structured database facts."""
        pass


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", timeout: int = 15):
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

    async def _call_gemini(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self.api_url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Error calling Gemini API: {e}")
        return None

    async def extract_query_entities(self, message: str) -> ChatExtractedEntity:
        # Prompt Gemini to return JSON
        prompt = f"""Analyze the user's medicine inquiry and extract structured parameters in JSON format.
JSON schema:
{{
  "medicine_name": string or null,
  "active_ingredients": [string] or null,
  "strength": string or null,
  "dosage_form": string or null,
  "intent": "search" | "compare" | "composition_explain" | "alternative" | "emergency" | "general"
}}

User query: "{message}"

Return ONLY valid raw JSON without markdown formatting or code blocks:"""

        raw = await self._call_gemini(prompt, system_instruction=SYSTEM_PROMPT)
        if raw:
            try:
                # Clean any markdown fences
                cleaned = re.sub(r"^```json\s*", "", raw.strip(), flags=re.IGNORECASE)
                cleaned = re.sub(r"\s*```$", "", cleaned.strip())
                parsed = json.loads(cleaned)
                return ChatExtractedEntity(**parsed)
            except Exception as e:
                logger.warning(f"Failed to parse Gemini entity JSON: {e}. Falling back to regex.")

        # Fallback to regex extractor
        return FallbackLLMProvider.regex_extract_entities(message)

    async def generate_grounded_response(
        self,
        user_message: str,
        language: str,
        extracted: ChatExtractedEntity,
        context_data: Dict[str, Any],
        conversation_history: List[ChatMessage],
    ) -> str:
        lang_instruction = "Respond in simple, clear Hindi (using Devanagari script)." if language == "hi" else "Respond in simple, clear English."

        facts_json = json.dumps(context_data, indent=2, default=str)
        prompt = f"""{lang_instruction}

User inquiry: "{user_message}"

Verified factual data retrieved from backend database:
{facts_json}

Instructions:
1. Explain the verified product details, active ingredients, dosage forms, and price comparisons factually.
2. If Jan Aushadhi alternatives exist, highlight them respectfully as affordable government initiatives.
3. If no matching verified medicine was found or prices are unverified, clearly state that limitation.
4. Emphasize that substitution requires consulting a doctor or licensed pharmacist.
5. Do NOT invent prices, manufacturers, or medical approvals.
7. Use clean, plain formatting without informal symbols like '@' (write 'for ₹X' or 'priced at ₹X'). Avoid unnecessary asterisks.
8. End with the mandatory medical disclaimer.
"""
        response_text = await self._call_gemini(prompt, system_instruction=SYSTEM_PROMPT)
        if response_text:
            return response_text.strip()

        # Fallback to deterministic template
        return FallbackLLMProvider.format_deterministic_response(user_message, language, extracted, context_data)


class FallbackLLMProvider(BaseLLMProvider):
    """
    Deterministic rule-based provider that ensures complete system functionality
    even when external LLM providers or internet connectivity are unavailable.
    """

    @staticmethod
    def regex_extract_entities(message: str) -> ChatExtractedEntity:
        lowered = message.lower()

        # Detect intent
        intent = "search"
        if "compare" in lowered or "difference between" in lowered or "vs" in lowered:
            intent = "compare"
        elif "alternative" in lowered or "generic version" in lowered or "substitute" in lowered:
            intent = "alternative"
        elif "composition" in lowered or "active ingredient" in lowered or "what is in" in lowered:
            intent = "composition_explain"

        # Detect strength (e.g. '500mg' or trailing number like 'omee 500' -> 500mg)
        strength_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(mg|g|mcg|ml|iu)\b", lowered)
        strength = strength_match.group(0) if strength_match else None
        if not strength:
            num_match = re.search(r"\b(\d{2,4})\b", lowered)
            if num_match:
                strength = f"{num_match.group(1)}mg"

        # Detect dosage form
        form = None
        for f in ["tablet", "capsule", "syrup", "injection", "cream", "ointment", "drops", "inhaler"]:
            if f in lowered:
                form = f.title()
                break

        # Remove common query filler words to isolate medicine name
        filler_patterns = [
            r"\b(what is the|what is|generic alternative to|alternative to|show me|tell me|give me|find me)\b",
            r"\b(affordable medicines with|affordable medicine|lower-priced|equivalent|substitute for)\b",
            r"\b(in simple hindi|in hindi|in english|difference between|compare|prices of|price of|price)\b",
            r"\b(composition of|what is in|active ingredient of|details of)\b",
            r"\b(about this medicine|about this|about that|this medicine|this drug|this pill|medicine|drug|tablet|tablets|capsule|capsules)\b",
            r"\b(please|kindly|can you|could you|help me with|info on|information on|for me)\b",
            r"\b(this|that|these|those|the|a|an|is|are|of|to|in|for|with)\b",
        ]
        clean_name = lowered
        for pattern in filler_patterns:
            clean_name = re.sub(pattern, " ", clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r"[?,!\.\"\']", "", clean_name).strip()

        # If clean_name has fewer than 2 meaningful characters or is trivial, set to None
        medicine_name = clean_name if len(clean_name) >= 2 else None

        return ChatExtractedEntity(
            medicine_name=medicine_name,
            strength=strength,
            dosage_form=form,
            intent=intent,
        )

    async def extract_query_entities(self, message: str) -> ChatExtractedEntity:
        return self.regex_extract_entities(message)

    @staticmethod
    def format_deterministic_response(
        user_message: str,
        language: str,
        extracted: ChatExtractedEntity,
        context_data: Dict[str, Any],
    ) -> str:
        medicines = context_data.get("medicines", [])
        brand_lookups = context_data.get("brand_lookups", [])
        alternatives = context_data.get("alternatives", [])
        comparison = context_data.get("comparison", {})
        query = extracted.medicine_name or user_message

        is_hindi = language == "hi"

        lines = []

        if not medicines and not alternatives and not brand_lookups:
            if is_hindi:
                lines.append(f"क्षमा करें, हमें '{query}' के लिए सत्यापित डेटाबेस में कोई दवा रिकॉर्ड नहीं मिला।")
                lines.append("कृपया दवा का नाम, सटीक मात्रा (स्ट्रेंथ) या घटक दोबारा जांचें, या अपने नजदीकी पंजीकृत फार्मासिस्ट से परामर्श लें।")
            else:
                lines.append(f"We could not find verified records matching '{query}' in our database.")
                lines.append("Please verify the spelling, exact strength, or active ingredients, or consult a licensed pharmacist.")
        else:
            if is_hindi:
                lines.append(f"यहाँ '{query}' के संबंध में सत्यापित जानकारी दी गई है:\n")
            else:
                lines.append(f"Here is verified information regarding '{query}':\n")

            # Brand lookups from popular Indian brands dataset
            if brand_lookups:
                if is_hindi:
                    lines.append("लोकप्रिय ब्रांड संदर्भ एवं जन औषधि विकल्प विवरण:")
                else:
                    lines.append("Popular Brand Reference & PMBJP Generic Equivalence:")

                for b in brand_lookups[:2]:
                    b_name = b.get("popular_brand_names")
                    b_comp = b.get("active_generic_composition")
                    b_code = b.get("primary_pmbi_drug_code")
                    b_mkt = b.get("branded_market_reference_inr")
                    b_jan = b.get("janaushadhi_mrp_inr")
                    b_sav = b.get("indicative_savings_pct")
                    b_rule = b.get("pharmacist_and_doctor_verification_rule")

                    mkt_str = f"₹{b_mkt:.2f}" if b_mkt is not None else "N/A"
                    jan_str = f"₹{b_jan:.2f}" if b_jan is not None else "MRP Pending (Under Rate Contract — Not Sold at ₹0)"
                    sav_str = f" [लगभग {b_sav} बचत / ~{b_sav} indicative savings]" if b_sav else ""

                    if is_hindi:
                        lines.append(f"• लोकप्रिय ब्रांड: {b_name}")
                        lines.append(f"  - सक्रिय संरचना: {b_comp} (कोड: {b_code})")
                        lines.append(f"  - बाजार संदर्भ मूल्य: {mkt_str} vs जन औषधि MRP: {jan_str}{sav_str}")
                        if b_rule:
                            lines.append(f"  - चिकित्सकीय नियम: {b_rule}")
                    else:
                        lines.append(f"• Popular Brand(s): {b_name}")
                        lines.append(f"  - Active Generic Composition: {b_comp} (Code: {b_code})")
                        lines.append(f"  - Market Reference: {mkt_str} vs Jan Aushadhi MRP: {jan_str}{sav_str}")
                        if b_rule:
                            lines.append(f"  - Verification Rule: {b_rule}")
                lines.append("")

            # Medicines found
            if medicines:
                for idx, m in enumerate(medicines[:3], 1):
                    brand = m.get("brand_name")
                    generic = m.get("generic_name")
                    form = m.get("dosage_form")
                    pack = f"{m.get('pack_size')} {m.get('pack_unit')}"
                    pricing_status = m.get("pricing_status") or ""

                    price_info = m.get("latest_price")
                    if price_info and price_info.get("amount_inr") is not None:
                        price_str = f"₹{price_info.get('amount_inr')} ({price_info.get('price_type', 'MRP')})"
                    elif "under rate" in pricing_status.lower():
                        price_str = "Under Rate Contract (MRP Pending — Not Sold at ₹0 / Not Free)"
                    else:
                        price_str = "मूल्य सत्यापित नहीं / Price not verified"

                    if is_hindi:
                        lines.append(f"• {brand} ({form}, {pack})")
                        lines.append(f"  - सक्रिय घटक (Active Ingredients): {generic}")
                        lines.append(f"  - सत्यापित मूल्य: {price_str}")
                    else:
                        lines.append(f"• {brand} ({form}, {pack})")
                        lines.append(f"  - Active Ingredients: {generic}")
                        lines.append(f"  - Verified Price: {price_str}")

            # Alternatives found
            if alternatives:
                exact_matches = [a for a in alternatives if a.get("match_classification") == "EXACT_COMPOSITION_MATCH"]
                if exact_matches:
                    if is_hindi:
                        lines.append("\nसत्यापित समान घटक वाले किफायती विकल्प (Generic Alternatives):")
                    else:
                        lines.append("\nVerified Equivalent Formulations (Potential Generic Alternatives):")

                    for cand in exact_matches[:3]:
                        prod = cand.get("product", {})
                        p_brand = prod.get("brand_name")
                        p_jan = " (प्रधानमंत्री जन औषधि / PMBJP)" if prod.get("is_jan_aushadhi") else ""
                        p_pack = f"{prod.get('pack_size')} {prod.get('pack_unit')}"
                        p_price = prod.get("latest_price", {})
                        price_val = f"₹{p_price.get('amount_inr')}" if p_price else "Price not verified"
                        savings = cand.get("savings_percentage")
                        savings_str = f" [लगभग {savings}% बचत / ~{savings}% savings]" if savings else ""

                        lines.append(f"• {p_brand}{p_jan} - {p_pack} for {price_val}{savings_str}")

            # Check if query specified a strength (e.g. 500) that differs from the brand's standard formulation
            if extracted.strength and "500" in extracted.strength and medicines:
                first_med = medicines[0]
                brand_lower = first_med.get("brand_name", "").lower()
                if "omee" in brand_lower or "omez" in brand_lower:
                    if is_hindi:
                        lines.append("\nमात्रा (स्ट्रेंथ) संबंधी विशेष सूचना:")
                        lines.append("• ओमी (Omee) सामान्यतः ओमेप्राजोल 20mg (एसिडिटी / प्रोटॉन पंप इनहिबिटर) के रूप में आती है, 500mg में नहीं।")
                        lines.append("• यदि आप 500mg की एंटीबायोटिक या बुखार की दवा तलाश रहे थे, तो सामान्य 500mg विकल्पों में Amoxicillin 500mg (Mox 500), Paracetamol 500mg (Calpol 500) या Ciprofloxacin 500mg (Ciplox 500) शामिल हैं।")
                    else:
                        lines.append("\nNote on Formulation & Strength:")
                        lines.append("• Omee is standardly formulated as Omeprazole 20mg (a proton pump inhibitor for acidity and reflux), not 500mg.")
                        lines.append("• If you were seeking a 500mg antibiotic or fever medication, common formulations include Amoxicillin 500mg (Mox 500), Paracetamol 500mg (Calpol 500), or Ciprofloxacin 500mg (Ciplox 500).")

        # High risk or prescription advisory
        if is_hindi:
            lines.append("\nमहत्वपूर्ण चिकित्सकीय परामर्श:")
            lines.append("समान घटक होने पर भी अपनी निर्धारित दवा बदलने से पहले अपने डॉक्टर या फार्मासिस्ट से पुष्टि अवश्य कराएं।")
            lines.append(f"\nMedical Notice: {MANDATORY_DISCLAIMER}")
        else:
            lines.append("\nImportant Medical Guidance:")
            lines.append("Even with an identical composition match, always verify substitution with your doctor or pharmacist.")
            lines.append(f"\nMedical Notice: {MANDATORY_DISCLAIMER}")

        return "\n".join(lines)

    async def generate_grounded_response(
        self,
        user_message: str,
        language: str,
        extracted: ChatExtractedEntity,
        context_data: Dict[str, Any],
        conversation_history: List[ChatMessage],
    ) -> str:
        return self.format_deterministic_response(user_message, language, extracted, context_data)


class LLMService:
    """
    Factory and orchestrator for AI-powered queries with fallback resilience.
    """

    def __init__(self):
        if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            self.provider: BaseLLMProvider = GeminiLLMProvider(
                api_key=settings.GEMINI_API_KEY,
                model_name=settings.LLM_MODEL,
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
        else:
            self.provider: BaseLLMProvider = FallbackLLMProvider()

    async def process_chat(
        self,
        db: Session,
        message: str,
        language: str = "en",
        conversation_history: Optional[List[ChatMessage]] = None,
    ) -> ChatResponse:
        conversation_history = conversation_history or []
        warnings: List[str] = []
        sources: List[Dict[str, Any]] = []
        follow_up_questions: List[str] = []

        # 1. Emergency check
        is_emergency, emergency_msg = SafetyValidationService.check_emergency(message)
        if is_emergency:
            return ChatResponse(
                answer=emergency_msg,
                extracted_entities=ChatExtractedEntity(intent="emergency"),
                warnings=["Immediate emergency medical care required."],
                disclaimer=SafetyValidationService.get_standard_disclaimer(),
            )

        # 2. Unsafe prescription intent check
        is_unsafe, unsafe_msg = SafetyValidationService.check_unsafe_intent(message)
        if is_unsafe:
            warnings.append("Direct prescription modification request intercepted.")

        # 3. Entity extraction
        extracted = await self.provider.extract_query_entities(message)

        # 4. Check for ambiguous query
        if not extracted.medicine_name and not extracted.active_ingredients:
            return ChatResponse(
                answer=(
                    "Could you please specify the name of the medicine, brand (e.g. 'Dolo 650', 'Augmentin 625 Duo'), "
                    "or the active ingredient you are inquiring about? If you have the packaging, please mention the strength (e.g. 500mg) and form (tablet/syrup)."
                    if language == "en"
                    else "कृपया उस दवा का नाम, ब्रांड (जैसे 'Dolo 650') या सक्रिय घटक बताएं जिसके बारे में आप जानकारी चाहते हैं। कृपया स्ट्रेंथ (जैसे 500mg) और प्रकार (टैबलेट/सिरप) भी बताएं।"
                ),
                extracted_entities=extracted,
                follow_up_questions=[
                    "What is the exact brand name written on your prescription?",
                    "What is the strength (e.g. 500 mg, 650 mg)?",
                ],
                disclaimer=SafetyValidationService.get_standard_disclaimer(),
            )

        # 5. Retrieve factual records from backend database
        search_query = extracted.medicine_name or (extracted.active_ingredients[0] if extracted.active_ingredients else "")
        search_res = MedicineSearchService.search_medicines(db, query=search_query, limit=5)
        brand_res = BrandSearchService.search_brands(db, query=search_query, limit=3)

        structured_medicines = list(search_res.items)
        if brand_res.items:
            for b in brand_res.items:
                if b.linked_product and not any(m.id == b.linked_product.id for m in structured_medicines):
                    structured_medicines.append(b.linked_product)

        context_data: Dict[str, Any] = {
            "query": search_query,
            "medicines": [m.model_dump() for m in structured_medicines],
            "brand_lookups": [b.model_dump() for b in brand_res.items],
            "alternatives": [],
            "comparison": {},
        }
        structured_comparison = None

        # If alternatives requested or if we found a primary medicine
        if search_res.items:
            primary_med = search_res.items[0]

            # Collect source metadata
            if primary_med.latest_price and primary_med.latest_price.source_name:
                sources.append({
                    "name": primary_med.latest_price.source_name,
                    "url": primary_med.latest_price.source_url,
                    "verified_at": primary_med.latest_price.verified_at,
                    "status": primary_med.latest_price.verification_status,
                })

            alt_res = AlternativeMatchingService.match_alternatives(
                db, AlternativeSearchRequest(medicine_id=primary_med.id)
            )
            context_data["alternatives"] = [c.model_dump() for c in alt_res.candidates]

            # If user wants a comparison or multiple candidates found
            if extracted.intent == "compare" or len(search_res.items) >= 2:
                prod_ids = [m.id for m in search_res.items[:3]]
                comp_res = PriceComparisonService.compare_prices(
                    db,
                    PriceComparisonRequest(product_ids=prod_ids, reference_product_id=primary_med.id)
                )
                structured_comparison = comp_res
                context_data["comparison"] = comp_res.model_dump()

        # 6. Generate grounded response
        answer = await self.provider.generate_grounded_response(
            user_message=message,
            language=language,
            extracted=extracted,
            context_data=context_data,
            conversation_history=conversation_history,
        )

        if is_unsafe:
            answer = f"{unsafe_msg}\n\n---\n\n{answer}"

        # Follow up suggestions
        if search_res.items:
            follow_up_questions.append(f"Show Jan Aushadhi alternatives for {search_res.items[0].brand_name}")
            follow_up_questions.append(f"Compare verified prices for {search_res.items[0].brand_name}")

        return ChatResponse(
            answer=answer,
            extracted_entities=extracted,
            structured_medicines=structured_medicines,
            structured_comparison=structured_comparison,
            warnings=warnings,
            sources=sources,
            follow_up_questions=follow_up_questions,
            disclaimer=SafetyValidationService.get_standard_disclaimer(),
        )
