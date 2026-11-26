import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Determine base project directory (c:\HON) and sqlite database path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
default_db = (BASE_DIR / "chicago_crime.db").resolve().as_posix()

DB_PATH = os.environ.get("CHICAGO_CRIME_DB", default_db)
if "\\" in DB_PATH:
    DB_PATH = Path(DB_PATH).resolve().as_posix()

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create SQLite engine with multi-threaded support for FastAPI, Streamlit, and Jupyter
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Standard session factory for API and services
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base shared across all domain models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request
    and ensures the session is properly closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
