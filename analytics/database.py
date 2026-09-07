import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ey_cart")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD is missing from .env")

engine = create_engine(
    "postgresql+psycopg2://",
    connect_args={
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
    },
    pool_pre_ping=True,
)


def fetch_all(sql: str, params: dict | None = None) -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(row._mapping) for row in result]


def fetch_one(sql: str, params: dict | None = None) -> dict | None:
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {}).mappings().first()
        return dict(result) if result else None


def health_check() -> dict:
    """Check that the EY CART PostgreSQL database is reachable."""
    row = fetch_one(
        """
        SELECT
            current_database() AS database,
            current_user AS user,
            version() AS version
        """
    )
    return row or {}
