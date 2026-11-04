"""Скрипт добавления остальных модулей (readers, loans, fines, reports)."""
from pathlib import Path

files = {}

# ================= READERS =================
files["readers/__init__.py"] = '''"""Readers module."""
from readers.models import Reader
from readers.service import ReaderService

__all__ = ["Reader", "ReaderService"]
'''

files["readers/models.py"] = '''"""Reader model."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Reader:
    full_name: str
    phone: str | None = None
    email: str | None = None
    registered_at: str = ""
    id: int | None = None

    def to_dict(self):
        return asdict(self)
'''

files["readers/repository.py"] = '''"""Reader repository."""
from readers.models import Reader


class ReaderRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all(self):
        rows = self.conn.execute(
            "SELECT id, full_name, phone, email, registered_at FROM readers ORDER BY id"
        ).fetchall()
        return [Reader(**dict(row)) for row in rows]

    def get_by_id(self, reader_id):
        row = self.conn.execute(
            "SELECT id, full_name, phone, email, registered_at FROM readers WHERE id = ?",
            (reader_id,),
        ).fetchone()
        return Reader(**dict(row)) if row else None

    def get_by_email(self, email):
        row = self.conn.execute(
            "SELECT id, full_name, phone, email, registered_at FROM readers WHERE email = ?",
            (email,),
        ).fetchone()
        return Reader(**dict(row)) if row else None

    def add(self, reader):
        cur = self.conn.execute(
            "INSERT INTO readers (full_name, phone, email, registered_at) VALUES (?, ?, ?, ?)",
            (reader.full_name, reader.phone, reader.email, reader.registered_at),
        )
        self.conn.commit()
        return Reader(
            id=cur.lastrowid,
            full_name=reader.full_name,
            phone=reader.phone,
            email=reader.email,
            registered_at=reader.registered_at,
        )
'''

files["readers/service.py"] = '''"""Reader service."""
from datetime import datetime
from readers.models import Reader
from readers.repository import ReaderRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError


class ReaderService:
    def __init__(self, repo):
        self.repo = repo

    def list_readers(self):
        return self.repo.get_all()

    def get_reader(self, reader_id):
        reader = self.repo.get_by_id(reader_id)
        if not reader:
            raise NotFoundError(f"Reader {reader_id} not found")
        return reader

    def register(self, full_name, phone=None, email=None):
        if not full_name or not full_name.strip():
            raise ValidationError("full_name is required")
        if email and self.repo.get_by_email(email):
            raise ConflictError(f"Reader with email {email} already exists")
        reader = Reader(
            full_name=full_name.strip(),
            phone=phone,
            email=email,
            registered_at=datetime.now().isoformat(timespec="seconds"),
        )
        return self.repo.add(reader)
'''

files["readers/routes.py"] = '''"""Reader HTTP routes."""
from flask import Blueprint, jsonify, request
from core.db import get_db
from core.exceptions import ValidationError
from readers.repository import ReaderRepository
from readers.service import ReaderService

bp = Blueprint("readers", __name__, url_prefix="/readers")

def _service():
    return ReaderService(ReaderRepository(get_db()))

@bp.get("/")
def list_readers():
    return jsonify([r.to_dict() for r in _service().list_readers()])

@bp.get("/<int:reader_id>")
def get_reader(reader_id):
    return jsonify(_service().get_reader(reader_id).to_dict())

@bp.post("/")
def register_reader():
    data = request.get_json(silent=True) or {}
    if not data:
        raise ValidationError("JSON body required")
    reader = _service().register(
        full_name=data.get("full_name", ""),
        phone=data.get("phone"),
        email=data.get("email"),
    )
    return jsonify(reader.to_dict()), 201
'''

files["readers/tests/__init__.py"] = ""

