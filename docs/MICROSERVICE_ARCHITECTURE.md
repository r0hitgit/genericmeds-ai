# GenericMeds AI: Enterprise Healthcare Microservice Architecture & Integration Guide

> **Service Name:** `genericmeds-service`  
> **Domain:** Healthcare Affordability, Statutory Drug Equivalence & Geospatial Pharmacy Discovery  
> **Target Ecosystem:** Hospital Information Systems (HIS), Electronic Health Records (EHR), Telemedicine Platforms, and Healthcare Superapps in India.

---

## 1. Executive Overview & Microservice Mission

**GenericMeds AI** is engineered as an autonomous, high-throughput, low-latency microservice designed to integrate into large-scale healthcare platforms. Its core mission is to eliminate information asymmetry in Indian pharmaceutical pricing by providing real-time active ingredient matching, verified statutory price comparisons under the **Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)** and **National Pharmaceutical Pricing Authority (NPPA)**, and GPS-enabled Jan Aushadhi Kendra store discovery.

### Key Capabilities Provided to the Parent System
1. **Drug Composition & Equivalence Engine:** Rigorous multi-ingredient, strength, route, and release-characteristic equivalence matching.
2. **Normalized Price Comparator:** Unit-price normalization ($\text{Price} / \text{Quantity}$) and verifiable savings calculations.
3. **Geospatial Kendra Locator:** High-speed bounding box and Haversine distance discovery for over 15,000+ government generic pharmacies with directions URLs.
4. **Clinical Safety & Medical Guardrails:** Statutory Schedule H/H1 tagging, narrow therapeutic index warnings, cold-chain handling rules, and automated emergency triage (112 / 108).
5. **RAG-Grounded Multilingual Assistant:** LLM provider abstraction (Google Gemini API with deterministic rule-based fallback) explaining pharmacopeial concepts in English and Hindi.

---

## 2. Microservice Integration Architecture

### High-Level Distributed System Context

```mermaid
flowchart TD
    subgraph Clients["Client Tier (Web, iOS, Android, Hospital Kiosks)"]
        Web[Hospital Web Portal]
        App[Patient Mobile App]
        DoctorApp[Doctor Prescription EHR App]
    end

    subgraph GatewayTier["API Gateway & Security Tier"]
        GW[Kong / Traefik / Envoy API Gateway]
        IAM[Keycloak / OAuth2 Auth Service]
    end

    subgraph MajorEcosystem["Major Healthcare System Services"]
        EHR[EHR & E-Prescription Service]
        Billing[Hospital Billing & Discharge Service]
        Telemed[Teleconsultation Service]
        EventBus[Message Broker / Kafka / RabbitMQ]
    end

    subgraph GenericMedsService["GenericMeds AI Microservice (Containerized)"]
        API[FastAPI Gateway Layer]
        AuthMid[X-Admin-Key & JWT Middleware]
        
        subgraph CoreEngines["Domain Services"]
            SearchEng[Medicine Search Service]
            EquivEng[Equivalence & Salt Engine]
            PriceComp[Price Comparator & Normalizer]
            KendraEng[Geospatial Kendra Locator]
            SafetyEng[Clinical Guardrails & Triage]
            LLMEng[RAG LLM & Gemini Adapter]
        end
        
        subgraph DataStores["Storage & Caching Layer"]
            DB[(PostgreSQL / SQLite Database)]
            Redis[(Redis Distributed Cache)]
        end
    end

    subgraph ExternalServices["External Regulators & Providers"]
        PMBI[PMBI Statutory Data Feeds]
        NPPA[NPPA Pharma Sahi Daam]
        GeminiAPI[Google Gemini 1.5 Flash API]
        OSM[OpenStreetMap / Google Maps API]
    end

    %% Client flows
    Clients -->|HTTPS / REST| GW
    GW -->|Validate Token| IAM
    GW -->|/api/v1/prescriptions| EHR
    GW -->|/api/v1/medicines/*| API
    GW -->|/api/v1/kendras/*| API

    %% Internal service orchestration
    EHR -->|gRPC / REST: Get Generics for Rx| API
    Billing -->|REST: Calculate Patient Savings| API
    EHR -->|Event: prescription.created| EventBus
    EventBus -->|Async Ingestion / Savings Audit| API

    %% Microservice internal dependencies
    API --> AuthMid
    AuthMid --> CoreEngines
    CoreEngines --> DB
    CoreEngines --> Redis
    LLMEng --> GeminiAPI
    KendraEng --> OSM
```

