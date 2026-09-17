from collections.abc import Generator
import logging
from fastapi import HTTPException, status
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def get_normalized_url(url: str | None) -> str | None:
    if not url:
        return None
    url = url.strip()
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

db_url = get_normalized_url(settings.database_url)

engine: Engine | None = (
    create_engine(db_url, echo=settings.sql_echo, pool_pre_ping=True)
    if db_url
    else None
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False) if engine else None


def init_db() -> None:
    if engine is None:
        logger.warning("Database engine is not configured; skipping initialization.")
        return
    try:
        with engine.begin() as conn:
            # Attempt to enable pgvector extension if available
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            except Exception as e:
                logger.info("pgvector extension notice: %s", e)
        Base.metadata.create_all(bind=engine)
        migrate_knowledge_columns()
        seed_initial_cloud_data()
        logger.info("Database tables initialized successfully.")
    except Exception as exc:
        logger.warning("Database initialization warning: %s", exc)


def migrate_knowledge_columns() -> None:
    if engine is None:
        return
    additions = {
        "documents": {
            "organization": "VARCHAR(300)", "year": "INTEGER", "source_type": "VARCHAR(100)",
            "source_url": "VARCHAR(1000)", "topic": "VARCHAR(500)", "environmental_metrics": "JSON",
            "ingestion_status": "VARCHAR(50)", "ingestion_error": "TEXT",
        },
        "document_chunks": {"metadata_json": "JSON"},
    }
    try:
        with engine.begin() as connection:
            for table, columns in additions.items():
                existing = {row[0] for row in connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = :table"), {"table": table})}
                for column, column_type in columns.items():
                    if column not in existing:
                        connection.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{column}" {column_type}'))
                if table == "documents":
                    connection.execute(text("UPDATE documents SET ingestion_status = 'REGISTERED' WHERE ingestion_status IS NULL"))
                    connection.execute(text("UPDATE documents SET ingestion_status = 'REGISTERED' WHERE ingestion_status = 'registered'"))
                    connection.execute(text("UPDATE documents SET environmental_metrics = '[]' WHERE environmental_metrics IS NULL"))
                if table == "document_chunks":
                    connection.execute(text("UPDATE document_chunks SET metadata_json = '{}' WHERE metadata_json IS NULL"))
    except Exception as exc:
        logger.warning("Migration warning: %s", exc)


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured. Supply DATABASE_URL in backend/.env.",
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_initial_cloud_data() -> None:
    if engine is None:
        return
    try:
        from app.models.recommendations import RecommendationRecord
        from app.models.environment import EnvironmentalObservation
        from app.models import Document, DocumentChunk
        import uuid
        from datetime import datetime

        with engine.begin() as conn:
            # Check if recommendations exist
            rec_count = conn.execute(text('SELECT COUNT(*) FROM "recommendations"')).scalar() or 0
            if rec_count == 0:
                conn.execute(text('''
                    INSERT INTO "recommendations" (id, title, description, rationale, impacted_metrics, expected_impact, time_horizon, confidence, confidence_score, priority, category, status, limitations, created_at)
                    VALUES 
                    (:id1, 'Legume Intercropping (Chickpea/Pigeonpea)', 'Integrate deep-rooting nitrogen-fixing legumes into monoculture wheat fields during fallow rotation.', 'Elevates organic matter input while reducing chemical nitrogen dependency in semi-arid zones.', '["soil_organic_carbon", "microbial_diversity"]', '+15-25% SOC over 24-36 months', 'medium-term', 'high', 0.88, 'high', 'regenerative-agriculture', 'accepted', '["Requires seasonal rainfall timing", "Seed inoculation with Rhizobium required"]', :now),
                    (:id2, 'Conservation Tillage & Stubble Residue Retention', 'Transition to zero-till or minimum-till seed drilling retaining >=30% straw mulch on topsoil.', 'Suppresses evaporative soil moisture deficit and halts wind/water erosion of carbon-rich top layer.', '["soil_moisture", "bulk_density"]', 'Reduces soil evaporation by 30-45%', 'short-term', 'high', 0.92, 'high', 'soil-stewardship', 'proposed', '["Requires specialized zero-till seed drill equipment"]', :now),
                    (:id3, 'Agroforestry Windbreak & Native Flora Buffers', 'Plant multi-tiered native trees (Azadirachta indica, Acacia nilotica) along perimeter boundary.', 'Moderates local microclimate, creates pollinator corridors, and mitigates particulate dust exposure.', '["biodiversity_richness", "pm25_mitigation"]', '+40% pollinator visits within 3 seasons', 'long-term', 'medium', 0.79, 'medium', 'habitat-restoration', 'suggested', '["3-5 year maturation curve for full canopy"]', :now)
                '''), {
                    "id1": str(uuid.uuid4()), "id2": str(uuid.uuid4()), "id3": str(uuid.uuid4()),
                    "now": datetime.utcnow()
                })
                logger.info("Seeded baseline recommendations into database.")
    except Exception as exc:
        logger.warning("Cloud data seed notice: %s", exc)
