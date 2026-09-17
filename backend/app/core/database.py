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
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
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
