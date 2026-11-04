"""Loan HTTP routes."""
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
