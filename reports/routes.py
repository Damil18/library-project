"""Reports HTTP routes."""
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
