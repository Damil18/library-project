# Архитектура программного средства
Стиль: Модульный монолит со слоистой архитектурой.
- `routes.py` — Presentation layer (HTTP API).
- `service.py` — Application layer (бизнес-логика).
- `repository.py` — Infrastructure layer (SQLite).
- `models.py` — Domain layer (сущности).

## ADR-001: Выбор SQLite
Используется для простоты развертывания в учебном проекте.