---

## 3. Clean / Hexagonal Internal Service Architecture

GenericMeds AI follows **Clean Architecture** to maintain complete isolation between database technologies, external LLM APIs, and consumer interfaces:

```mermaid
flowchart LR
    subgraph DrivingAdapters["Driving Adapters (Inbound)"]
        REST[FastAPI REST Endpoints]
        AdminUI[Admin CSV / Excel Import]
        EventSub[Kafka / AMQP Consumer]
    end

    subgraph ApplicationCore["Application Core (Use Cases & Business Rules)"]
        SearchUC[Medicine Discovery]
        EquivUC[Active Ingredient Equivalence]
        PriceUC[Savings Calculation & Pack Normalization]
        KendraUC[Haversine Spatial Proximity]
        TriageUC[Safety Validation & Emergency Interceptor]
    end

    subgraph DomainModels["Domain Entities (Pure Enterprise Logic)"]
        ProdEnt[MedicineProduct]
        IngEnt[ActiveIngredient & Strength]
        PriceEnt[MedicinePrice & Freshness]
        KendraEnt[JanAushadhiKendra]
        GuideEnt[MoleculeGuideline]
    end

    subgraph DrivenAdapters["Driven Adapters (Outbound)"]
        SQLAlchemy[SQLAlchemy ORM -> PostgreSQL / SQLite]
        CacheAdapter[Redis Cache Client]
        GeminiAdapter[Gemini REST Client / httpx]
        MapsAdapter[Google Maps / OSM Directions Generator]
    end

    REST --> ApplicationCore
    AdminUI --> ApplicationCore
    EventSub --> ApplicationCore

    ApplicationCore --> DomainModels
    ApplicationCore --> DrivenAdapters
```

---

## 4. Entity-Relationship Data Model

```mermaid
erDiagram
    DATA_SOURCES ||--o{ MEDICINE_PRODUCTS : registers
    DATA_SOURCES ||--o{ MEDICINE_PRICES : provides
    MEDICINE_PRODUCTS ||--|{ PRODUCT_INGREDIENTS : contains
    ACTIVE_INGREDIENTS ||--|{ PRODUCT_INGREDIENTS : constitutes
    MEDICINE_PRODUCTS ||--o{ MEDICINE_PRICES : historical_prices

    DATA_SOURCES {
        int id PK
        string source_name
        string source_url
        string source_type
        datetime last_checked_at
        datetime last_successful_sync_at
        string data_status
    }

    MEDICINE_PRODUCTS {
        int id PK
        string brand_name
        string generic_name
        string pmbi_code
        string therapeutic_group
        string manufacturer_name
        string dosage_form
        string administration_route
        string release_type
        float pack_size
        string pack_unit
        string prescription_status
        boolean is_jan_aushadhi
        int source_id FK
        datetime created_at
        datetime updated_at
    }

    ACTIVE_INGREDIENTS {
        int id PK
        string normalized_name UK
        string display_name
    }

    PRODUCT_INGREDIENTS {
        int id PK
        int product_id FK
        int ingredient_id FK
        float strength_value
        string strength_unit
    }

    MEDICINE_PRICES {
        int id PK
        int product_id FK
        float amount_inr
        string price_type
        float pack_quantity
        string unit_of_measure
        string verification_status
        datetime verified_at
        int source_id FK
        string source_url
    }

    JAN_AUSHADHI_KENDRAS {
        int id PK
        string official_kendra_code UK
        string kendra_name
        string address
        string city
        string district
        string state
        string pincode
        float latitude
        float longitude
        string phone
        string opening_hours
        boolean is_24x7
        string verification_status
        datetime last_verified_at
    }

    MOLECULE_GUIDELINES {
        int id PK
        string lookup_id UK
        string therapeutic_class
        string active_ingredient
        string strengths_forms
        string pmbi_codes
        string dispensing_rule
        string price_diff_pct
        string reference_url
    }
```

