# TerraSage - AI Biodiversity Intelligence System
### Darukaa.Earth AI Biodiversity Intelligence Chatbot Challenge

TerraSage is an AI-powered conversational environmental intelligence platform designed to behave like an **AI Environmental Scientist**, not a generic chatbot. It connects live satellite and ground telemetry, an authoritative scientific RAG layer, multi-variable ecological reasoning, and evidence-backed recommendations to tackle complex biodiversity and land degradation challenges.

---

## Core Highlights & Challenge Compliance

| Requirement | Implementation | Authoritative Source |
| :--- | :--- | :--- |
| **Soil Health** | pH, Organic Carbon %, Depth, and Baseline Soil Stewardship | SoilGrids & Field Diagnostics |
| **Climate Factors** | Surface Temperature, Annual/Daily Precipitation | NASA POWER API |
| **Land Cover / Use** | 10m High-Resolution Land Classification | ESA WorldCover 2021 |
| **Biodiversity Indicators** | Observed Species Richness, Occurrence Counts | GBIF (Global Biodiversity Information Facility) |
| **Human Impact** | Real-time PM2.5, PM10, European & US AQI, Tree Cover Loss | Copernicus CAMS / Open-Meteo & Hansen GFC |
| **Scientific RAG** | 535 Ingested Chunks in PostgreSQL with Vector Embeddings | FAO Recarbonization of Global Soils, IPCC AR6 WGII |
| **Multi-Metric Reasoning** | Cross-Domain Engine connecting >= 3 variables | CrossDomainEvaluator (no single-variable answers) |
| **Conversational Intelligence**| Clarification triggers on incomplete data, multi-turn memory | Autonomous Context Engine |
| **Recommendation Engine** | Measurable targets (+15-25% SOC over 2-3 years), non-obvious actions | FAO & IPCC grounded rule definitions |

---

## Architecture & Data Pipeline

<p align="center">
  <img src="docs/images/architecture_flow.png" alt="TerraSage System Architecture Flow" width="950" />
</p>

```
[User Inquiry / Site Coordinates]
            |
            v
+-------------------------------------------------------------------+
|                  Conversational Context Engine                    |
|  - Extracts location, coordinates, crop, land use, SOC            |
|  - Triggers clarification questions if context is lacking (< 3)  |
|  - Maintains multi-turn conversation memory                       |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|               Multi-Domain Telemetry & RAG Pipeline               |
|  - SoilGrids (Soil Health: pH, SOC, Bulk Density)                 |
|  - NASA POWER (Agroclimatology: Temp, Precipitation, Solar)       |
|  - ESA WorldCover (10m Sentinel-2 Land Classification)            |
|  - GBIF API (Biodiversity Occurrences & Native Species Count)     |
|  - Copernicus CAMS / Open-Meteo (PM2.5, PM10, AQI, Impact)        |
|  - pgvector RAG (535 Scientific Chunks: FAO & IPCC Literature)    |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                 Multi-Variable Reasoning Subsystem                |
|  - Validates interaction across >= 3 variables                    |
|  - Evaluates ecological trade-offs (e.g., SOC vs. Aridity)        |
|  - Enforces scientific confidence scores (0.00 - 1.00)            |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                     AI Synthesis & Action Engine                  |
|  - Ultra-fast Groq Llama 3.3 / GPT-OSS or Fallback Scientist v1   |
|  - Generates verifiable citations [Author, Year, Findings]        |
|  - Emits structured actionable recommendations (Target: +15-25%)  |
+---------------------------------+---------------------------------+
                                  |
                                  v
[Frontend HUD: Live Environmental Telemetry & Scientific Chat Stream]
```

---

## Key Features

### 1. AI Environmental Scientist Persona
Unlike generic LLMs, TerraSage never produces generic advisory advice. It operates as an authoritative environmental researcher:
- **Refuses Unfounded Guesses**: If an agronomist asks about declining yields without specifying soil or rainfall history, TerraSage pauses and queries the exact missing variables.
- **Synthesizes Complex Variables**: Connects Soil Organic Carbon (SOC), precipitation deficits, and historical tillage regimes into an integrated ecological model.
- **Cites Peer-Reviewed Science**: Integrates 535 vectorized knowledge chunks directly from FAO Recarbonization of Global Soils (GSOCseq) and IPCC Climate Change & Land reports.

### 2. Five Telemetry Layers
1. **Soil Health**: Soil organic carbon (cg/kg), pH, bulk density, CEC via SoilGrids REST API.
2. **Climate**: Precipitation, surface temperature, humidity, solar radiation via NASA POWER.
3. **Land Cover**: Sentinel-2 10-meter land cover classifications via ESA WorldCover.
4. **Biodiversity**: Observed species count, native richness, and invasive species flags via GBIF.
5. **Human Impact**: Real-time atmospheric particulates (PM2.5, PM10, AQI) via Copernicus CAMS & Hansen Global Forest Change deforestation monitoring.

### 3. Actionable Recommendation Engine
- **Quantified Targets**: Every proposed restoration intervention defines a measurable, multi-year ecological target (e.g., *Increase SOC from 0.3% to 0.45% (+15-25% relative) within 24-36 months*).
- **Lifecycle Tracking**: Recommendations can be filtered, reviewed, and transitioned through stages: `proposed` -> `accepted` -> `in_progress` -> `implemented`.
- **Implementation Trade-offs**: Outlines direct implementation costs, co-benefits, and risks for farmers.

---

## Project Structure

