# api — Fledif

All files in this folder are your area. Gleb does not commit here (except agreed changes in `routes_github.py`).

| File | Purpose |
|------|---------|
| `main.py` | FastAPI startup |
| `db.py` | SQLite + users, projects, transactions tables |
| `auth.py` | initData validation (HMAC) |
| `budget.py` | 10/30/30/30 and dashboard |
| `routes.py` | GET dashboard, POST projects |
| `routes_github.py` | POST webhook — invokes bot/notify.py |
| `config.py` | Variables from .env |
| `data/` | Database file |

Run (when code is ready): `uvicorn main:app --app-dir api` or from the api folder.
