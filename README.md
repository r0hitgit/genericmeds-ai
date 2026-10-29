# GenericMeds AI (India) 🇮🇳

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Deployed%20Live-black?style=for-the-badge&logo=vercel)](https://genericmeds-ai.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.3.1-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**AI-Powered Generic Medicine Discovery, Active Ingredient Equivalence, and PMBJP Price Comparison Platform**

---

## 🌐 Live Production Deployment

| Service | Live URL | Description |
|---|---|---|
| **Live Web Application** | **[https://genericmeds-ai.vercel.app](https://genericmeds-ai.vercel.app)** | Production frontend with instant search, Jan Aushadhi locator, and floating AI assistant |
| **Interactive API Docs (Swagger)** | **[https://genericmeds-ai.vercel.app/docs](https://genericmeds-ai.vercel.app/docs)** | Interactive OpenAPI Swagger UI for direct endpoint testing |
| **Alternative Technical Specs (ReDoc)** | **[https://genericmeds-ai.vercel.app/redoc](https://genericmeds-ai.vercel.app/redoc)** | Clean technical REST specification documentation |
| **System Health & Readiness** | **[https://genericmeds-ai.vercel.app/health](https://genericmeds-ai.vercel.app/health)** | Live operational health check, DB status, and active LLM provider |
| **GitHub Repository** | **[https://github.com/r0hitgit/genericmeds-ai](https://github.com/r0hitgit/genericmeds-ai)** | Open-source monorepo source code and full-stack implementation |

---

## 1. Project Purpose & Mission

**GenericMeds AI** is designed to empower Indian citizens, patients, and families to discover affordable generic medicines, understand their active salt formulations, calculate exact unit price savings, and locate accredited generic pharmacies operating under the **Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)** and **National Pharmaceutical Pricing Authority (NPPA)** ceiling price orders.

### Core Capabilities:
- **Exact Composition Equivalence Matching**: Algorithmic cross-matching strictly validating active salts, strength equivalence, dosage forms, routes of administration, and release profiles (immediate-release vs. sustained-release).
- **Price Comparison & Savings Calculator**: Automatically normalizes pack sizes (e.g., 10 tablets vs. 15 tablets) and computes exact unit savings and percentage savings against commercial Maximum Retail Prices (MRP).
- **Pan-India Jan Aushadhi Kendra Locator**: Dual GPS browser geolocation + instant 6-digit postal PIN code auto-detection (with official India Post API + district/state fallback).
- **Floating AI Clinical Assistant**: Dedicated floating widget in the bottom-right corner powered by Google Gemini and RAG grounded in statutory PMBI records.
- **Apple-Style Glassmorphism UI**: High-focus comparison modal with glassmorphic backdrop fading, keeping the global navigation bar and footer completely visible.
- **Bilingual Grounded Explanations**: Seamless switching between simple English and Hindi (हिंदी).
- **Clinical Safety Guardrails**: Strict warnings for high-risk Narrow Therapeutic Index (NTI) drugs (insulin, warfarin, carbamazepine, injectables), emergency symptom triage (112 / 108 helplines), and statutory medical advisories.

> [!IMPORTANT]
> **Medical Disclaimer:** This platform is an educational and affordability discovery platform, **NOT** a clinical diagnostic system or prescription generator. Never start, stop, or substitute prescribed medicine without consulting a registered medical practitioner or licensed pharmacist.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                          │
│   React 19 + Vite SPA, Vanilla CSS, Lucide Vector Icons     │
│   Hosted on Vercel Edge CDN (0ms Cold Starts, HTTP/2)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON via REST (/api/v1/...)
┌──────────────────────────────▼──────────────────────────────┐
│             FastAPI Application (app/main.py)               │
│   Vercel Serverless Function Runtime (api/index.py)         │
│   Endpoints: /medicines, /alternatives, /prices, /kendras   │
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
│   Pre-Seeded SQLite Database (2,500+ verified records)      │
│   Fast RAM/tmp partition mounting on Serverless Cold Starts  │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│               Configurable AI / LLM Provider                │
│   Google Gemini 1.5 Flash API + Deterministic RAG Fallback  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Project Structure

```text
genericmeds-ai/
├── api/
│   └── index.py                    # Vercel Serverless Python entrypoint
├── app/
│   ├── main.py                     # FastAPI application setup, CORS, static mounts
│   ├── core/
│   │   ├── config.py               # Pydantic BaseSettings, Vercel /tmp DB auto-mount
│   │   ├── database.py             # SQLAlchemy engine & session dependency
│   │   └── security.py             # Administrative API key authentication
│   ├── models/
│   │   ├── alias.py                # MedicineAlias model
│   │   ├── brand_lookup.py         # BrandGenericLookup model
│   │   ├── ingredient.py           # ActiveIngredient & ProductIngredient models
│   │   ├── kendra.py               # JanAushadhiKendra verified locator model
│   │   ├── medicine.py             # MedicineProduct model
│   │   ├── pricing.py              # MedicinePrice model
│   │   └── source.py               # DataSource registry model
│   ├── api/
│   │   └── routes/
│   │       ├── alternatives.py     # Generic alternative search endpoints
│   │       ├── brands.py           # Brand lookup & search endpoints
│   │       ├── catalogue.py        # Scaled catalogue import & status endpoints
│   │       ├── chat.py             # AI conversational assistant endpoints
│   │       ├── health.py           # Health & readiness check endpoints
│   │       ├── kendras.py          # Jan Aushadhi Kendra GPS & postal search
│   │       ├── medicines.py        # Layered medicine search & detail endpoints
│   │       ├── pricing.py          # Price comparison endpoints
│   │       └── sources.py          # Statutory data sources list
│   ├── services/
│   │   ├── alternatives.py         # Multi-attribute clinical equivalence engine
│   │   ├── brand_search.py         # Popular brand & PMBI generic lookup service
│   │   ├── kendra_search.py        # Kendra locator & postal search engine
│   │   ├── medicine_search.py      # Typo-tolerant medicine search engine
│   │   ├── pincode_service.py      # Pan-India India Post API & prefix cache
│   │   ├── price_comparison.py     # Unit price normalizer & savings calculator
│   │   └── safety_validation.py    # Emergency detection & high-risk flagger
│   ├── static/                     # Compiled production frontend assets & favicons
│   └── tests/                      # 60 automated test cases (100% passing)
├── data/
│   └── imports/                    # Official PMBJP & NPPA statutory catalogues
├── docs/
│   ├── MICROSERVICE_ARCHITECTURE.md
│   └── VERCEL_DEPLOYMENT_GUIDE.md  # Step-by-step Vercel deployment guide
├── frontend/                       # React 19 + Vite single-page application
│   ├── src/
│   │   ├── components/
│   │   │   ├── AIChatAssistant.jsx
│   │   │   ├── AlternativeComparisonModal.jsx
│   │   │   ├── BrandLogo.jsx
│   │   │   ├── ClinicalGuidelines.jsx
│   │   │   ├── ComparisonSandbox.jsx
│   │   │   ├── DataSources.jsx
│   │   │   ├── FloatingAIAssistant.jsx  # Bottom-right floating AI chat widget
│   │   │   ├── Footer.jsx
│   │   │   ├── Home.jsx
│   │   │   ├── KendraLocator.jsx
│   │   │   ├── Medicines.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── TherapeuticGroups.jsx
│   │   └── services/api.js
│   ├── package.json
│   └── vite.config.js
├── genericmeds.db                  # Pre-seeded SQLite database (2,500+ medicines)
├── package.json                    # Root build script for Vercel
├── requirements.txt                # Production Python dependencies
├── vercel.json                     # Vercel Edge CDN & Serverless rewrites
└── README.md
```

---

## 4. Local Installation & Development

### 1. Clone the Repository
```bash
git clone https://github.com/r0hitgit/genericmeds-ai.git
cd genericmeds-ai
```

### 2. Python Virtual Environment Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Variables
Create your local `.env`:
```bash
cp .env.example .env
```

| Key | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./genericmeds.db` | Local SQLite database URL |
| `LLM_PROVIDER` | `gemini` | `gemini` or `mock` deterministic fallback |
| `GEMINI_API_KEY` | *(Optional)* | Google Gemini API key |
| `LLM_MODEL` | `gemini-1.5-flash` | Gemini model variant |
| `ENVIRONMENT` | `development` | Set to `production` for deployments |

### 4. Start Backend Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Start Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
- Open [http://localhost:5173](http://localhost:5173) for hot-reloading development with automatic API proxying to `http://127.0.0.1:8000`.

---

## 5. Automated Test Suite (60/60 Passed)

GenericMeds AI includes 60 unit and integration tests verifying:
- Multi-salt active ingredient equivalence matching
- Schedule H, H1, and Narrow Therapeutic Index safety rules
- Price normalization and savings calculations
- Pan-India postal PIN code auto-detection
- Idempotent catalogue ingestion

Run pytest:
```bash
.venv/bin/pytest -v
```

Output:
```text
======================== 60 passed in 17.99s ========================
```

---

## 6. Example API Usage

### 1. Search Medicines
```bash
curl -s "https://genericmeds-ai.vercel.app/api/v1/medicines/search?q=Augmentin%20625&limit=2"
```

### 2. Find Verified Bioequivalent Alternatives
```bash
curl -s -X POST "https://genericmeds-ai.vercel.app/api/v1/alternatives/search" \
  -H "Content-Type: application/json" \
  -d '{"medicine_id": 2572, "max_candidates": 5}'
```

### 3. Compare Prices
```bash
curl -s -X POST "https://genericmeds-ai.vercel.app/api/v1/prices/compare" \
  -H "Content-Type: application/json" \
  -d '{"medicine_ids": [2572, 2573]}'
```

### 4. Auto-Detect Postal PIN Code (Pan-India)
```bash
# Lookup Gorakhpur (273004)
curl -s "https://genericmeds-ai.vercel.app/api/v1/kendras/lookup-pin?pincode=273004"
```

### 5. Chat with AI Clinical Assistant
```bash
curl -s -X POST "https://genericmeds-ai.vercel.app/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the generic alternative to Augmentin 625 Duo?",
    "language": "en"
  }'
```

---

## 7. Official Statutory Data Sources

- **Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)**: [https://janaushadhi.gov.in](https://janaushadhi.gov.in)
- **National Pharmaceutical Pricing Authority (NPPA)**: [https://nppaindia.nic.in](https://nppaindia.nic.in)
- **Central Drugs Standard Control Organisation (CDSCO)**: [https://cdsco.gov.in](https://cdsco.gov.in)
- **India Post Postal PIN Code Directory**: [https://api.postalpincode.in](https://api.postalpincode.in)

---

## 8. License

This project is licensed under the [MIT License](LICENSE).
Built with public healthcare accessibility for India in mind.
