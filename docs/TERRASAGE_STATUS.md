# TerraSage Project Status

Updated: 2026-09-17

## 1. What TerraSage Is

TerraSage is an AI Environmental Intelligence application for retrieving and eventually reasoning over environmental knowledge. It is designed to work across five environmental domains:

- Soil: pH, organic carbon, moisture
- Climate: temperature and rainfall
- Land: land use and land cover
- Biodiversity: species richness and habitat diversity
- Human impact: pollution and deforestation

The long-term product is not a generic chatbot. The intended flow is:

```text
Environmental data + user question
        -> environmental knowledge retrieval
        -> multi-metric reasoning
        -> evidence-backed recommendations
        -> impacted metrics, time horizons, confidence, and citations
```

Only the foundation and knowledge retrieval portions of that flow have been built so far. The reasoning and recommendation layers are intentionally deferred.

## 2. Current Build Progress

### Chunk 3: Real-world environmental data layer

Status: implemented and in verification.

Completed:

- Real provider architecture under `backend/app/environmental_data/`
- Provider interface with NASA POWER, SoilGrids, ESA WorldCover, and GBIF implementations
- Coordinate validation and normalized environmental observations
- PostgreSQL persistence model for observations and provider cache entries
- Environmental data API: `POST /api/environment/data` and `GET /api/environment/profile?latitude=...&longitude=...`
- Provider-aware aggregation into a real environmental profile for soil, climate, land, and biodiversity
- Honest unavailable/error reporting when a provider cannot return data
- Frontend real-data rendering for the Environmental Profile using the live provider payload structure

Remaining verification:

- Live external API checks for each provider using the Mumbai reference coordinates
- Promoting the backend profile to the dashboard with source attribution from provider results
- Final frontend polish for source metadata and provider-specific unavailable states across more screens

### Chunk 1: Backend and environmental data foundation

Status: implemented and verified.

Completed:

- FastAPI application
- PostgreSQL connection through SQLAlchemy and Psycopg
- Pydantic request/response validation
- Environment-based configuration through `backend/.env`
- CORS configuration for the frontend
- Relational environmental schema
- Dashboard and environmental profile APIs
- Nullable fields for unavailable environmental measurements
- Empty, loading, retry, and error states in the connected frontend views
- Removal of the dashboard health score
- Removal of demo measurements from Dashboard and Environmental Profile

### Chunk 2: Knowledge and retrieval system

Status: implemented and verified.

Completed:

- Curated authoritative source registry
- Real document download and text extraction
- PDF and HTML extraction
- Text cleaning and chunking
- Chunk metadata and text-supported environmental metric tags
- Local sentence-transformers embedding provider
- PostgreSQL pgvector storage
- PostgreSQL cosine-distance retrieval
- Source listing API
- Semantic search API
- Evidence Library backend integration
- Retrieved-evidence section in Analyze
- Dashboard evidence count from PostgreSQL
- Dataset registry table for future structured datasets
- Duplicate document prevention by official source URL
- Duplicate chunk prevention by document and chunk index
- Explicit ingestion statuses: `REGISTERED`, `INGESTED`, `INGESTION_BLOCKED`, and `FAILED`

## 3. Repository Structure

```text
TerraSage/
  backend/
    app/
      main.py                         FastAPI application and route registration
      core/
        config.py                     Environment-backed settings
        database.py                    SQLAlchemy engine, sessions, migrations
      models/
        environment.py                 Users, profiles, environmental metrics
        knowledge.py                   Documents, chunks, embeddings, evidence, datasets
      schemas/
        environment.py                 Environmental API contracts
      api/routes/
        environment.py                Profile endpoints
        dashboard.py                  Dashboard endpoint
        knowledge.py                  Knowledge source/search endpoints
      knowledge/
        sources.py                    Curated official source registry
        ingestion.py                  Download, extraction, chunking, tagging, persistence
        embedding.py                  Provider-based local/API embedding abstraction
        retrieval.py                  pgvector retrieval
        schemas.py                    Knowledge API contracts
        ingest.py                     CLI entry point
      repositories/
        environment_repository.py     Database access for environmental profiles
      services/
        environment_service.py        Environmental profile business logic
        dashboard_service.py           Dashboard response construction
    tests/
    .env.example
    requirements.txt
    README.md

  frontend/
    src/
      pages/
        DashboardPage.tsx             Backend-backed dashboard
        EnvironmentPage.tsx           Backend-backed environmental profile
        EvidencePage.tsx              Backend-backed evidence library
        AnalyzePage.tsx               Retrieved-evidence demonstration
      services/
        http.ts                        Shared API request helper
        dashboardService.ts            Dashboard API client
        environmentService.ts          Profile API client
        evidenceService.ts             Sources/search API client
        knowledgeService.ts            Knowledge search API client
      models/index.ts                  Frontend data contracts
      components/shared/EvidenceCard.tsx
  docs/
    TERRASAGE_STATUS.md               This project status document
```

