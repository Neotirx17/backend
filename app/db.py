from sqlmodel import SQLModel, create_engine, Session
from .config import settings

# Create engine (works for SQLite and PostgreSQL)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

def create_db_and_tables():
    from . import models  # ensure models are imported
    SQLModel.metadata.create_all(engine)

# dependency

def get_session():
    with Session(engine) as session:
        yield session
