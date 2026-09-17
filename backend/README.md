# TerraSage backend

FastAPI service for the TerraSage environmental data foundation.

## Run locally

1. Create a PostgreSQL database named `terrasage` and enable the `vector` extension when available:

```sql
CREATE DATABASE terrasage;
CREATE EXTENSION IF NOT EXISTS vector;
```

2. Copy `.env.example` to `.env` and update `DATABASE_URL`.
3. Confirm pgvector is enabled in PostgreSQL and set the local embedding configuration in `.env`:

```env
PGVECTOR_ENABLED=true
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

The local provider does not require `EMBEDDING_API_KEY` and refuses to create fake embeddings.
4. Install dependencies and start the API:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Register the curated source metadata, or index sources when embedding configuration and source access are available:

```powershell
python -m app.knowledge.ingest
python -m app.knowledge.ingest --index
```

The API is available at `http://localhost:8000`, with interactive docs at `/docs`.

## Endpoints

- `GET /api/health`
- `GET /api/environment/profile`
- `POST /api/environment/profile`
- `PATCH /api/environment/profile`
- `GET /api/dashboard`
- `GET /api/knowledge/sources`
- `POST /api/knowledge/search`

The environment and dashboard endpoints return nullable environmental fields. Knowledge search uses configured local embeddings and returns an explicit error when the embedding model is unavailable; it never fabricates evidence or vectors.
