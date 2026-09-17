import argparse

from app.core.database import SessionLocal
from app.core.database import migrate_embedding_columns, migrate_knowledge_columns, engine, Base
from app.knowledge.ingestion import ingest_source, register_source
from app.knowledge.sources import CURATED_SOURCES


def main() -> None:
    parser = argparse.ArgumentParser(description="Register and optionally ingest curated TerraSage sources")
    parser.add_argument("--index", action="store_true", help="Download, extract, embed, and index sources")
    args = parser.parse_args()
    if SessionLocal is None:
        raise SystemExit("DATABASE_URL is not configured")
    migrate_knowledge_columns()
    migrate_embedding_columns()
    import app.models
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        for source in CURATED_SOURCES:
            if args.index:
                try:
                    document = ingest_source(db, source)
                    print(f"INGESTED: {document.title}")
                except Exception as error:
                    from app.models import Document
                    document = db.query(Document).filter(Document.source_url == source.source_url).first()
                    status = document.ingestion_status if document else "FAILED"
                    print(f"{status}: {source.title}: {error}")
            else:
                document = register_source(db, source)
                print(f"REGISTERED: {document.title}")


if __name__ == "__main__":
    main()
