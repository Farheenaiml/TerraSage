from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.environment import router as environment_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.reasoning import router as reasoning_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.conversations import router as conversations_router
from app.core.config import settings
from app.core.database import Base, engine, init_db, migrate_knowledge_columns
from app.models import Document, DocumentChunk, Embedding, EvidenceMetadata  # noqa: F401
from app.models.environment import EnvironmentalObservation, ProviderCache  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if engine is not None:
            init_db()
            logger.info("Database schema is ready")
        else:
            logger.warning("DATABASE_URL is not configured; running without database.")
    except Exception as err:
        logger.warning("Database startup notice: %s", err)
    yield

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(environment_router)
app.include_router(dashboard_router)
app.include_router(knowledge_router)
app.include_router(reasoning_router)


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    if engine is None:
        return {"status": "degraded", "database": "not_configured"}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError:
        return {"status": "degraded", "database": "unavailable"}

app.include_router(recommendations_router, prefix="/api/recommendations")
app.include_router(conversations_router, prefix="/api/conversations")
