# ASM_tgbot

Чотири папки — кожен працює в своїй, без зайвих вкладень.

| Папка | Хто | Що робить |
|-------|-----|-----------|
| **frontend/** | Ishak | Telegram Mini App (React) |
| **api/** | Fledif | FastAPI, БД, бюджет, HMAC |
| **bot/** | Gleb | Aiogram, стендапи, GitHub-алерти |
| **deploy/** | Fledif | Docker, nginx, compose |

Корінь: `.env.example`, `docker-compose.yml` — спільні налаштування.

Гілка: **develop**.

## Клон

```bash
git clone https://github.com/AsmCodeOfficiall/ASM_tgbot.git
cd ASM_tgbot
git checkout develop
```

## Хто куди не лізе

- Ishak → тільки `frontend/`
- Gleb → тільки `bot/` (+ один роут у `api/routes_github.py` за домовленістю)
- Fledif → `api/` + `deploy/`