---

## 5. Core Algorithmic Engines

### 1. The Strict Equivalence Matching Engine
A medicine $B$ is classified as an `EXACT_COMPOSITION_MATCH` to medicine $A$ if and only if:
1. **Ingredient Cardinality:** $|I_A| = |I_B|$ (all active ingredients match identically).
2. **Normalized Ingredients:** $\forall i_A \in I_A, \exists i_B \in I_B$ such that $\text{Norm}(i_A) = \text{Norm}(i_B)$.
3. **Exact Strength Equality:** $\text{StrengthValue}(i_A) = \text{StrengthValue}(i_B)$ and $\text{StrengthUnit}(i_A) = \text{StrengthUnit}(i_B)$.
4. **Formulation Compatibility:** $\text{DosageForm}(A) = \text{DosageForm}(B)$ and $\text{AdministrationRoute}(A) = \text{AdministrationRoute}(B)$.
5. **Release Compatibility:** $\text{ReleaseType}(A) = \text{ReleaseType}(B)$ (e.g. *prolonged-release* cannot substitute for *immediate-release* without clinical authorization).

If strengths differ, it is classified as `DIFFERENT_STRENGTH`. If forms differ, it is tagged `DIFFERENT_FORMULATION`.

### 2. Normalized Pricing & Savings Formula
$$\text{UnitPrice} = \frac{\text{AmountINR}}{\text{PackQuantity}}$$
$$\text{UnitSavingsINR} = \text{UnitPrice}_{\text{reference}} - \text{UnitPrice}_{\text{alternative}}$$
$$\text{SavingsPercentage} = \left(\frac{\text{UnitSavingsINR}}{\text{UnitPrice}_{\text{reference}}}\right) \times 100$$

> - Prices older than 90 days (`PRICE_STALE_DAYS`) are automatically flagged as `outdated`.
> - Rate contract items with pending MRPs are strictly preserved as `amount_inr = null` (`verification_status = "under_process"`), preventing catastrophic ₹0 miscalculations.

### 3. Geospatial Proximity Engine (Haversine & Spatial Indexing)
To achieve sub-50ms query times over tens of thousands of Kendras:
1. **Bounding Box Pre-filtering:** Computes a coordinate envelope before calculating expensive trigonometric functions:
   $$\Delta\phi = \frac{r \times 1.1}{111.0}, \quad \Delta\lambda = \frac{r \times 1.1}{111.0 \times \cos(\phi_{\text{user}})}$$
2. **Haversine Distance Formulation:**
   $$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$
   $$d = 2 R \arctan2\left(\sqrt{a}, \sqrt{1-a}\right), \quad R = 6371.0\text{ km}$$

---

## 6. Microservice API Contract Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/health` | Kubernetes Liveness/Readiness Probe & DB health | None |
| `GET` | `/api/v1/medicines/search` | Search by brand, generic, or salt with pagination | None |
| `GET` | `/api/v1/medicines/{id}` | Complete verified medicine record & price history | None |
| `POST` | `/api/v1/alternatives/search` | Retrieve composition-equivalent Jan Aushadhi matches | None |
| `POST` | `/api/v1/prices/compare` | Multi-product normalized unit price comparator | None |
| `POST` | `/api/v1/chat` | RAG-grounded AI assistant (English & Hindi) | None |
| `GET` | `/api/v1/kendras/nearby` | GPS-based Haversine radius search (5, 10, 25, 50 km) | None |
| `GET` | `/api/v1/kendras/search` | Manual location search (PIN, State, District) | None |
| `GET` | `/api/v1/kendras/{id}` | Detailed verified Kendra record & navigation link | None |
| `POST` | `/api/v1/kendras/import` | Administrative CSV import with row-level validation | `X-Admin-Key` |
| `GET` | `/api/v1/kendras/groups` | 68 PMBI therapeutic classifications with item counts | None |
| `GET` | `/api/v1/kendras/guidelines` | 15 clinical safe dispensing rules (Schedule H/H1) | None |
| `GET` | `/api/v1/sources` | Statutory provenance & sync status | None |
| `POST` | `/api/v1/admin/import/csv` | Administrative drug catalogue ingestion | `X-Admin-Key` |

