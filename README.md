# Система управління студентами

## Запуск

Потрібен менеджер проєктів [uv](https://docs.astral.sh/uv/).

```bash
uv sync                 # створити середовище і встановити залежності
uv run student-portal   # запустити консольний застосунок
```

Щоб бачити час виконання операцій, задайте рівень журналу `INFO`: `LOG_LEVEL=INFO uv run student-portal` (у PowerShell: `$env:LOG_LEVEL="INFO"; uv run student-portal`).

## Журнал оцінок

Пункт меню 9 імпортує оцінки з файлу CSV у кодуванні UTF-8 з роздільником `;`, наприклад `data/journal.csv`:

```text
student_id;course;score;graded_on
1;Вебтехнології;91;2026-10-20
```

Якщо хоча б один рядок має помилку, не імпортується жодна оцінка.

## Перевірки

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## Тести

```bash
uv run pytest            # усі тести
uv run pytest -v         # з назвою кожного тесту
uv run pytest -k journal # лише тести, у назві яких є «journal»
```

Тести лежать у теці `tests/`, спільні фікстури - у `tests/conftest.py`. Тести не змінюють `data/`: файли створюються в тимчасовій теці `tmp_path`.
