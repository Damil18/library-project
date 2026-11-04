"""Скрипт создания CI и документации."""
from pathlib import Path

files = {}

files[".github/workflows/ci.yml"] = '''name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest
    - name: Run tests
      run: pytest
'''

files["README.md"] = '''# Library Project (Система учёта библиотечного фонда)

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
'''

for path, content in files.items():
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("OK  " + path)

print("Total: 2 files created")