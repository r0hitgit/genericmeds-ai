import os
import sys
import csv
import re
import pandas as pd
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, init_db
from app.models.source import DataSource
from app.models.ingredient import ActiveIngredient, ProductIngredient
from app.models.medicine import MedicineProduct
from app.models.pricing import MedicinePrice
from app.models.kendra import JanAushadhiKendra
from app.services.source_verification import SourceVerificationService
from app.services.data_ingestion import DataIngestionService
from scripts.process_all_pmbjp_data import clean_number, parse_pack_info, parse_dosage_form, parse_release_type, parse_prescription_status

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMPORTS_DIR = os.path.join(BASE_DIR, "data", "imports")
os.makedirs(IMPORTS_DIR, exist_ok=True)

# 1. Kendra Directory Data
KENDRA_DATA = [
    {
        "kendra_code": "PMBJK-DEL-01",
        "hospital_name": "AIIMS New Delhi In-Campus Pradhan Mantri Bhartiya Janaushadhi Kendra",
        "city_state": "Delhi NCR (New Delhi)",
        "location": "Near Rajkumari Amrit Kaur (RAK) OPD Block & Masjid Moth Campus, AIIMS, Ansari Nagar, New Delhi",
        "operating_hours": "24x7 Operations (3 Shifts)",
        "portfolio_scope": "Full PMBI Basket: 2,439 Listed Products across 68 Therapeutic Groups (Oncology, Cardiac, Neuro, Antibiotics, Insulins, Surgical Consumables)",
        "dispensing_rules": "Dispenses against valid generic prescriptions from AIIMS/government/private doctors; substitution decisions must be approved by a doctor or registered pharmacist",
        "helpline_url": "Toll-Free: 1800-180-8080 | Jan Aushadhi Sugam App | https://janaushadhi.gov.in/",
        "is_24x7": True,
    },
    {
        "kendra_code": "PMBJK-DEL-02",
        "hospital_name": "Safdarjung Hospital & VMMC In-Campus Jan Aushadhi Kendra",
        "city_state": "Delhi NCR (New Delhi)",
        "location": "OPD Building Ground Floor, Safdarjung Hospital, Ring Road, New Delhi",
        "operating_hours": "24x7 Operations",
        "portfolio_scope": "Surgical Consumables (314 items), Parenteral Antibiotics, Chronic Cardiac, Anti-Diabetic & Orthopedic Braces/Supports",
        "dispensing_rules": "Walk-in counter adjacent to Main OPD Pharmacy; printed MRP is uniform nationwide; zero-MRP items on PMBI list are under rate contract and not sold",
        "helpline_url": "https://www.pmbi.co.in/ProductList.aspx | Helpline: 1800-180-8080",
        "is_24x7": True,
    },
    {
        "kendra_code": "PMBJK-DEL-03",
        "hospital_name": "Dr. Ram Manohar Lohia (RML) Hospital & Lady Hardinge (LHMC) Jan Aushadhi Kendras",
        "city_state": "Delhi NCR (Central Delhi)",
        "location": "RML Hospital Gate No. 1 / OPD Block, Baba Kharak Singh Marg & LHMC Shaheed Bhagat Singh Marg, New Delhi",
        "operating_hours": "08:00 AM - 09:00 PM (24x7 Emergency Counter at RML)",
        "portfolio_scope": "Central Government Hospital OPD medicines, Cardiovascular, Neurology, Urology, Insulins & Home Diagnostic Devices",
        "dispensing_rules": "Schedule H/H1 drugs strictly require a Registered Medical Practitioner (RMP) prescription; retain Kendra GST invoice for CGHS/ECHS reimbursement",
        "helpline_url": "https://janaushadhi.gov.in/",
        "is_24x7": True,
    },
    {
        "kendra_code": "PMBJK-CHD-01",
        "hospital_name": "PGIMER Chandigarh In-Campus Jan Aushadhi Kendras (New OPD & Nehru Hospital)",
        "city_state": "Northern Hub (Chandigarh)",
        "location": "New OPD Block Ground Floor & Nehru Hospital Extension, PGIMER, Sector 12, Chandigarh",
        "operating_hours": "24x7 Operations",
        "portfolio_scope": "Oncology (88 items), Immunosuppressants (14 items), Parenteral Antibiotics & Surgical Dressings/Sutures",
        "dispensing_rules": "Accepts PGIMER generic OPD prescriptions; pharmacists verify strength, dosage form, and pack size before dispensing",
        "helpline_url": "https://pgimer.edu.in/ | PMBI Toll-Free: 1800-180-8080",
        "is_24x7": True,
    },
    {
        "kendra_code": "PMBJK-MUM-01",
        "hospital_name": "KEM Hospital, Lokmanya Tilak (Sion) & JJ Hospital Jan Aushadhi Network",
        "city_state": "Western Hub (Mumbai, Maharashtra)",
        "location": "Parel / Byculla / Sion Hospital Campus & Dadar-Parel Oncology Corridor (near Tata Memorial Hospital), Mumbai",
        "operating_hours": "08:00 AM - 10:00 PM",
        "portfolio_scope": "Oncology, Supportive Care, Cardiovascular, Anti-TB, Antiretrovirals & Nutraceuticals",
        "dispensing_rules": "Over 15,057+ verified Kendras (as of Feb 2025 Parliament reply) expanding to 18,000+ nationwide via Jan Aushadhi Sugam locator",
        "helpline_url": "https://janaushadhi.gov.in/",
        "is_24x7": False,
    },
    {
        "kendra_code": "PMBJK-CHE-01",
        "hospital_name": "Rajiv Gandhi Govt General Hospital (RGGGH) & Tamil Nadu Medical Hub Jan Aushadhi Kendras",
        "city_state": "Southern Hub (Chennai, Vellore, Coimbatore, Madurai)",
        "location": "Park Town (Opposite Chennai Central), Greams Road Corridor, Vellore Ida Scudder Rd & Coimbatore Avinashi Rd",
        "operating_hours": "08:00 AM - 09:30 PM",
        "portfolio_scope": "Chronic Cardiac, Anti-Diabetic, Nephrology/Urology, Ophthalmic Drops, Hernia Belts, Knee Caps & Surgical Tapes",
        "dispensing_rules": "International patients purchasing post-discharge refills must carry their treating doctor's prescription and itemised Kendra invoice for customs",
        "helpline_url": "https://janaushadhi.gov.in/",
        "is_24x7": False,
    },
    {
        "kendra_code": "PMBJK-BLR-01",
        "hospital_name": "Victoria Hospital (BMCRI), Kidwai Memorial Cancer Institute & Jayadeva Cardiac Hub Kendras",
        "city_state": "Southern Hub (Bengaluru, Karnataka)",
        "location": "Victoria Hospital Campus (KR Market), Kidwai Campus (M.H. Marigowda Rd) & Bannerghatta Rd / Bommasandra Corridors",
        "operating_hours": "08:00 AM - 09:30 PM",
        "portfolio_scope": "Cardiovascular (304 items), Central Nervous System (301 items), Oncology (88 items) & Surgical Consumables",
        "dispensing_rules": "WHO-GMP manufactured & NABL batch-tested generic medicines supplied by Pharmaceuticals & Medical Devices Bureau of India (PMBI)",
        "helpline_url": "https://www.pmbi.co.in/",
        "is_24x7": False,
    },
    {
        "kendra_code": "PMBJK-HYD-01",
        "hospital_name": "Osmania General Hospital, NIMS (Nizam's Institute) & Gandhi Hospital Jan Aushadhi Kendras",
        "city_state": "South-Central Hub (Hyderabad, Telangana)",
        "location": "NIMS Punjagutta Campus, Afzalgunj & Secunderabad Corridors, Hyderabad",
        "operating_hours": "08:00 AM - 09:30 PM",
        "portfolio_scope": "Gastrointestinal (119 items), Hepato-Protective (17 items), Orthopedics (35 items) & Surgical Consumables",
        "dispensing_rules": "Every batch passes NABL laboratory quality testing prior to release from PMBI Central Warehouses (Gurugram, Chennai, Guwahati, Surat, Bengaluru)",
        "helpline_url": "https://www.pmbi.co.in/",
        "is_24x7": False,
    },
    {
        "kendra_code": "PMBJK-KOL-01",
        "hospital_name": "SSKM (IPGMER), Medical College Kolkata & Rajarhat Cancer Corridor Jan Aushadhi Kendras",
        "city_state": "Eastern Hub (Kolkata, West Bengal)",
        "location": "AJC Bose Road (SSKM), College Street & New Town/Mukundapur Medical Corridors, Kolkata",
        "operating_hours": "08:00 AM - 09:30 PM",
        "portfolio_scope": "Full Chronic & Acute Basket serving Eastern India, North-East India, Bhutan & Bangladesh cross-border patients",
        "dispensing_rules": "Pharmacist consultation required for verifying pack sizes (e.g., 6's vs 10's vs 100's bottles) against physician prescription",
        "helpline_url": "https://janaushadhi.gov.in/",
        "is_24x7": False,
    },
    {
        "kendra_code": "PMBJK-KOC-01",
        "hospital_name": "Ernakulam General Hospital, Govt Medical College Trivandrum & Kerala PMBJK Network",
        "city_state": "Southern Hub (Kochi & Trivandrum, Kerala)",
        "location": "Hospital Road (Ernakulam), Medical College Ulloor Rd (Trivandrum) & Edappally/Ponekkara Corridors",
        "operating_hours": "08:00 AM - 09:00 PM",
        "portfolio_scope": "Cardiology, Endocrinology/Thyroid, Diabetic Care, Ophthalmology & Geriatric Consumables (Swabhiman Diapers, Glucometers)",
        "dispensing_rules": "Kerala holds the 2nd highest state concentration of Kendras (1,528+ Kendras per data.gov.in RS Question 3374)",
        "helpline_url": "https://janaushadhi.gov.in/",
        "is_24x7": False,
    },
]