files["readers/tests/test_service.py"] = '''"""ReaderService unit tests."""
from datetime import datetime
import pytest
from core.exceptions import ConflictError, NotFoundError, ValidationError
from readers import Reader, ReaderService


class FakeReaderRepository:
    def __init__(self):
        self.readers = []
        self._next_id = 1

    def get_all(self):
        return list(self.readers)

    def get_by_id(self, reader_id):
        return next((r for r in self.readers if r.id == reader_id), None)

    def get_by_email(self, email):
        return next((r for r in self.readers if r.email == email), None)

    def add(self, reader):
        created = Reader(
            id=self._next_id,
            full_name=reader.full_name,
            phone=reader.phone,
            email=reader.email,
            registered_at=reader.registered_at or datetime.now().isoformat(timespec="seconds"),
        )
        self._next_id += 1
        self.readers.append(created)
        return created


@pytest.fixture
def service():
    return ReaderService(FakeReaderRepository())


def test_register(service):
    reader = service.register("Иван Иванов", email="ivan@example.com")
    assert reader.id == 1
    assert reader.full_name == "Иван Иванов"

def test_register_duplicate_email(service):
    service.register("A", email="a@example.com")
    with pytest.raises(ConflictError):
        service.register("B", email="a@example.com")
'''

# ================= LOANS =================
files["loans/__init__.py"] = '''"""Loans module."""
from loans.models import Loan
from loans.service import LoanService

__all__ = ["Loan", "LoanService"]
'''

files["loans/models.py"] = '''"""Loan model."""
from dataclasses import asdict, dataclass


@dataclass
class Loan:
    reader_id: int
    isbn: str
    issued_at: str
    due_at: str
    status: str = "active"
    returned_at: str | None = None
    id: int | None = None

    def to_dict(self):
        return asdict(self)
'''

files["loans/repository.py"] = '''"""Loan repository."""
from loans.models import Loan


class LoanRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all(self):
        rows = self.conn.execute(
            "SELECT id, reader_id, isbn, issued_at, due_at, returned_at, status FROM loans ORDER BY id"
        ).fetchall()
        return [Loan(**dict(row)) for row in rows]

    def get_by_id(self, loan_id):
        row = self.conn.execute(
            "SELECT id, reader_id, isbn, issued_at, due_at, returned_at, status FROM loans WHERE id = ?",
            (loan_id,),
        ).fetchone()
        return Loan(**dict(row)) if row else None

    def get_active_by_reader(self, reader_id):
        rows = self.conn.execute(
            "SELECT id, reader_id, isbn, issued_at, due_at, returned_at, status FROM loans WHERE reader_id = ? AND status = 'active'",
            (reader_id,),
        ).fetchall()
        return [Loan(**dict(row)) for row in rows]

    def add(self, loan):
        cur = self.conn.execute(
            "INSERT INTO loans (reader_id, isbn, issued_at, due_at, returned_at, status) VALUES (?, ?, ?, ?, ?, ?)",
            (loan.reader_id, loan.isbn, loan.issued_at, loan.due_at, loan.returned_at, loan.status),
        )
        self.conn.commit()
        loan.id = cur.lastrowid
        return loan

    def update(self, loan):
        self.conn.execute(
            "UPDATE loans SET returned_at = ?, status = ? WHERE id = ?",
            (loan.returned_at, loan.status, loan.id),
        )
        self.conn.commit()
'''

