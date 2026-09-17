from collections.abc import Generator

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine: Engine | None = (
    create_engine(settings.database_url, echo=settings.sql_echo, pool_pre_ping=True)
    if settings.database_url
    else None
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False) if engine else None


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


def migrate_embedding_columns() -> None:
    if engine is None:
        return
    with engine.begin() as connection:
        for table, column in (("document_chunks", "embedding"), ("embeddings", "vector")):
            column_type = connection.execute(
                text("SELECT udt_name FROM information_schema.columns WHERE table_name = :table AND column_name = :column"),
                {"table": table, "column": column},
            ).scalar()
            if column_type == "vector":
                continue
            row_count = connection.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
            if row_count:
                raise RuntimeError(f"Cannot migrate populated {table}.{column} without a data migration.")
            connection.execute(text(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" TYPE vector(384) USING NULL::vector(384)'))
        for table, column in (("document_chunks", "embedding"), ("embeddings", "vector")):
            column_type = connection.execute(
                text("SELECT udt_name FROM information_schema.columns WHERE table_name = :table AND column_name = :column"),
                {"table": table, "column": column},
            ).scalar()
            if column_type != "vector":
                row_count = connection.execute(text(f'SELECT count(*) FROM "{table}"')).scalar_one()
                if row_count:
                    raise RuntimeError(f"Cannot migrate non-empty {table}.{column} without a data migration.")
                connection.execute(text(f'ALTER TABLE "{table}" ALTER COLUMN "{column}" TYPE vector(384) USING NULL::vector'))


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