# 2. Flagship 39 Branded Market Reference Comparisons
FLAGSHIP_COMPARISONS = [
    {"code": "PMBI-410", "category": "Oncology", "name": "Trastuzumab Inj 440mg with WFI", "pack": "1 Vial", "pmbi_price": 14062.50, "market_price": 52000.0, "brand_ref": "Herclon / Vivitra 440mg", "savings_pct": 72.96},
    {"code": "PMBI-2258", "category": "Oncology", "name": "Rituximab 500mg / 50ml Injection", "pack": "50ml Vial", "pmbi_price": 10968.75, "market_price": 38000.0, "brand_ref": "MabThera / Ristova 500mg", "savings_pct": 71.13},
    {"code": "PMBI-159", "category": "Oncology", "name": "Gemcitabine Injection IP 1000mg", "pack": "1 Vial", "pmbi_price": 783.75, "market_price": 3800.0, "brand_ref": "Gemzar / Oncogem 1000mg", "savings_pct": 79.38},
    {"code": "PMBI-997", "category": "Oncology", "name": "Paclitaxel Injection IP 100mg (6mg/ml)", "pack": "1 Vial", "pmbi_price": 506.25, "market_price": 3200.0, "brand_ref": "Taxol / Intaxel 100mg", "savings_pct": 84.18},
    {"code": "PMBI-156", "category": "Oncology", "name": "Doxorubicin Injection IP 50mg", "pack": "1 Vial", "pmbi_price": 281.25, "market_price": 1450.0, "brand_ref": "Adriamycin / Doxoruba 50mg", "savings_pct": 80.60},
    {"code": "PMBI-916", "category": "Oncology", "name": "Imatinib Mesylate Tablets IP 400mg", "pack": "10's", "pmbi_price": 210.94, "market_price": 1650.0, "brand_ref": "Glivec / Veenat 400mg", "savings_pct": 87.22},
    {"code": "PMBI-154", "category": "Oncology", "name": "Cisplatin Injection 50mg / 50ml", "pack": "1 Vial", "pmbi_price": 160.88, "market_price": 620.0, "brand_ref": "Cisplat / Kemoplat 50mg", "savings_pct": 74.05},
    {"code": "PMBI-935", "category": "Oncology", "name": "Letrozole Tablets IP 2.5mg", "pack": "10's", "pmbi_price": 31.88, "market_price": 210.0, "brand_ref": "Femara / Letroz 2.5mg", "savings_pct": 84.82},
    {"code": "PMBI-164", "category": "Oncology", "name": "Tamoxifen Citrate Tablets IP 20mg", "pack": "10's", "pmbi_price": 15.00, "market_price": 85.0, "brand_ref": "Nolvadex / Tamodex 20mg", "savings_pct": 82.35},
    {"code": "PMBI-276", "category": "Cardiovascular", "name": "Enoxaparin Injection IP 40mg / 0.4ml", "pack": "0.4 ml", "pmbi_price": 187.00, "market_price": 540.0, "brand_ref": "Clexane / Lovenox 40mg", "savings_pct": 65.37},
    {"code": "PMBI-1392", "category": "Cardiovascular", "name": "Aspirin Gastro Resistant 75mg and Rosuvastatin 10mg Capsules IP", "pack": "10's", "pmbi_price": 38.16, "market_price": 195.0, "brand_ref": "Rosuvas A 10mg / Rozucor A", "savings_pct": 80.43},
    {"code": "PMBI-759", "category": "Cardiovascular", "name": "Rosuvastatin Tablets IP 10mg", "pack": "15's", "pmbi_price": 19.28, "market_price": 210.0, "brand_ref": "Rosuvas 10 / Crestor 10", "savings_pct": 90.82},
    {"code": "PMBI-269", "category": "Cardiovascular", "name": "Clopidogrel Tablets IP 75mg", "pack": "10's", "pmbi_price": 19.28, "market_price": 115.0, "brand_ref": "Plavix / Deplatt 75mg", "savings_pct": 83.23},
    {"code": "PMBI-267", "category": "Cardiovascular", "name": "Atorvastatin Tablets IP 20mg", "pack": "10's", "pmbi_price": 12.47, "market_price": 145.0, "brand_ref": "Lipitor / Atorva 20mg", "savings_pct": 91.40},
    {"code": "PMBI-300", "category": "Cardiovascular", "name": "Telmisartan Tablets IP 40mg", "pack": "10's", "pmbi_price": 12.38, "market_price": 95.0, "brand_ref": "Micardis / Telma 40mg", "savings_pct": 86.97},
    {"code": "PMBI-264", "category": "Cardiovascular", "name": "Amlodipine Tablets IP 5mg", "pack": "10's", "pmbi_price": 5.68, "market_price": 55.0, "brand_ref": "Norvasc / Amlopres 5mg", "savings_pct": 89.67},
    {"code": "PMBI-363", "category": "Anti-Diabetic", "name": "Insulin Glargine Injection IP 100 IU per ml", "pack": "3 ml", "pmbi_price": 340.00, "market_price": 890.0, "brand_ref": "Lantus 100IU Cartridge", "savings_pct": 61.80},
    {"code": "PMBI-143", "category": "Anti-Diabetic", "name": "Insulin Injection IP 40 IU per ml (Insulin Human Soluble 30% and Isophane 70%)", "pack": "10 ml", "pmbi_price": 91.35, "market_price": 245.0, "brand_ref": "Human Mixtard 30/70 40IU Vial", "savings_pct": 62.71},
    {"code": "PMBI-1802", "category": "Anti-Diabetic", "name": "Sitagliptin Phosphate 50mg & Metformin Hydrochloride 500mg Tablets", "pack": "10's", "pmbi_price": 56.72, "market_price": 240.0, "brand_ref": "Janumet 50/500mg", "savings_pct": 76.37},
    {"code": "PMBI-34", "category": "Anti-Diabetic", "name": "Metformin Hydrochloride Prolonged-release 500mg and Glimepiride 2mg Tablets IP", "pack": "15's", "pmbi_price": 27.23, "market_price": 165.0, "brand_ref": "Amaryl M 2mg / Glycomet GP 2", "savings_pct": 83.50},
    {"code": "PMBI-1461", "category": "Anti-Diabetic", "name": "Vildagliptin Tablets IP 50mg", "pack": "15's", "pmbi_price": 20.63, "market_price": 180.0, "brand_ref": "Galvus 50mg / Jalra 50mg", "savings_pct": 88.54},
    {"code": "PMBI-145", "category": "Anti-Diabetic", "name": "Metformin Hydrochloride Tablets IP 500mg", "pack": "10's", "pmbi_price": 6.81, "market_price": 35.0, "brand_ref": "Glucophage / Glycomet 500", "savings_pct": 80.54},
    {"code": "PMBI-396", "category": "Anti-Fungal", "name": "Liposomal Amphotericin B Injection 50 mg per Vial", "pack": "20 ml", "pmbi_price": 2700.00, "market_price": 8500.0, "brand_ref": "AmBisome 50mg Vial", "savings_pct": 68.24},
    {"code": "PMBI-97", "category": "Antibiotics", "name": "Meropenem Injection IP 1 g", "pack": "Vial", "pmbi_price": 221.25, "market_price": 1350.0, "brand_ref": "Meronem 1g / Mepronem", "savings_pct": 83.61},
    {"code": "PMBI-103", "category": "Antibiotics", "name": "Piperacillin 4000mg and Tazobactum 500mg Injection IP", "pack": "Vial", "pmbi_price": 114.38, "market_price": 520.0, "brand_ref": "Tazocin 4.5g / Pipzo 4.5g", "savings_pct": 78.00},
    {"code": "PMBI-39", "category": "Antibiotics", "name": "Amoxycillin 500mg and Potassium Clavulanate 125mg Tablets IP", "pack": "6's", "pmbi_price": 57.85, "market_price": 205.0, "brand_ref": "Augmentin 625 Duo / Moxikind CV", "savings_pct": 71.78},
    {"code": "PMBI-55", "category": "Antibiotics", "name": "Cefixime Tablets IP 200 mg", "pack": "10's", "pmbi_price": 52.55, "market_price": 120.0, "brand_ref": "Zifi 200 / Taxim-O 200", "savings_pct": 56.21},
    {"code": "PMBI-72", "category": "Antibiotics", "name": "Azithromycin Tablets IP 500 mg", "pack": "3's", "pmbi_price": 39.38, "market_price": 115.0, "brand_ref": "Zithromax / Azee 500", "savings_pct": 65.76},
    {"code": "PMBI-212", "category": "Gastrointestinal", "name": "Pantoprazole Gastro Resistant Tablets IP 40 mg", "pack": "10's", "pmbi_price": 12.47, "market_price": 135.0, "brand_ref": "Pantocid 40 / Pan 40", "savings_pct": 90.76},
    {"code": "PMBI-1", "category": "Analgesic", "name": "Aceclofenac 100mg and Paracetamol 325mg Tablets", "pack": "10's", "pmbi_price": 10.32, "market_price": 95.0, "brand_ref": "Zerodol-P / Hifenac-P", "savings_pct": 89.14},
    {"code": "PMBI-23", "category": "Analgesic", "name": "Paracetamol Tablets IP 500 mg", "pack": "10's", "pmbi_price": 6.56, "market_price": 15.0, "brand_ref": "Calpol 500 / Crocin 500", "savings_pct": 56.27},
    {"code": "PMBI-466", "category": "Hepato-Protective", "name": "Ursodeoxycholic Acid Tablets IP 300 mg", "pack": "10's", "pmbi_price": 176.66, "market_price": 480.0, "brand_ref": "Udiliv 300 / Ursochol 300", "savings_pct": 63.20},
    {"code": "PMBI-332", "category": "Anti-Thyroid", "name": "Thyroxine Sodium Tablets IP 100 mcg", "pack": "100's", "pmbi_price": 70.33, "market_price": 210.0, "brand_ref": "Thyronorm 100 / Eltroxin 100", "savings_pct": 66.51},
    {"code": "PMBI-8133", "category": "Surgical / Device", "name": "Digital Blood Pressure Instrument ( 100% mercury free)", "pack": "1 Kit", "pmbi_price": 937.50, "market_price": 1699.0, "brand_ref": "Omron Digital BP Monitor", "savings_pct": 44.82},
    {"code": "PMBI-8136", "category": "Surgical / Device", "name": "Elecrical Nebulizer Machine", "pack": "1 Unit", "pmbi_price": 750.00, "market_price": 1149.0, "brand_ref": "Philips / Dr Trust Nebulizer", "savings_pct": 34.73},
    {"code": "PMBI-8122", "category": "Surgical / Device", "name": "GLUCOMETER DIGITAL (1 glucometer, 25 strips, 25 lancets,1 lancing device,1 battery 3V, Warranty card)", "pack": "1 Kit", "pmbi_price": 492.19, "market_price": 1250.0, "brand_ref": "Accu-Chek Active Glucometer Kit", "savings_pct": 60.62},
    {"code": "PMBI-8172", "category": "Surgical / Device", "name": "Pulse Oximeter", "pack": "1 Unit", "pmbi_price": 464.07, "market_price": 1399.0, "brand_ref": "Dr Morepen / Beurer Oximeter", "savings_pct": 66.83},
    {"code": "PMBI-9028", "category": "Surgical / Device", "name": "Medical Steam Vaporizer", "pack": "1 Unit", "pmbi_price": 234.38, "market_price": 450.0, "brand_ref": "Vicks / Dr Trust Steam Vaporizer", "savings_pct": 47.92},
    {"code": "PMBI-8128", "category": "Surgical / Device", "name": "Medical Digital Thermometer", "pack": "1 Unit", "pmbi_price": 88.99, "market_price": 165.0, "brand_ref": "Omron / Dr Morepen Digital Thermometer", "savings_pct": 46.07},
]
