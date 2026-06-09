# frontend — Ishak (Telegram Mini App)

React + Vite + Tailwind + `@twa-dev/sdk`. One screen (SPA), no react-router.

## Screen

1. **Team fund overview**
2. **Personal balance**
3. **Recent transactions / projects**
4. Add project button → modal (Name, Amount USD)
5. Modal submit uses native Telegram **MainButton**
6. On success — toast “Project added successfully!”

## Telegram Theme

`hooks/useTelegramTheme.js` — colors from `WebApp.themeParams` → CSS `--tg-theme-*`.

## Hugging Face Space

On HF this runs in a single Docker container on port **7860**:

- FastAPI serves built `frontend/dist` and API `/api/*`
- **Do not set `VITE_API_URL`** (or leave it empty) — requests go to the same origin
- `WEBAPP_URL` in the bot = your Space URL (for example `https://USER-asm-tgbot.hf.space`)

Local development:

```bash
# terminal 1 — backend + bot
python run.py

# terminal 2 — frontend with proxy to :7860
cd frontend && npm install && npm run dev
```

Production build (Dockerfile does this automatically):

```bash
cd frontend && npm run build
```

## Structure

| File | Purpose |
|------|---------|
| `App.jsx` | Main SPA |
| `api.js` | `fetchApi` + `Authorization: tma` |
| `components/` | Dashboard, TransactionList, ProjectModal, SuccessToast |
| `hooks/` | `useTelegramTheme`, `useMainButton`, `useTelegramBackButton` |
| `utils/` | `format.js`, `theme.js` |
