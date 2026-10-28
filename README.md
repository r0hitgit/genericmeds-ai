# GenericMeds AI (India)

**AI-Powered Generic Medicine Discovery, Active Ingredient Equivalence, and Price Comparison Platform**

---

## 1. Project Purpose & Mission

**GenericMeds AI** is designed to help middle-class and low-income Indian families discover affordable generic medicines, understand their active ingredients, compare verified medicine prices, and locate generic alternatives listed under the **Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)** and **National Pharmaceutical Pricing Authority (NPPA)** ceiling price orders.

### What GenericMeds AI Does:
- **Exact Composition Equivalence Matching**: Matches medicines only when active ingredients, strengths, dosage forms, routes of administration, and release profiles (e.g., immediate-release vs. sustained-release) match identically.
- **Price Comparison & Savings Calculator**: Automatically normalizes pack sizes (e.g., 10 tablets vs. 15 tablets) and computes exact unit savings and percentage savings against Maximum Retail Prices (MRP) and government-listed prices.
- **Jan Aushadhi Discovery**: Directly indexes formulations supplied through PMBI Jan Aushadhi Kendras.
- **Bilingual Grounded Medical Explanations**: Explains medical terms in simple English and Hindi (हिंदी).
- **Clinical Safety Guardrails**: Strictly flags high-risk drugs (insulin, warfarin, carbamazepine, injectables), prevents unsafe prescription changes, halts on emergency symptoms, and provides mandatory disclaimers.

> [!IMPORTANT]
> **Medical Disclaimer:** This tool is an informational and affordability discovery platform, **NOT** a doctor, diagnostic system, or prescription generator. Never start, stop, or substitute a prescribed medicine without consulting a qualified physician or licensed pharmacist.

---

## 2. System Architecture

The platform follows a modular, decoupled architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                          │
│  Interactive UI (Tailwind/HTML5) & REST API Clients / Mobile│
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
┌──────────────────────────────▼──────────────────────────────┐
│                  FastAPI Application (app/main.py)          │
│  Routes: /health, /medicines, /alternatives, /prices, /chat │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │                       │                       │
┌──────▼─────────────┐ ┌───────▼─────────────┐ ┌───────▼─────────────┐
│  Search & Equiv.   │ │   Price Comparator  │ │  Safety & Triage    │
│  Service           │ │   Service           │ │  Service            │
│  (MedicineSearch & │ │  (Unit normalization│ │  (Emergency triage,│
│   Alternatives)    │ │   & Stale tracking) │ │   High-risk flags)  │
└──────┬─────────────┘ └───────┬─────────────┘ └───────┬─────────────┘
       │                       │                       │
┌──────▼───────────────────────▼───────────────────────▼──────┐
│                    Data & Persistence Layer                 │
│   SQLAlchemy ORM (SQLite for Dev, PostgreSQL for Prod)      │
│   Entities: MedicineProduct, ActiveIngredient, Price, Source│
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│               Configurable AI / LLM Provider                │
│    Google Gemini API (httpx REST client) / Fallback Engine   │
│             System Prompt & Medical Grounding               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Project Structure

