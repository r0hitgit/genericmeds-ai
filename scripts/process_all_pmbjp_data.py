import os
import sys
import re
import csv
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


def clean_number(val):
    if val is None or pd.isna(val):
        return None
    s = str(val).strip().replace(",", "").replace("INR", "").replace("₹", "")
    try:
        f = float(s)
        return f if f > 0 else None
    except ValueError:
        return None


def parse_pack_info(pack_str: str):
    if not pack_str or pd.isna(pack_str):
        return 10.0, "tablets"
    s = str(pack_str).strip()

    m_s = re.match(r"^(\d+)(?:'s|\s*tablets|\s*capsules|\s*strips)?$", s, re.IGNORECASE)
    if m_s:
        return float(m_s.group(1)), "tablets"

    m_vol = re.match(r"^(\d+(?:\.\d+)?)\s*(g|gm|gms|ml|l|kg)\b", s, re.IGNORECASE)
    if m_vol:
        unit = m_vol.group(2).lower()
        if unit in ("g", "gm", "gms"):
            unit = "g"
        return float(m_vol.group(1)), unit

    m_unit = re.match(r"^(\d+)\s*(vial|kit|bottle|ampoule|sachet|unit|tube|pair)\b", s, re.IGNORECASE)
    if m_unit:
        return float(m_unit.group(1)), m_unit.group(2).lower()

    m_num = re.search(r"\b(\d+(?:\.\d+)?)\b", s)
    if m_num:
        return float(m_num.group(1)), "units"

    return 1.0, "unit"


def parse_dosage_form(prod_name: str, group_name: str = ""):
    lowered = prod_name.lower()
    if "tablet" in lowered or "tab" in lowered or "tablets" in lowered:
        return "Tablet", "Oral"
    if "capsule" in lowered or "cap" in lowered or "capsules" in lowered or "softgel" in lowered:
        return "Capsule", "Oral"
    if "injection" in lowered or "inj" in lowered or "infusion" in lowered:
        return "Injection", "Parenteral"
    if "eye drop" in lowered or "ophthalmic" in lowered or "eye/ear drop" in lowered:
        return "Eye Drop", "Ophthalmic"
    if "nasal spray" in lowered or "nasal drop" in lowered:
        return "Nasal Spray", "Nasal"
    if "inhaler" in lowered or "rotacap" in lowered or "respule" in lowered or "powder for inhalation" in lowered:
        return "Inhaler", "Inhalation"
    if "cream" in lowered:
        return "Cream", "Topical"
    if "ointment" in lowered:
        return "Ointment", "Topical"
    if "gel" in lowered:
        return "Gel", "Topical"
    if "syrup" in lowered or "suspension" in lowered or "oral solution" in lowered or "drops" in lowered or "elixir" in lowered:
        return "Syrup", "Oral"
    if "mouthwash" in lowered or "gargle" in lowered:
        return "Mouthwash", "Oral Topical"
    if "powder" in lowered or "sachet" in lowered or "granules" in lowered:
        return "Powder", "Oral"
    if "patch" in lowered:
        return "Patch", "Transdermal"
    if any(k in lowered for k in ["bandage", "gauze", "cotton", "plaster", "suture", "cannula", "syringe", "gloves", "needle", "belt", "collar", "tube", "crutch", "walker"]):
        return "Medical Device", "Medical Supply"
    return "Pharmaceutical", "Oral"


def parse_release_type(prod_name: str):
    lowered = prod_name.lower()
    if "sustained release" in lowered or "sustained-release" in lowered or "sr" in lowered.split():
        return "sustained-release"
    if "prolonged release" in lowered or "prolonged-release" in lowered or "pr" in lowered.split():
        return "prolonged-release"
    if "extended release" in lowered or "extended-release" in lowered or "er" in lowered.split() or "xr" in lowered.split():
        return "extended-release"
    if any(k in lowered for k in ["gastro-resistant", "gastro resistant", "enteric coated", "enteric-coated", "delayed release", "delayed-release"]):
        return "modified-release"
    if any(k in lowered for k in ["dispersible", "orodispersible", "mouth dissolving"]):
        return "dispersible"
    return "immediate-release"


def parse_prescription_status(therapeutic_group: str, prod_name: str):
    lowered_grp = therapeutic_group.lower()
    lowered_name = prod_name.lower()
    if any(k in lowered_grp for k in ["surgical", "consumables", "nutraceuticals", "ayurvedic", "derma care"]):
        return "OTC / Medical Supply"
    if "antibiotic" in lowered_grp:
        if any(h in lowered_name for h in ["azithromycin", "cefixime", "meropenem", "piperacillin", "linezolid"]):
            return "Schedule H1"
        return "Schedule H"
    if any(k in lowered_grp for k in ["central nervous system", "oncology", "cardiovascular", "anti-diabetic", "immunosuppressant"]):
        return "Schedule H"
    if "paracetamol" in lowered_name and not ("tramadol" in lowered_name or "codeine" in lowered_name):
        return "OTC"
    return "Schedule H"