---

## 7. Integration Patterns for Your Major Project

### Pattern A: Synchronous In-App E-Prescription Substitution
When a doctor selects a high-cost branded medicine (e.g., *Augmentin 625 Duo*) in your EHR/Telemedicine application:

```mermaid
sequenceDiagram
    autonumber
    actor Doctor as Doctor / Pharmacist
    participant EHR as EHR Frontend / Backend
    participant Gateway as API Gateway
    participant GM as GenericMeds Service
    participant DB as GenericMeds DB

    Doctor->>EHR: Prescribes 'Augmentin 625 Duo'
    EHR->>Gateway: POST /api/v1/alternatives/search { name: 'Augmentin 625 Duo' }
    Gateway->>GM: Forward Request
    GM->>DB: Query Normalized Formulation & Salts
    DB-->>GM: Amoxycillin 500mg + Potassium Clavulanate 125mg
    GM->>DB: Query PMBJP Matches
    DB-->>GM: PMBI-39 (₹57.85 for 6's vs ₹205.00)
    GM-->>Gateway: Exact match: Jan Aushadhi Amoxyclav (Save 71.8%)
    Gateway-->>EHR: Return AlternativeDTO
    EHR-->>Doctor: Display: "Jan Aushadhi equivalent saves patient ₹147.15 (72%)"
    Doctor->>EHR: Confirm Generic Substitution
```

### Pattern B: Asynchronous Post-Discharge Savings Audit (Event-Driven)
For patient discharge slips and pharmacy analytics:
1. The **Hospital Billing Service** publishes an event: `hospital.bill.finalized` with medication lines.
2. The **GenericMeds Event Worker** consumes the message.
3. It computes the total potential savings if the patient fills chronic refills at a PMBJP Jan Aushadhi Kendra.
4. Generates an automated SMS / WhatsApp link with the **nearest 3 Kendras** based on the patient's home PIN code.

---

## 8. Production Deployment & Containerization

### Dockerfile (Production Multi-Stage Build)

```dockerfile
# Stage 1: Build virtual environment
FROM python:3.11-slim AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Minimal runtime image
FROM python:3.11-slim AS runtime

WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user for healthcare security compliance
RUN groupadd -g 10001 appgroup && \
    useradd -u 10000 -g appgroup -s /bin/sh appuser && \
    mkdir -p /app/data && chown -R appuser:appgroup /app

COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv
COPY --chown=appuser:appgroup . /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Production Environment Variables

```env
# Application & Environment
PROJECT_NAME="GenericMeds AI"
VERSION="1.0.0"
ENVIRONMENT="production"
LOG_LEVEL="INFO"

# Database Configuration (PostgreSQL in production)
DATABASE_URL="postgresql+psycopg2://genericmeds_user:SecurePassword123@postgres.cluster.local:5432/genericmeds_db"

# Administrative Security
ADMIN_API_KEY="generate-a-strong-64-character-hex-token-here"

# LLM Grounded Explanations
LLM_PROVIDER="gemini"
GEMINI_API_KEY="AIzaSyYourProductionGoogleGeminiKey"
LLM_MODEL="gemini-1.5-flash"

# Statutory Pricing Invalidation
PRICE_STALE_DAYS=90

# CORS & Integration Whitelist
CORS_ORIGINS="https://hospital-his.yourdomain.com,https://patient-app.yourdomain.com"
```

---

## 9. Kubernetes Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: genericmeds-service
  namespace: healthcare-core
  labels:
    app.kubernetes.io/name: genericmeds-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: genericmeds-service
  template:
    metadata:
      labels:
        app: genericmeds-service
    spec:
      containers:
      - name: genericmeds
        image: your-registry.io/healthcare/genericmeds-service:v1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: genericmeds-config
        - secretRef:
            name: genericmeds-secret
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1024Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: genericmeds-service
  namespace: healthcare-core
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: genericmeds-service
```
