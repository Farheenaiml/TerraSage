# TerraSage — AI Biodiversity Intelligence System
### Darukaa.Earth AI Biodiversity Intelligence Chatbot Challenge

TerraSage is an AI-powered conversational environmental intelligence platform designed to behave like an **AI Environmental Scientist**, not a generic chatbot. It connects live satellite and ground telemetry, an authoritative scientific RAG layer, multi-variable ecological reasoning, and evidence-backed recommendations to tackle complex biodiversity and land degradation challenges.

---

## 🌟 Core Highlights & Challenge Compliance

| Requirement | Implementation | Authoritative Source |
| :--- | :--- | :--- |
| **Soil Health** | pH, Organic Carbon %, Depth, and Baseline Soil Stewardship | SoilGrids & Field Diagnostics |
| **Climate Factors** | Surface Temperature, Annual/Daily Precipitation | NASA POWER API |
| **Land Cover / Use** | 10m High-Resolution Land Classification | ESA WorldCover 2021 |
| **Biodiversity Indicators** | Observed Species Richness, Occurrence Counts | GBIF (Global Biodiversity Information Facility) |
| **Human Impact** | Real-time PM2.5, PM10, European & US AQI, Tree Cover Loss | Copernicus CAMS / Open-Meteo & Hansen GFC |
| **Scientific RAG** | 535 Ingested Chunks in PostgreSQL with Vector Embeddings | FAO Recarbonization of Global Soils, IPCC AR6 WGII |
| **Multi-Metric Reasoning** | Cross-Domain Engine connecting $\ge 3$ variables | CrossDomainEvaluator (no single-variable answers) |
| **Conversational Intelligence**| Clarification triggers on incomplete data, multi-turn memory | Autonomous Context Engine |
| **Recommendation Engine** | Measurable targets (+15–25% SOC over 2–3 years), non-obvious actions | FAO & IPCC grounded rule definitions |

---

## 🏗️ Architecture & Data Pipeline

<p align="center">
  <img src="docs/images/architecture_flow.png" alt="TerraSage System Architecture Flow" width="950" />
</p>


```
[User Inquiry / Site Coordinates]
            │
            ▼
┌───────────────────────────────────────────────────────────┐
│              Conversational Context Engine                │
│  - Extracts location, coordinates, crop, land use, SOC    │
│  - Triggers clarification questions if context is lacking │
│  - Maintains multi-turn conversation memory               │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│             Real-Time Environmental Telemetry             │
│  - NASA POWER (Temperature & Precipitation)               │
│  - ESA WorldCover 10m (Land Classification)               │
│  - GBIF (Species Richness & Observations)                 │
│  - Copernicus CAMS (Air Quality: PM2.5, PM10, AQI)        │
│  - Hansen GFC (Deforestation & Tree Cover Loss)           │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│               Multi-Metric Reasoning Engine               │
│  - Connects >= 3 variables across domains simultaneously   │
│  - Evaluates ecological tensions, synergies, and risks    │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│         pgvector Knowledge Retrieval (RAG) Layer          │
│  - 535 Ingested Chunks from FAO, IPCC, and Nature papers  │
│  - Vector Similarity Search via sentence-transformers     │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│            Evidence-Backed Recommendation Engine          │
│  - Synthesizes What to Do, Why It Works, and Targets      │
│  - Links peer-reviewed FAO/IPCC citations & time horizons │
│  - Qualitative confidence levels (High / Medium / Low)    │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│         Conversational Scientific GenAI Synthesizer       │
│  - Autonomous built-in AI Environmental Scientist engine  │
│  - Pluggable support for Groq (Llama 3.3 70B) or OpenAI   │
└───────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema & Knowledge System

The system uses **PostgreSQL with `pgvector`** for semantic vector similarity search and relational state management:

* `knowledge_documents`: Authoritative publications (FAO GSOCseq, IPCC Climate Change & Land, Nature Ecology).
* `document_chunks`: Ingested semantic chunks with 384-dimensional dense vector embeddings (`all-MiniLM-L6-v2`).
* `environmental_observations`: Cached, normalized telemetry tagged with source, unit, depth, and time period.
* `conversations`: Multi-turn session states storing persistent `user_context` (location, crop, SOC %, rainfall).
* `conversation_messages`: Turn history storing assistant responses, clarification prompts, and evidence citations.
* `recommendations`: Lifecycle tracking (`suggested` $
ightarrow$ `in-progress` $
ightarrow$ `implemented` $
ightarrow$ `dismissed`).

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
* **Python 3.10+** (with virtual environment)
* **Node.js 18+** & npm
* **PostgreSQL 15+** with the `vector` extension installed (`CREATE EXTENSION vector;`)

### 2. Backend Setup
```powershell
cd backend

# Copy sample environment configuration
cp .env.example .env

# Configure PostgreSQL connection in .env:
# DATABASE_URL=postgresql+psycopg://postgres:<password>@localhost:5432/terrasage

# Set PYTHONPATH and launch server
$env:PYTHONPATH=".venv\Lib\site-packages;backend"
& ".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000
```
* Backend API: `http://localhost:8000`
* Interactive API Documentation (Swagger): `http://localhost:8000/docs`

### 3. Frontend Setup
```powershell
cd frontend

# Install dependencies and start Vite dev server
npm install
npm run dev
```
* Frontend Web App: `http://localhost:5173`

---

## 🧪 Testing & Verification

### Run Automated Unit Tests (15/15 Passing)
```powershell
cd backend
$env:PYTHONPATH=".venv\Lib\site-packages;backend"
& ".venv\Scripts\python.exe" -m pytest tests/test_conversations.py
```

### Build Frontend
```powershell
cd frontend
npm run build
```

---

## 🎯 Verified Challenge Use Cases

### 1. Incomplete Input Clarification (Challenge PDF Page 2)
* **User Input**: `"Biodiversity is declining on my land"`
* **System Output**:
  * `Clarification Required: True`
  * `Question: "Can you provide soil organic carbon %, rainfall pattern, and land use type?"`

### 2. Multi-Metric Agricultural Scenario (Challenge PDF Page 3)
* **User Input**: `"Soil organic carbon: 0.3%, rainfall: low, crop: monoculture wheat, region: semi-arid"`
* **System Output**:
  * **Intervention**: Legume-Based Intercropping & Soil Organic Carbon Restoration.
  * **What to do**: Introduce drought-adapted legume cover crops (e.g., chickpea, cowpea, vetch) and retain standing wheat straw stubble.
  * **Measurable Target**: Increases soil organic carbon by **~15–25% over 2–3 years**.
  * **Ecological Mechanism**: Multi-species rhizosphere symbiosis, glomalin production, and moisture retention.
  * **Authoritative Citations**: FAO Recarbonization of Global Soils (GSOCseq) & IPCC Climate Change and Land.

---

## 👥 Reviewer Access & Submission
Submitted for the **Darukaa.Earth Hackathon Challenge**.
Reviewer contact access:
* `ankita.dasgupta@darukaa.com`
* `harsh.kumar@darukaa.com`
* `utkarsh.gauniyal@darukaa.com`
* `guneet.mutreja@darukaa.com`
