from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
from app.core.logging import logger

Base = declarative_base()

try:
    engine = create_engine(
        settings.sync_database_uri,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.warning(f"Could not initialize PostgreSQL engine immediately: {e}")
    engine = None
    SessionLocal = None


def get_db():
    """Dependency for obtaining database session."""
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_pgvector_extension():
    """Ensures vector extension exists in PostgreSQL."""
    if engine is None:
        return
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            logger.info("Verified 'vector' PostgreSQL extension.")
    except Exception as e:
        logger.warning(f"Failed to check/create vector extension: {e}")