## 4. Runtime Architecture

### Frontend

The frontend is a React + TypeScript + Vite application. It renders API responses and does not own environmental measurements for the connected views.

Frontend API configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The frontend does not contain a database URL or database password.

### Backend

The backend is a FastAPI application served by Uvicorn. Routes are separated from SQLAlchemy models, Pydantic schemas, repositories, and services.

Backend configuration is loaded from:

```text
backend/.env
```

The backend environment contains the PostgreSQL `DATABASE_URL` and local embedding configuration. It is ignored by Git.

### Database

The configured PostgreSQL installation is:

```text
C:\Program Files\PostgreSQL\17
```

Verified database facts:

- PostgreSQL: 17.10
- Database: `terrasage`
- User: `postgres`
- pgvector extension: 0.8.6
- PostgreSQL vector type: `vector(384)`

## 5. Database Schema

### Environmental tables

- `users`
- `environmental_profiles`
- `soil_metrics`
- `climate_metrics`
- `land_metrics`
- `biodiversity_metrics`
- `human_impact_metrics`

Each environmental metric group is separated from the profile so fields can remain nullable and new groups can be added without putting all logic into one table.

### Knowledge tables

- `documents`
- `document_chunks`
- `embeddings`
- `evidence_metadata`
- `environmental_datasets`

The knowledge model stores source metadata, extracted chunk text, chunk metadata, model names, and vector embeddings. The current embedding columns are PostgreSQL `vector(384)` columns.

`environmental_datasets` is architecture only. No real environmental datasets have been downloaded or added yet.

## 6. Knowledge Corpus

The following five official sources are registered and currently marked `INGESTED`:

1. FAO, *Recarbonizing Global Soils: A Technical Manual of Recommended Sustainable Soil Management*
2. FAO, *The State of the World's Biodiversity for Food and Agriculture*
3. FAO, *State of Knowledge of Soil Biodiversity*
4. IPCC, *Climate Change and Land*
5. FAO, *Conservation Agriculture*

Official source URLs are stored in the database. The first three are official FAO PDFs. The IPCC and Conservation Agriculture sources are official webpages.

Verified corpus totals:

- Documents: `5`
- Document chunks: `535`
- Stored embeddings: `535`
- Non-null chunk vectors: `535`
- Vector dimension: `384`
- Ingestion status: `5 INGESTED`, `0 INGESTION_BLOCKED`, `0 FAILED`

The ingestion command is:

```powershell
cd C:\Users\Projects\TerraSage\backend
$env:PYTHONPATH='C:\Users\Projects\TerraSage\.venv\Lib\site-packages;.'
..\.venv\Scripts\python.exe -m app.knowledge.ingest --index
```

The pipeline marks a source `INGESTED` only after content extraction, chunk creation, local embedding, and database persistence succeed. It does not substitute third-party documents or fabricate excerpts.

## 7. Embedding and Retrieval

The current provider is local:

```env
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

The selected backend environment is:

```text
C:\Users\Projects\TerraSage\.venv\Scripts\python.exe
```

Verified local packages:

- `sentence-transformers`: 3.0.1
- `transformers`: 4.41.2
- `torch`: 2.4.1

The local model was loaded successfully and generated real numeric 384-dimensional vectors. No embedding API key is required for the local provider.

Retrieval flow:

```text
query text
  -> all-MiniLM-L6-v2 embedding
  -> PostgreSQL pgvector cosine-distance ordering
  -> indexed document chunks
  -> source metadata, excerpt, score, matched metrics
