"""Loan model."""
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
