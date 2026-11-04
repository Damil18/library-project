# Library Project (Система учёта библиотечного фонда)

Учебный проект по дисциплине "Технология разработки программного обеспечения".

## Технологии
- Python 3.12
- Flask 3.0
- SQLite
- Pytest (тестирование)

## Модули
- `books` — управление каталогом книг
- `readers` — регистрация и управление читателями
- `loans` — выдача и возврат книг
- `reports` — формирование статистики

## Установка и запуск
~~~bash
python -m venv .venv
source .venv/Scripts/activate  # Для Windows
pip install -r requirements.txt
pip install pytest
python app.py
~~~

## Тестирование
~~~bash
pytest
~~~
