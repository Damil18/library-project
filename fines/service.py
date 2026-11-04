"""Fines service."""
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