files["loans/service.py"] = '''"""Loan service."""
from datetime import datetime, timedelta
from books.repository import BookRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError
from loans.models import Loan
from loans.repository import LoanRepository
from readers.repository import ReaderRepository

MAX_ACTIVE_LOANS = 5
LOAN_DAYS = 14


class LoanService:
    def __init__(self, loan_repo, reader_repo, book_repo):
        self.loan_repo = loan_repo
        self.reader_repo = reader_repo
        self.book_repo = book_repo

    def list_loans(self):
        return self.loan_repo.get_all()

    def issue_book(self, reader_id, isbn):
        if not reader_id or not isbn:
            raise ValidationError("reader_id and isbn are required")
        if not self.reader_repo.get_by_id(reader_id):
            raise NotFoundError(f"Reader {reader_id} not found")
        if not self.book_repo.get_by_isbn(isbn):
            raise NotFoundError(f"Book {isbn} not found")
        active = self.loan_repo.get_active_by_reader(reader_id)
        if len(active) >= MAX_ACTIVE_LOANS:
            raise ConflictError(f"Reader {reader_id} already has {MAX_ACTIVE_LOANS} active loans")
        if any(loan.isbn == isbn for loan in active):
            raise ConflictError(f"Reader {reader_id} already has book {isbn}")

        now = datetime.now()
        due = now + timedelta(days=LOAN_DAYS)
        loan = Loan(
            reader_id=reader_id,
            isbn=isbn,
            issued_at=now.isoformat(timespec="seconds"),
            due_at=due.isoformat(timespec="seconds"),
            status="active",
        )
        return self.loan_repo.add(loan)

    def return_book(self, loan_id):
        loan = self.loan_repo.get_by_id(loan_id)
        if not loan:
            raise NotFoundError(f"Loan {loan_id} not found")
        if loan.status != "active":
            raise ConflictError(f"Loan {loan_id} is not active")
        loan.returned_at = datetime.now().isoformat(timespec="seconds")
        loan.status = "returned"
        self.loan_repo.update(loan)
        return loan
'''

files["loans/routes.py"] = '''"""Loan HTTP routes."""
from flask import Blueprint, jsonify, request
from books.repository import BookRepository
from core.db import get_db
from core.exceptions import ValidationError
from loans.repository import LoanRepository
from loans.service import LoanService
from readers.repository import ReaderRepository

bp = Blueprint("loans", __name__, url_prefix="/loans")

def _service():
    conn = get_db()
    return LoanService(LoanRepository(conn), ReaderRepository(conn), BookRepository(conn))

@bp.get("/")
def list_loans():
    return jsonify([loan.to_dict() for loan in _service().list_loans()])

@bp.post("/")
def issue_loan():
    data = request.get_json(silent=True) or {}
    if not data:
        raise ValidationError("JSON body required")
    try:
        reader_id = int(data.get("reader_id"))
    except (TypeError, ValueError):
        raise ValidationError("reader_id must be integer")
    loan = _service().issue_book(reader_id=reader_id, isbn=data.get("isbn", ""))
    return jsonify(loan.to_dict()), 201

@bp.post("/<int:loan_id>/return")
def return_loan(loan_id):
    loan = _service().return_book(loan_id)
    return jsonify(loan.to_dict())
'''

files["loans/tests/__init__.py"] = ""

files["loans/tests/test_service.py"] = '''"""LoanService unit tests."""
from datetime import datetime
import pytest
from books import Book
from core.exceptions import ConflictError, NotFoundError
from loans import Loan, LoanService
from readers import Reader


class FakeBookRepo:
    def __init__(self):
        self.books = [Book("111", "T1", "A1"), Book("222", "T2", "A2")]
    def get_by_isbn(self, isbn):
        return next((b for b in self.books if b.isbn == isbn), None)

class FakeReaderRepo:
    def __init__(self):
        self.readers = [Reader(id=1, full_name="R1", registered_at="x")]
    def get_by_id(self, reader_id):
        return next((r for r in self.readers if r.id == reader_id), None)

class FakeLoanRepo:
    def __init__(self):
        self.loans = []
        self._next = 1
    def get_all(self):
        return list(self.loans)
    def get_by_id(self, loan_id):
        return next((l for l in self.loans if l.id == loan_id), None)
    def get_active_by_reader(self, reader_id):
        return [l for l in self.loans if l.reader_id == reader_id and l.status == "active"]
    def add(self, loan):
        loan.id = self._next
        self._next += 1
        self.loans.append(loan)
        return loan
    def update(self, loan):
        for i, l in enumerate(self.loans):
            if l.id == loan.id:
                self.loans[i] = loan
                return

@pytest.fixture
def service():
    return LoanService(FakeLoanRepo(), FakeReaderRepo(), FakeBookRepo())

def test_issue_book_success(service):
    loan = service.issue_book(1, "111")
    assert loan.id == 1
    assert loan.status == "active"

def test_return_book(service):
    loan = service.issue_book(1, "111")
    returned = service.return_book(loan.id)
    assert returned.status == "returned"
'''

