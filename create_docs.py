"""Скрипт создания документации и диаграмм."""
from pathlib import Path

files = {}

files["docs/tz.md"] = """# Техническое задание (ТЗ)
## 1. Общие сведения
Наименование: Система учёта библиотечного фонда «БиблиоУчёт».
Заказчик: Учебный заказчик. Исполнитель: Студент.

## 2. Назначение и цели
Автоматизация учёта выдачи и возврата книг. Цель: сократить время обслуживания читателя.

## 3. Функциональные требования
- FR-01: Регистрация читателя.
- FR-02: Поиск книги по ISBN.
- FR-03: Фиксация выдачи книги (срок 14 дней).
- FR-04: Фиксация возврата.
- FR-05: Ограничение: не более 5 активных книг на читателя.
- FR-06: Отчёт по выдачам.

## 4. Нефункциональные требования
- NFR-01: Поиск <= 1 сек.
- NFR-02: Стек: Python, Flask, SQLite.
"""

files["docs/architecture.md"] = """# Архитектура программного средства
Стиль: Модульный монолит со слоистой архитектурой.
- `routes.py` — Presentation layer (HTTP API).
- `service.py` — Application layer (бизнес-логика).
- `repository.py` — Infrastructure layer (SQLite).
- `models.py` — Domain layer (сущности).

## ADR-001: Выбор SQLite
Используется для простоты развертывания в учебном проекте.
"""

files["docs/artifacts.md"] = """# Перечень артефактов проекта
| ID | Артефакт | Тип | Владелец |
|---|---|---|---|
| A-01 | ТЗ | Документ | Аналитик |
| A-02 | Схема БД | Данные | Архитектор |
| A-03 | Код books | Код | Разработчик |
| A-04 | Код readers | Код | Разработчик |
| A-05 | Тесты | Тесты | Тестировщик |
| A-06 | CI workflow | Конфигурация | DevOps |
"""

files["docs/idef0.puml"] = """@startuml
rectangle "A-0: Управлять библиотечным фондом" as A0
actor "Читатель" as R
actor "Библиотекарь" as L
R --> A0 : Запрос читателя
A0 --> R : Выдача / Уведомление
L --> A0 : Механизм
@enduml
"""

files["docs/idef1x.puml"] = """@startuml
entity "Книга" as Book {
  * ISBN
  --
  Название
  Автор
}
entity "Читатель" as Reader {
  * ID
  --
  ФИО
}
entity "Выдача" as Loan {
  * ID
  --
  ЧитательID
  ISBN
}
Book ||--o{ Loan
Reader ||--o{ Loan
@enduml
"""

files["docs/sequence.puml"] = """@startuml
actor "Библиотекарь" as L
participant "LoanController" as C
participant "LoanService" as S
participant "SQLite" as DB
L -> C : POST /loans
C -> S : issue_book()
S -> DB : INSERT INTO loans
DB --> S : OK
S --> C : Loan Object
C --> L : 201 Created
@enduml
"""

for path, content in files.items():
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("OK  " + path)

print("Total: 6 docs created")