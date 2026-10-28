import re
from typing import List, Tuple, Dict, Any
from app.ai.system_prompt import MANDATORY_DISCLAIMER

# Critical medical emergency indicators
EMERGENCY_KEYWORDS = [
    r"\bchest pain\b",
    r"\bheart attack\b",
    r"\bcan't breathe\b",
    r"\bcannot breathe\b",
    r"\bshortness of breath\b",
    r"\bsevere breathlessness\b",
    r"\banaphylaxis\b",
    r"\bsevere allergic reaction\b",
    r"\bswelling of lips\b",
    r"\bthroat closing\b",
    r"\bpassed out\b",
    r"\bunconscious\b",
    r"\bloss of consciousness\b",
    r"\bstroke\b",
    r"\bparalysis\b",
    r"\bseizure\b",
    r"\bconvulsion\b",
    r"\bpoisoning\b",
    r"\boverdose\b",
    r"\bsuicide\b",
    r"\bkill myself\b",
    r"\bsevere bleeding\b",
    r"\bcoughing up blood\b",
]

# Unsafe requests asking for prescription changes, dosage adjustment, or medical decisions
PRESCRIPTION_CHANGE_PATTERNS = [
    r"\bcan i take\b.*\binstead\b",
    r"\bshould i stop taking\b",
    r"\bshould i change my dose\b",
    r"\bcan i double\b",
    r"\bprescribe me\b",
    r"\bwrite me a prescription\b",
    r"\bwhat dose should i take\b",
    r"\bhow many tablets should i take\b",
    r"\bdiagnose me\b",
    r"\bwhat disease do i have\b",
]

# High-risk active ingredients / drug classes requiring strict clinical supervision
HIGH_RISK_SUBSTANCES = {
    "insulin": "Insulin requires strict individual blood-glucose titration. Never switch insulin brands or formulations without endocrinologist/physician guidance.",
    "warfarin": "Narrow therapeutic index anticoagulant. Small changes in bioavailability can cause life-threatening haemorrhage or thrombosis. Requires INR monitoring.",
    "heparin": "Injectable anticoagulant with high bleeding risk.",
    "dabigatran": "Direct oral anticoagulant; strict dosage and renal function alignment required.",
    "rivaroxaban": "Direct oral anticoagulant; strict dosage and clinical verification required.",
    "apixaban": "Direct oral anticoagulant; strict clinical supervision required.",
    "phenytoin": "Antiepileptic with narrow therapeutic index and non-linear kinetics. Brand switching can trigger breakthrough seizures.",
    "carbamazepine": "Antiepileptic with narrow therapeutic index; switching requires serum level monitoring.",
    "sodium valproate": "Antiepileptic / mood stabilizer with strict therapeutic window.",
    "valproic acid": "Antiepileptic with strict therapeutic window.",
    "lithium": "Extremely narrow therapeutic window; toxicity risk. Serum levels must be monitored.",
    "digoxin": "Cardiac glycoside with narrow therapeutic index. Small pharmacokinetic variances can cause digitalis toxicity.",
    "cyclosporine": "Immunosuppressant with critical organ rejection risk upon bioequivalence variance.",
    "tacrolimus": "Immunosuppressant; brand/generic switching must be guided by transplant specialist.",
    "theophylline": "Narrow therapeutic index bronchodilator with high toxicity risk.",
    "levothyroxine": "Thyroid hormone with narrow therapeutic range; formulation switches require TSH re-testing.",
}

# High-risk dosage forms / release types
HIGH_RISK_RELEASE_TYPES = [
    "modified-release",
    "sustained-release",
    "extended-release",
    "controlled-release",
    "delayed-release",
    "gastro-resistant",
]


class SafetyValidationService:
    """
    Validates clinical safety rules, emergency triage, and prescription warnings.
    Both backend endpoints and AI service query this engine.
    """

    @classmethod
    def check_emergency(cls, text: str) -> Tuple[bool, str]:
        """
        Detects medical emergencies. If detected, returns True and an immediate triage message.
        """
        lowered = text.lower()
        for pattern in EMERGENCY_KEYWORDS:
            if re.search(pattern, lowered):
                return True, (
                    "⚠️ MEDICAL EMERGENCY DETECTED: If you or someone near you is experiencing severe symptoms "
                    "(such as acute chest pain, severe breathlessness, loss of consciousness, anaphylaxis, seizure, "
                    "or poisoning), STOP USING THIS TOOL and immediately seek emergency medical care.\n\n"
                    "• In India, call 112 (National Emergency) or 108 (Ambulance) right away.\n"
                    "• Go to the nearest hospital casualty / emergency department immediately.\n\n"
                    "This tool does not handle emergency medical triage."
                )
        return False, ""

    @classmethod
    def check_unsafe_intent(cls, text: str) -> Tuple[bool, str]:
        """
        Detects if user is asking for direct medical diagnosis, dosage prescription, or stopping/changing medication.
        """
        lowered = text.lower()
        for pattern in PRESCRIPTION_CHANGE_PATTERNS:
            if re.search(pattern, lowered):
                return True, (
                    "⚠️ MEDICAL SAFETY CAUTION: GenericMeds AI cannot prescribe medicines, diagnose conditions, "
                    "or recommend changing or stopping your medication.\n\n"
                    "Dosage adjustments and switching prescribed therapies must ALWAYS be confirmed with your treating "
                    "doctor or a licensed pharmacist. We can show you verified generic formulations and prices so you "
                    "can ask your doctor: 'Is an exact generic alternative suitable for my prescription?'"
                )
        return False, ""

    @classmethod
    def check_high_risk_product(cls, ingredient_names: List[str], release_type: str, dosage_form: str) -> Tuple[bool, List[str]]:
        """
        Evaluates whether a medicine product or formulation belongs to a high-risk category.
        """
        is_high_risk = False
        reasons: List[str] = []

        # Check substances
        for ing in ingredient_names:
            ing_lower = ing.lower()
            for substance, warning in HIGH_RISK_SUBSTANCES.items():
                if substance in ing_lower:
                    is_high_risk = True
                    reasons.append(f"High-Risk Medicine ({substance.title()}): {warning}")

        # Check release types
        rel_lower = release_type.lower()
        if any(h in rel_lower for h in HIGH_RISK_RELEASE_TYPES):
            is_high_risk = True
            reasons.append(
                f"Modified Release Formulation ({release_type}): Bioavailability and dissolution profiles vary significantly between manufacturers. "
                "Do not substitute without explicit physician authorization."
            )

        # Check injectables
        if "injection" in dosage_form.lower() or "infusion" in dosage_form.lower():
            is_high_risk = True
            reasons.append(
                "Parenteral / Injectable Formulation: Injections require strict sterile compounding, proper cold-chain storage, and clinical supervision."
            )

        return is_high_risk, reasons

    @classmethod
    def get_standard_disclaimer(cls) -> str:
        return MANDATORY_DISCLAIMER