```
TerraSage/
├── backend/                        # FastAPI Backend Application
│   ├── app/
│   │   ├── api/                    # API Route Controllers
│   │   │   ├── auth.py             # Authentication & Demo Profile
│   │   │   ├── conversations.py    # Multi-turn Chat & Telemetry HUD
│   │   │   ├── dashboard.py        # Aggregated Ecosystem Metrics
│   │   │   ├── environmental.py    # 5-Layer Telemetry Providers
│   │   │   ├── evidence.py         # 535-Chunk Scientific RAG Explorer
│   │   │   ├── reasoning.py        # Multi-Variable Reasoning API
│   │   │   └── recommendations.py  # Restoration Recommendations
│   │   ├── conversations/          # Conversational Subsystem
│   │   ├── core/                   # Security, Config, Database Engine
│   │   ├── environmental/          # Telemetry Providers (NASA, ESA, GBIF, Soil, CAMS)
│   │   ├── llm/                    # Groq, OpenAI & Scientist Fallback Factory
│   │   ├── models/                 # SQLAlchemy ORM Models
│   │   ├── rag/                    # Vector Search & Document Ingestion
│   │   ├── reasoning/              # Cross-Domain Reasoning Rules
│   │   └── recommendations/        # Recommendation Engine
│   ├── tests/                      # Automated Pytest Suite
│   └── requirements.txt            # Python Dependencies
├── frontend/                       # React 18 + TypeScript + Vite
│   ├── src/
│   │   ├── components/             # Reusable UI & Telemetry HUD Components
│   │   ├── pages/                  # Dashboard, Conversations, Environment, Evidence
│   │   ├── services/               # API Client Services
│   │   └── App.tsx                 # Route Hierarchy & Navigation
│   ├── package.json                # Frontend Dependencies
│   └── vite.config.ts              # Vite Bundler Configuration
├── docs/                           # Documentation & Architecture Assets
│   └── images/                     # System Diagrams
└── README.md                       # Main Documentation
```

---

## Getting Started

### Prerequisites
- **Python**: 3.10+
- **Node.js**: 18+ and npm
- **PostgreSQL**: 15+ with the `pgvector` extension installed

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows PowerShell:
.env\Scripts\Activate.ps1
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
```

#### Environment Variables (`backend/.env`)
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/terrasage
SECRET_KEY=your-secure-jwt-secret-key
ENVIRONMENT=development

# Cloud LLM (Groq Llama 3.3 / GPT-OSS):
LLM_PROVIDER=groq
LLM_API_KEY=gsk_your_groq_api_key_here
LLM_MODEL=openai/gpt-oss-20b

# (Optional: Fallback to built-in Environmental Scientist):
# LLM_PROVIDER=mock
```

#### Start Backend Server:
```bash
uvicorn app.main:app --reload --port 8000
```
Backend API will be accessible at: `http://localhost:8000`
Interactive Swagger Docs: `http://localhost:8000/docs`

---

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
The Frontend UI will be accessible at: `http://localhost:5173`

---

## Step-by-Step Testing & Verification Guide

### Scenario 1: Interactive Chat with Multi-Variable Clarification
1. Navigate to **Conversations** (`http://localhost:5173/conversations`).
2. Click **+ New Conversation**. Notice that the right-hand **Environmental Context** panel starts clean (no premature missing variables).
3. Send a vague query:
   ```text
   Biodiversity is declining on my farm.
   ```
4. **Expected Behavior**: The AI Environmental Scientist acknowledges the concern and triggers a **Clarification Request** asking for missing variables (soil metrics, precipitation, and past farming practices). The right-hand panel now highlights the required variables.
5. Provide the multi-variable data:
   ```text
   Soil organic carbon: 0.3%, rainfall: 420mm semi-arid, monoculture wheat for 6 years, degraded micro-arthropods.
   ```
6. **Expected Behavior**: The model evaluates cross-variable synergies (SOC + precipitation + crop rotation), renders bold scientific analysis, cites FAO/IPCC evidence, and proposes concrete interventions (such as **Legume Intercropping & Reduced Tillage** targeting +15-25% SOC). The right HUD reflects the identified variables.

### Scenario 2: Live Environmental Telemetry Profiling
1. Navigate to **Environment Profile** (`http://localhost:5173/environment`).
2. Select the **Nashik Farm** preset (Latitude: `19.9975`, Longitude: `73.7898`).
3. Click **Query Site Data**.
4. **Expected Behavior**: Real-time telemetry cards load across all 5 domains:
   - **SoilGrids**: SOC, pH, bulk density.
   - **NASA POWER**: Mean annual rainfall, solar insolation, temperature.
   - **ESA WorldCover**: High-resolution land cover distribution.
   - **GBIF**: Native biodiversity occurrence count.
   - **Copernicus CAMS**: PM2.5, PM10, and European AQI.

### Scenario 3: Evidence Library & RAG
1. Navigate to **Evidence** (`http://localhost:5173/evidence`).
2. Type `soil organic carbon` or `agroforestry` in the search bar.
3. **Expected Behavior**: Semantic retrieval surfaces indexed chunks from the FAO GSOCseq report and IPCC Climate Change & Land assessments with exact section citations and relevancy rankings.

---

## Automated Test Suite

Run the full automated test suite to verify backend stability and compliance:

```bash
cd backend
pytest tests/ -v
```

---

## Scientific Grounding & Citations
- **FAO (2020)**: *Global Soil Organic Carbon Sequestration Potential (GSOCseq)*. Food and Agriculture Organization of the United Nations, Rome.
- **IPCC (2019)**: *Special Report on Climate Change, Desertification, Land Degradation, Sustainable Land Management, Food Security, and Greenhouse Gas Fluxes in Terrestrial Ecosystems (SRCCL)*.
- **ISRIC (2021)**: *SoilGrids250m 2.0: Global gridded soil information based on machine learning*.
- **GBIF.org (2024)**: *GBIF Occurrence Download*. Global Biodiversity Information Facility.
- **ESA (2021)**: *WorldCover 10m 2021 v200*. European Space Agency.
