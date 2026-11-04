"""Application configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "library.db"))
    SCHEMA_PATH = str(BASE_DIR / "docs" / "schema.sql")
    TESTING = False
