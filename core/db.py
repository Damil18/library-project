"""Database access helpers."""
import sqlite3
from pathlib import Path

from flask import current_app, g


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE_PATH"])
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    schema = Path(current_app.config["SCHEMA_PATH"])
    if not schema.exists():
        raise FileNotFoundError("Schema not found: " + str(schema))
    conn = get_db()
    conn.executescript(schema.read_text(encoding="utf-8"))
    conn.commit()