```

The retrieval service does not use LIKE search, random vectors, hashes, zero vectors, or fabricated evidence.

## 8. APIs

### Health and environmental data

```text
GET   /api/health
GET   /api/environment/profile
POST  /api/environment/profile
PATCH /api/environment/profile
GET   /api/dashboard
```

### Knowledge

```text
GET  /api/knowledge/sources
POST /api/knowledge/search
```

Search request shape:

```json
{
  "query": "How does soil organic carbon relate to sustainable soil management?",
  "top_k": 5,
  "metrics": []
}
```

Search returns only chunks belonging to documents whose status is `INGESTED`.

## 9. Frontend Connections

### Dashboard

Connected to `GET /api/dashboard`.

The dashboard currently displays:

- Available environmental factor count
- Missing environmental factor count
- Nullable soil, climate, land, biodiversity, and human-impact fields
- Backend evidence count
- Honest empty placeholders for analyses and recommendations

The arbitrary environmental health score has been removed.

### Environmental Profile

Connected to `GET /api/environment/profile`.

It displays backend profile location, timestamps, completeness derived from available/missing fields, and nullable environmental metrics. When no profile exists, it displays:

```text
No environmental profile available yet.
Add environmental data to begin.
```

### Evidence Library

Connected to `GET /api/knowledge/sources` for source listing. Search calls `POST /api/knowledge/search`.

It displays real PostgreSQL source metadata, official source links, chunk counts, environmental metrics, and relevance when search results are returned. It no longer uses the old `example.org` evidence records in this connected view.

### Analyze

The natural-language Analyze view has a `Retrieve knowledge` action. It displays:

- The submitted query
- Retrieved source title and organization
- Publication year when available
- Evidence excerpt
- Matched environmental metrics
- Relevance score
- Official source link

The section is explicitly labeled retrieved knowledge. It does not generate an AI answer, recommendation, confidence calculation, or scientific conclusion.

## 10. Verified Tests

Backend:

```text
python -m pytest -q
3 passed
```

Frontend:

```text
npm run typecheck
npm run build
```

Both passed during the latest verification.

Live API verification passed:

- `/api/health` -> HTTP 200
- `/api/knowledge/sources` -> HTTP 200, 5 sources
- `/api/dashboard` -> HTTP 200, evidence total 5
- `/api/environment/profile` -> HTTP 200
- `/api/knowledge/search` -> HTTP 200 with real indexed results

The four tested semantic query categories included soil carbon, climate/land/biodiversity, soil cover/moisture/agriculture, and a multi-metric query involving rainfall, soil organic carbon, monoculture, and biodiversity decline.

Three retrieved excerpts were checked against the exact stored indexed chunk text and verified present.

## 11. How to Run the Project

### Start the backend

Use the selected environment and ensure its site-packages path is first because this local venv inherits part of the base Python installation:

```powershell
cd C:\Users\Projects\TerraSage\backend
$env:PYTHONPATH='C:\Users\Projects\TerraSage\.venv\Lib\site-packages;.'
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Start the frontend

In a second terminal:

```powershell
cd C:\Users\Projects\TerraSage\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

If port 5173 is occupied, Vite selects another port. The frontend `.env` must point to the backend at port 8000.

### Check the database

```powershell
cd C:\Users\Projects\TerraSage\backend
$env:PYTHONPATH='C:\Users\Projects\TerraSage\.venv\Lib\site-packages;.'
..\.venv\Scripts\python.exe -c "from sqlalchemy import create_engine, text; from app.core.config import settings; c=create_engine(settings.database_url).connect(); print(c.execute(text('select current_database()')).scalar()); print(c.execute(text('select extversion from pg_extension where extname=\'vector\'')).scalar()); c.close()"
```

## 12. What Is Not Built Yet

These are intentionally deferred and are not part of the completed foundation:

- User authentication and real login/signup API
- Final LLM reasoning engine
- Multi-turn conversation memory
- Clarification engine for incomplete inputs
- Recommendation generation
- Impacted-metric projections
- Short-, medium-, and long-term recommendation horizons
- Confidence calculation for recommendations
- Full evidence citation/referencing workflow in generated answers
- Large structured environmental datasets
- Dataset ingestion and scheduled updates
- Production-grade document storage/object storage
- Background ingestion jobs and queues
- Database migrations through Alembic
- Production deployment, monitoring, and secret management

The existing frontend still contains deferred mock services/data for screens that are outside the connected Chunk 1 and Chunk 2 surfaces. Those should be replaced when their respective features are implemented; they are not used by the connected Dashboard, Environmental Profile, Evidence Library, or retrieval demonstration.

## 13. Known Operational Notes

- FastAPI and Vite are not intended to remain running after an agent verification session; start them with the commands above.
- The selected `.venv` has an inherited Python path quirk. Prioritize `.venv\Lib\site-packages` in `PYTHONPATH` when running backend commands.
- The model may emit a harmless Hugging Face cache deprecation warning on first use.
- The frontend build may report an outdated Browserslist database; this does not currently fail the build.
- PostgreSQL credentials remain only in `backend/.env`; do not paste or commit them.

## 14. Current Overall Status

The TerraSage foundation and first real knowledge retrieval pipeline are operational:

```text
PostgreSQL + pgvector
        -> real official source documents
        -> extracted and stored chunks
        -> real local 384-dimensional embeddings
        -> pgvector semantic retrieval
        -> backend knowledge APIs
        -> Evidence Library and Analyze retrieval UI
```

Chunk 3 has not been started. The next planned work is to improve the knowledge retrieval quality and then build the separate reasoning/recommendation capabilities, but those should remain separate from this completed foundation.