```
genericmeds-ai/
├── app/
│   ├── main.py                     # FastAPI application setup, middleware, static mount
│   ├── core/
│   │   ├── config.py               # Pydantic BaseSettings & environment loader
│   │   ├── database.py             # SQLAlchemy engine & session dependency
│   │   └── security.py             # Administrative API key authentication
│   ├── models/
│   │   ├── alias.py                # MedicineAlias model (brand, colloquial, phonetic, keywords)
│   │   ├── brand_lookup.py         # BrandGenericLookup model (popular Indian brands & PMBI codes)
│   │   ├── ingredient.py           # ActiveIngredient & ProductIngredient models
│   │   ├── kendra.py               # JanAushadhiKendra verified locator model
│   │   ├── medicine.py             # MedicineProduct model
│   │   ├── pricing.py              # MedicinePrice model
│   │   └── source.py               # DataSource registry model
│   ├── schemas/
│   │   ├── brand_lookup.py         # Brand lookup and search schemas
│   │   ├── catalogue.py            # Catalogue import, preview & status report schemas
│   │   ├── chat.py                 # Chat request & grounded response schemas
│   │   ├── kendra.py               # Kendra locator, distance & search schemas
│   │   ├── medicine.py             # Medicine product & alternative schemas
│   │   ├── pricing.py              # Price comparison request & item schemas
│   │   └── source.py               # Data source & admin import schemas
│   ├── api/
│   │   └── routes/
│   │       ├── admin.py            # Legacy admin import endpoints
│   │       ├── alternatives.py     # Generic alternative search endpoints
│   │       ├── brands.py           # Brand lookup & search endpoints
│   │       ├── catalogue.py        # Scaled catalogue import, preview & status endpoints
│   │       ├── chat.py             # AI conversational assistant endpoints
│   │       ├── health.py           # Health & readiness check endpoints
│   │       ├── kendras.py          # Jan Aushadhi Kendra GPS & filter endpoints
│   │       ├── medicines.py        # Layered medicine search & detail endpoints
│   │       ├── pricing.py          # Price comparison endpoints
│   │       └── sources.py          # Statutory data sources list
│   ├── services/
│   │   ├── alternatives.py         # Multi-attribute clinical equivalence engine
│   │   ├── brand_search.py         # Popular brand & PMBI generic lookup service
│   │   ├── catalogue_import.py     # High-throughput idempotent ingestion pipeline
│   │   ├── kendra_distance.py      # Haversine distance calculator
│   │   ├── kendra_search.py        # Verified Kendra location search engine
│   │   ├── medicine_search.py      # Layered exact, alias, and typo-tolerant search
│   │   ├── price_comparison.py     # Unit price normalizer & savings calculator
│   │   ├── safety_validation.py    # Emergency detection & high-risk flagger
│   │   └── source_verification.py  # Source synchronization tracking
│   ├── ai/
│   │   ├── llm_service.py          # Configurable LLM provider (Gemini + Offline fallback)
│   │   └── system_prompt.py        # Strict medical safety prompt & disclaimer
│   ├── static/
│   │   └── index.html              # Modern, responsive single-page web UI
│   └── tests/
│       ├── conftest.py             # In-memory test fixtures & database seeding
│       ├── test_alternatives.py    # Equivalence & combination matching tests
│       ├── test_chat.py            # Chat & language localization tests
│       ├── test_data_ingestion.py  # Malformed CSV & admin auth tests
│       ├── test_health.py          # Health status tests
│       ├── test_medicine_search.py # Brand, generic & ingredient search tests
│       ├── test_price_comparison.py# Savings calculation & stale price tests
│       └── test_safety.py          # Emergency triage & high-risk tests
├── data/
│   └── imports/
│       ├── branded_medicines_sample.csv   # Verified branded MRP catalogue
│       └── pmbi_jan_aushadhi_sample.csv   # Verified PMBI Jan Aushadhi catalogue
├── scripts/
│   ├── import_medicines.py         # CLI tool for custom CSV/Excel imports
│   └── seed_db.py                  # Initial database seeding script
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules
├── pytest.ini                      # Pytest runner configuration
├── requirements.txt                # Production dependencies
└── README.md                       # Comprehensive guide
```

---

## 4. Prerequisites

- **Python 3.11+** installed (check using `python3 --version` or `/opt/homebrew/bin/python3.11 --version` on macOS)
- **Git**
- Optional: PostgreSQL 14+ for production deployments

---

## 5. Installation & Setup Instructions

### Step 1: Clone or Navigate to the Workspace Directory
```bash
cd /Users/rohitverma/.gemini/antigravity/scratch/genericmeds-ai
```

### Step 2: Create a Python 3.11 Virtual Environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the `.env.example` template:
```bash
cp .env.example .env
```

