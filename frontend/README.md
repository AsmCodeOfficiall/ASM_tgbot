# frontend — Ishak (Telegram Mini App)

React + Vite + Tailwind + `@twa-dev/sdk`. Один екран (SPA), без react-router.

## Екран

1. **Загальний фонд команди**
2. **Особистий баланс**
3. **Останні транзакції / проєкти**
4. Кнопка «Додати проєкт» → модалка (Назва, Сума USD)
5. Сабміт модалки — нативна **MainButton** Telegram
6. Після успіху — toast «Проєкт успішно додано!»

## Тема Telegram

`hooks/useTelegramTheme.js` — кольори з `WebApp.themeParams` → CSS `--tg-theme-*`.

## Hugging Face Space

На HF все крутиться в одному Docker-контейнері на порту **7860**:

- FastAPI віддає зібраний `frontend/dist` і API `/api/*`
- **`VITE_API_URL` не задавай** (або порожній) — запити йдуть на той самий origin
- `WEBAPP_URL` у боті = URL вашого Space (наприклад `https://USER-asm-tgbot.hf.space`)

Локальна розробка:

```bash
# термінал 1 — бек + бот
python run.py

# термінал 2 — фронт з proxy на :7860
cd frontend && npm install && npm run dev
```

Збірка для продакшену (Dockerfile робить це автоматично):

```bash
cd frontend && npm run build
```

## Структура

| Файл | Навіщо |
|------|--------|
| `App.jsx` | Головний SPA |
| `api.js` | `fetchApi` + `Authorization: tma` |
| `components/` | Dashboard, TransactionList, ProjectModal, SuccessToast |
| `hooks/` | `useTelegramTheme`, `useMainButton`, `useTelegramBackButton` |
| `utils/` | `format.js`, `theme.js` |
