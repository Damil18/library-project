"""Скрипт создания файлов проекта library-project."""
from pathlib import Path

files = {}

files["requirements.txt"] = """flask==3.0.0
python-dotenv==1.0.0
"""

files["pyproject.toml"] = """[project]
name = "library-project"
version = "0.1.0"
description = "Library management system"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests", "books/tests"]
addopts = "-v"
"""

files[".gitignore"] = """__pycache__/
*.pyc
.venv/
env/
.env
.idea/
.vscode/
*.sqlite3
*.db
.pytest_cache/
.coverage
htmlcov/
"""

files["app.py"] = '''"""Application entry point."""
from flask import Flask, jsonify

from books.routes import bp as books_bp
from core.config import Config
from core.db import close_db, init_db
from core.exceptions import AppError


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if isinstance(config, dict):
        app.config.update(config)
    elif config is not None:
        app.config.from_object(config)

    app.register_blueprint(books_bp)

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": str(error)}), error.status_code

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
'''

files["core/__init__.py"] = '"""Core package."""\n'

files["core/config.py"] = '''"""Application configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "library.db"))
    SCHEMA_PATH = str(BASE_DIR / "docs" / "schema.sql")
    TESTING = False
'''

files["core/db.py"] = '''"""Database access helpers."""
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
'''

files["core/exceptions.py"] = '''"""Application exceptions."""


class AppError(Exception):
    status_code = 500


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class ValidationError(AppError):
    status_code = 400
'''

files["books/__init__.py"] = '''"""Books module."""
from books.models import Book
from books.service import BookService

__all__ = ["Book", "BookService"]
'''

files["books/models.py"] = '''"""Book model."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Book:
    isbn: str
    title: str
    author: str
    year: int | None = None
    genre: str | None = None

    def to_dict(self):
        return asdict(self)
'''

files["books/repository.py"] = '''"""Book repository."""
from books.models import Book


class BookRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all(self):
        rows = self.conn.execute(
            "SELECT isbn, title, author, year, genre FROM books ORDER BY title"
        ).fetchall()
        return [Book(**dict(row)) for row in rows]

    def get_by_isbn(self, isbn):
        row = self.conn.execute(
            "SELECT isbn, title, author, year, genre FROM books WHERE isbn = ?",
            (isbn,),
        ).fetchone()
        return Book(**dict(row)) if row else None

    def add(self, book):
        self.conn.execute(
            "INSERT INTO books (isbn, title, author, year, genre) VALUES (?, ?, ?, ?, ?)",
            (book.isbn, book.title, book.author, book.year, book.genre),
        )
        self.conn.commit()
        return book

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
'''

files["books/service.py"] = '''"""Book service."""
from books.models import Book
from books.repository import BookRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError


class BookService:
    def __init__(self, repo):
        self.repo = repo

    def list_books(self):
        return self.repo.get_all()

    def get_book(self, isbn):
        book = self.repo.get_by_isbn(isbn)
        if not book:
            raise NotFoundError("Book " + isbn + " not found")
        return book

    def add_book(self, isbn, title, author, year=None, genre=None):
        if not isbn or not isbn.strip():
            raise ValidationError("isbn is required")
        if not title or not title.strip():
            raise ValidationError("title is required")
        if not author or not author.strip():
            raise ValidationError("author is required")
        if self.repo.get_by_isbn(isbn):
            raise ConflictError("Book " + isbn + " already exists")
        book = Book(
            isbn=isbn.strip(),
            title=title.strip(),
            author=author.strip(),
            year=year,
            genre=genre,
        )
        return self.repo.add(book)
'''

files["books/routes.py"] = '''"""Book HTTP routes."""
from flask import Blueprint, jsonify, request

from books.repository import BookRepository
from books.service import BookService
from core.db import get_db
from core.exceptions import ValidationError

bp = Blueprint("books", __name__, url_prefix="/books")


def _service():
    return BookService(BookRepository(get_db()))


@bp.get("/")
def list_books():
    return jsonify([b.to_dict() for b in _service().list_books()])


@bp.get("/<isbn>")
def get_book(isbn):
    return jsonify(_service().get_book(isbn).to_dict())


@bp.post("/")
def create_book():
    data = request.get_json(silent=True) or {}
    if not data:
        raise ValidationError("JSON body required")
    book = _service().add_book(
        isbn=data.get("isbn", ""),
        title=data.get("title", ""),
        author=data.get("author", ""),
        year=data.get("year"),
        genre=data.get("genre"),
    )
    return jsonify(book.to_dict()), 201
'''

files["books/tests/__init__.py"] = ""

files["books/tests/test_service.py"] = '''"""BookService unit tests."""
import pytest

from books import Book, BookService
from core.exceptions import ConflictError, NotFoundError, ValidationError


class FakeBookRepository:
    def __init__(self):
        self.books = []

    def get_all(self):
        return list(self.books)

    def get_by_isbn(self, isbn):
        return next((b for b in self.books if b.isbn == isbn), None)

    def add(self, book):
        self.books.append(book)
        return book

    def count(self):
        return len(self.books)


@pytest.fixture
def service():
    return BookService(FakeBookRepository())


def test_add_book(service):
    book = service.add_book("123", "Title", "Author")
    assert book.isbn == "123"
    assert service.get_book("123").title == "Title"


def test_add_book_requires_isbn(service):
    with pytest.raises(ValidationError):
        service.add_book("", "Title", "Author")


def test_add_book_requires_title(service):
    with pytest.raises(ValidationError):
        service.add_book("123", "", "Author")


def test_add_book_duplicate(service):
    service.add_book("123", "T", "A")
    with pytest.raises(ConflictError):
        service.add_book("123", "T2", "A2")


def test_get_missing_book(service):
    with pytest.raises(NotFoundError):
        service.get_book("missing")
'''

files["docs/schema.sql"] = """-- Library database schema
CREATE TABLE IF NOT EXISTS books (
    isbn TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER,
    genre TEXT
);
"""

files["tests/__init__.py"] = ""

files["tests/conftest.py"] = '''"""Test fixtures."""
import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(
        {
            "DATABASE_PATH": str(db_path),
            "TESTING": True,
            "PROPAGATE_EXCEPTIONS": False,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
'''

files["tests/test_integration.py"] = '''"""Integration tests for the HTTP API."""


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_books_list_empty(client):
    assert client.get("/books/").get_json() == []


def test_books_create(client):
    r = client.post(
        "/books/", json={"isbn": "111", "title": "T", "author": "A"}
    )
    assert r.status_code == 201
    assert r.get_json()["isbn"] == "111"
    assert len(client.get("/books/").get_json()) == 1


def test_books_duplicate(client):
    client.post("/books/", json={"isbn": "111", "title": "T", "author": "A"})
    r = client.post(
        "/books/", json={"isbn": "111", "title": "T2", "author": "A2"}
    )
    assert r.status_code == 409


def test_books_missing(client):
    assert client.get("/books/missing").status_code == 404


def test_books_validation(client):
    r = client.post("/books/", json={"isbn": "", "title": "T", "author": "A"})
    assert r.status_code == 400
'''

# ==== Create files ====
for path, content in files.items():
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("OK  " + path)

print("")
print("Total: " + str(len(files)) + " files created")