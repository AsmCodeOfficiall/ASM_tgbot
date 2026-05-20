# api — Fledif

Усі файли в цій папці — твоя зона. Gleb сюди не комітить (крім узгоджених змін у `routes_github.py`).

| Файл | Навіщо |
|------|--------|
| `main.py` | Запуск FastAPI |
| `db.py` | SQLite + таблиці users, projects, transactions |
| `auth.py` | Перевірка initData (HMAC) |
| `budget.py` | 10/30/30/30 і dashboard |
| `routes.py` | GET dashboard, POST projects |
| `routes_github.py` | POST webhook — викликає bot/notify.py |
| `config.py` | Змінні з .env |
| `data/` | Файл бази |

Запуск (коли буде код): `uvicorn main:app --app-dir api` або з папки api.
