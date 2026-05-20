# bot — Gleb

Працюй тільки тут. API чіпаєш мінімум — через `api/routes_github.py` і спільний `.env`.

| Файл | Навіщо |
|------|--------|
| `main.py` | Запуск Aiogram |
| `handlers.py` | /start, стендап (FSM) |
| `keyboard.py` | Кнопка «Відкрити дашборд» (Web App) |
| `scheduler.py` | 19:00 питання, 21:00 зведення |
| `notify.py` | Повідомлення в групу (GitHub + стендап) |

Запуск: `python main.py` з папки bot.
