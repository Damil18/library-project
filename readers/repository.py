"""Reader repository."""
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