# ================= FINES & REPORTS =================
files["fines/__init__.py"] = '"""Fines module."""\n'
files["fines/service.py"] = '''"""Fines service."""
from datetime import datetime

FINE_PER_DAY = 10.0

class FineService:
    def calculate(self, loan):
        if loan.status != "returned" or not loan.returned_at:
            return 0.0
        due = datetime.fromisoformat(loan.due_at)
        returned = datetime.fromisoformat(loan.returned_at)
        overdue_days = (returned - due).days
        return max(0, overdue_days) * FINE_PER_DAY
'''

files["reports/__init__.py"] = '"""Reports module."""\n'
files["reports/service.py"] = '''"""Reports service."""
class ReportService:
    def __init__(self, loan_repo):
        self.loan_repo = loan_repo

    def loan_stats(self, start, end):
        loans = self.loan_repo.get_all()
        filtered = [l for l in loans if start <= l.issued_at < end]
        return {
            "from": start, "to": end, "total": len(filtered),
            "active": sum(1 for l in filtered if l.status == "active"),
            "returned": sum(1 for l in filtered if l.status == "returned"),
        }
'''
files["reports/routes.py"] = '''"""Reports HTTP routes."""
from flask import Blueprint, jsonify, request
from core.db import get_db
from core.exceptions import ValidationError
from loans.repository import LoanRepository
from reports.service import ReportService

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.get("/loans")
def loan_report():
    start = request.args.get("from")
    end = request.args.get("to")
    if not start or not end:
        raise ValidationError("Query params 'from' and 'to' are required (YYYY-MM-DD)")
    service = ReportService(LoanRepository(get_db()))
    return jsonify(service.loan_stats(start, end))
'''

# ================= UPDATE APP.PY & SCHEMA =================
files["app.py"] = '''"""Application entry point."""
from flask import Flask, jsonify
from books.routes import bp as books_bp
from readers.routes import bp as readers_bp
from loans.routes import bp as loans_bp
from reports.routes import bp as reports_bp
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
    app.register_blueprint(readers_bp)
    app.register_blueprint(loans_bp)
    app.register_blueprint(reports_bp)

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

files["docs/schema.sql"] = """-- Library database schema
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS books (
    isbn TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER,
    genre TEXT
);

CREATE TABLE IF NOT EXISTS readers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT UNIQUE,
    registered_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reader_id INTEGER NOT NULL,
    isbn TEXT NOT NULL,
    issued_at TEXT NOT NULL,
    due_at TEXT NOT NULL,
    returned_at TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    FOREIGN KEY (reader_id) REFERENCES readers(id),
    FOREIGN KEY (isbn) REFERENCES books(isbn)
);

CREATE TABLE IF NOT EXISTS fines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    FOREIGN KEY (loan_id) REFERENCES loans(id)
);
"""

files["tests/test_integration.py"] = '''"""Integration tests for the HTTP API."""

def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}

def test_books_and_loans_flow(client):
    # 1. Добавляем книгу
    r = client.post("/books/", json={"isbn": "111", "title": "T", "author": "A"})
    assert r.status_code == 201

    # 2. Регистрируем читателя
    r = client.post("/readers/", json={"full_name": "Иван"})
    assert r.status_code == 201
    reader_id = r.get_json()["id"]

    # 3. Выдаем книгу
    r = client.post("/loans/", json={"reader_id": reader_id, "isbn": "111"})
    assert r.status_code == 201
    loan_id = r.get_json()["id"]

    # 4. Пытаемся выдать ту же книгу еще раз (должен быть конфликт)
    r2 = client.post("/loans/", json={"reader_id": reader_id, "isbn": "111"})
    assert r2.status_code == 409

    # 5. Возвращаем книгу
    r = client.post(f"/loans/{loan_id}/return")
    assert r.status_code == 200
    assert r.get_json()["status"] == "returned"
'''

# ==== Create files ====
for path, content in files.items():
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("OK  " + path)

print("")
print(f"Total: {len(files)} files created")