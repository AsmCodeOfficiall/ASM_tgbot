# deploy — Fledif

Docker і nginx. Ishak і Gleb сюди не заходять.

| Файл | Навіщо |
|------|--------|
| `Dockerfile.api` | Образ для FastAPI |
| `Dockerfile.bot` | Образ для бота (або один Dockerfile на обидва) |
| `nginx.conf` | `/` → frontend/dist, `/api/` → api:8000 |
| `docker-compose.yml` | Можна перенести сюди з кореня — як зручніше |
