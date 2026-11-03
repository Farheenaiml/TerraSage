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

## Render database troubleshooting

The backend's `GET /api/health` response must report `"status":"ok"` and
`"database":"connected"`. If it reports an unavailable database, dashboard,
environment profile, conversations, and recommendations cannot load.

In the Render dashboard:

1. Confirm the `terrasage-db` PostgreSQL database is available and has not
   expired or been suspended. Back up any data before replacing a database.
2. Open the `terrasage-backend` service's **Environment** settings and confirm
   `DATABASE_URL` is linked to the active PostgreSQL database's internal
   connection string. Do not paste the URL into public issues or logs.
3. Confirm the backend and database are in the same Render region, save the
   environment change, then manually redeploy the backend.
4. Open `https://terrasage-backend.onrender.com/api/health`. Verify the JSON
   reports `"database":"connected"`, then reload the frontend.

If the database has expired or is missing, create a replacement PostgreSQL
database, update the backend's `DATABASE_URL` to that database's internal
connection string, and redeploy. A replacement database starts empty.

## Endpoints

- `GET /api/health`
- `GET /api/environment/profile`
- `POST /api/environment/profile`
- `PATCH /api/environment/profile`
- `GET /api/dashboard`
- `GET /api/knowledge/sources`
- `POST /api/knowledge/search`

The environment and dashboard endpoints return nullable environmental fields. Knowledge search uses configured local embeddings and returns an explicit error when the embedding model is unavailable; it never fabricates evidence or vectors.