Review or modify `.env`:
```ini
DATABASE_URL=sqlite:///./genericmeds.db
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-1.5-flash
ADMIN_API_KEY=genericmeds-admin-key-supersecret-change-in-production
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000
ENVIRONMENT=development
LOG_LEVEL=INFO
PRICE_STALE_DAYS=90
```
> *Note: If `GEMINI_API_KEY` is not provided or set to `mock`, GenericMeds AI automatically activates its deterministic fallback engine, maintaining 100% of search, equivalence, and price comparison features without crashing.*

### Step 5: Seed the Database with Verified Formulations
Run the database seeder to initialize tables and import the official PMBI Jan Aushadhi and branded market catalogues:
```bash
python scripts/seed_db.py
```

### Step 6: Start the FastAPI Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 6. Accessing the Application

- **Web User Interface**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Technical Specification**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 7. Example `curl` API Requests

### 1. Health Status
```bash
curl -s http://127.0.0.1:8000/health
```

### 2. Search Medicines by Name, Ingredient, or Brand
```bash
# Search for Dolo 650
curl -s "http://127.0.0.1:8000/api/v1/medicines/search?q=Dolo%20650"

# Search for Amoxicillin products in Jan Aushadhi only
curl -s "http://127.0.0.1:8000/api/v1/medicines/search?q=Amoxicillin&jan_aushadhi_only=true"
```

### 3. Discover Verified Generic Alternatives
```bash
# Find exact active ingredient alternatives for Augmentin 625 Duo (medicine ID: 18)
curl -s -X POST "http://127.0.0.1:8000/api/v1/alternatives/search" \
  -H "Content-Type: application/json" \
  -d '{"name": "Augmentin 625 Duo"}'
```

### 4. Compare Verified Prices & Calculate Savings
```bash
# Compare branded Augmentin 625 Duo with Jan Aushadhi Amoxyclav 625
curl -s -X POST "http://127.0.0.1:8000/api/v1/prices/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "product_ids": [18, 3],
    "reference_product_id": 18
  }'
```

### 5. Chat with GenericMeds AI (English & Hindi)
```bash
# English Query
curl -s -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the generic alternative to Augmentin 625 Duo?",
    "language": "en"
  }'

# Hindi Query
curl -s -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Dolo 650 का जेनेरिक विकल्प और मूल्य बताएं",
    "language": "hi"
  }'
```

### 6. Popular Brand Search & Jan Aushadhi Equivalence
```bash
# Search popular Indian brands (e.g., Amlong, Cilacar, Telma, Pan 40)
curl -s "http://127.0.0.1:8000/api/v1/brands/search?q=Amlong"

# Get details of specific brand lookup record (BRD-001)
curl -s "http://127.0.0.1:8000/api/v1/brands/BRD-001"
```

### 7. Catalogue Health, Data Freshness & Verification Status
```bash
# Public catalogue status report
curl -s "http://127.0.0.1:8000/api/v1/catalogue/status"
```

### 8. Admin Master Catalogue & Brand Ingestion (Preview & Import)
```bash
# 1. Generate validation preview (dry run audit of savings & code reconciliations)
curl -s -X POST "http://127.0.0.1:8000/api/v1/admin/catalogue/import/preview" \
  -H "X-Admin-Key: genericmeds-admin-key-supersecret-change-in-production"

# 2. Execute idempotent atomic database import
curl -s -X POST "http://127.0.0.1:8000/api/v1/admin/catalogue/import" \
  -H "X-Admin-Key: genericmeds-admin-key-supersecret-change-in-production" \
  -F "is_dry_run=false"
```

### 9. Find Nearby Jan Aushadhi Kendras (GPS & Manual Filter)
```bash
# Search by GPS Coordinates (e.g. Greater Noida/Alpha 2 with 10 km radius)
curl -s "http://127.0.0.1:8000/api/v1/kendras/nearby?latitude=28.4744&longitude=77.5040&radius_km=10"

# Manual filter by PIN code without GPS
curl -s "http://127.0.0.1:8000/api/v1/kendras/search?pin_code=201310"

# Manual filter by State and District
curl -s "http://127.0.0.1:8000/api/v1/kendras/search?state=UTTAR%20PRADESH&district=GAUTAM%20BUDDHA%20NAGAR"
```

---

## 7. React & Axios Modern Frontend

