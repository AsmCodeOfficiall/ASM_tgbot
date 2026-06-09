# bot — Gleb

Work only here. Touch the API minimally — via `api/routes_github.py` and shared `.env`.

| File | Purpose |
|------|---------|
| `main.py` | Aiogram startup |
| `handlers.py` | /start, standup (FSM) |
| `keyboard.py` | Open dashboard button (Web App) |
| `scheduler.py` | 19:00 questions, 21:00 summary |
| `notify.py` | Group messages (GitHub + standup) |

Run: `python main.py` from the bot folder.
