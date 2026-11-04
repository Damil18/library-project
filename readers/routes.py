"""Reader HTTP routes."""
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