The frontend is a dedicated modern **React + Vite** single-page application communicating via **Axios** with the FastAPI backend. It features an aesthetic medical-grade design system with dark/light themes, bilingual localization (English / हिंदी), and glassmorphic UI.

### Frontend Features:
- **Medicine Search & Alternative Finder**: Instant brand and active ingredient search with exact composition match tags, unit price calculations, and alternative comparisons.
- **Price Comparison Sandbox**: Multi-medicine comparison matrix computing package price differences, per-unit savings, and potential statutory savings.
- **Jan Aushadhi Kendra Locator**: Dual GPS browser geolocation + 6-digit PIN code / District / State search, Haversine distance badges, 24x7 filters, direct phone call, and Google Maps directions.
- **68 Reconciled PMBI Therapeutic Groups**: Interactive classification browser with live product counts.
- **Clinical Dispensing & Safety Rules**: Schedule H/H1, Narrow Therapeutic Index (NTI), and Cold Chain protocols.
- **AI Medical Assistant**: RAG-grounded conversational chat powered by Google Gemini with suggested follow-up chips and emergency triage guardrails.
- **Statutory Data Freshness Registry**: Audit of PMBI, NPPA, and CDSCO data sync status.

### Running the Frontend:

#### 1. In Development Mode (Vite Dev Server + Proxy):
```bash
cd frontend
npm install
npm run dev
# Vite runs at http://localhost:5173 with automatic API proxy to http://127.0.0.1:8000
```

#### 2. Building for Production:
```bash
cd frontend
npm run build
# Automatically compiles into app/static/ and is served directly by FastAPI at http://127.0.0.1:8000/
```

---

## 8. Running the Automated Test Suite

The test suite covers 60 comprehensive test cases verifying exact ingredient matching, combination formulation validation, release type checks, savings mathematics, emergency triage, security authentication, Kendra geolocation distance calculation, and scale catalogue ingestion with idempotency.

Run pytest:
```bash
.venv/bin/pytest -v
```

---

## 9. Official Data Sources & Verification Workflow

GenericMeds AI integrates official Indian medicine data:

1. **PMBI Jan Aushadhi (PMBJP)**:
   - Official product portal: [https://www.pmbi.co.in/ProductList.aspx](https://www.pmbi.co.in/ProductList.aspx)
   - Store Locator: [https://janaushadhi.gov.in/](https://janaushadhi.gov.in/)
2. **NPPA Pharma Sahi Daam**:
   - Ceiling Price Search: [https://nppaipdms.gov.in/NPPA/PharmaSahiDaam/searchMedicine](https://nppaipdms.gov.in/NPPA/PharmaSahiDaam/searchMedicine)
3. **CDSCO Drug Approvals**:
   - Central Drug Standard Control Organisation: [https://www.cdscoonline.gov.in/CDSCO/cdscoDrugs](https://www.cdscoonline.gov.in/CDSCO/cdscoDrugs)

### Real-World Data Note:
Official Indian government medicine portals employ anti-scraping CAPTCHAs and do not expose unauthenticated public REST endpoints for high-throughput transactional queries. As mandated by healthcare data architecture best practices, GenericMeds AI uses an **administrator-controlled CSV/Excel ingestion pipeline** with cryptographic validation, deduplication, and timestamps, preventing corrupted or fabricated prices from entering the system.

---

## 10. Production Deployment Guide

1. **Database Migration to PostgreSQL**:
   Update `.env`:
   ```ini
   DATABASE_URL=postgresql://genericmeds_user:strong_password@db-host:5432/genericmeds_db
   ```
2. **Production ASGI Server**:
   Run with Gunicorn + Uvicorn workers:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
   ```
3. **Reverse Proxy (Nginx)**:
   Place Nginx in front of Gunicorn with SSL/TLS termination, HTTP/2, and rate-limiting on `/api/v1/chat` and `/api/v1/admin/import-medicines`.
4. **Environment Isolation**:
   Change `ADMIN_API_KEY` to a 64-character random token and restrict CORS origins to authorized frontend domains.
