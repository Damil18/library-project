"""Loan repository."""
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
