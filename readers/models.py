"""Reader model."""
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
