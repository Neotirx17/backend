import os
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from backend/.env regardless of CWD
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseModel):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///backend/app.db")
    CORS_ORIGINS: list[str] = [
        os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    ]
    SEED_ON_STARTUP: bool = os.getenv("SEED_ON_STARTUP", "true").lower() in ("1","true","yes","y")

def _normalize_db_url(url: str) -> str:
    # Use psycopg driver when using PostgreSQL
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

settings = Settings()
settings.DATABASE_URL = _normalize_db_url(settings.DATABASE_URL)
