"""Book HTTP routes."""
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
