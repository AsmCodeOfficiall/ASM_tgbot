from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiogram.types import Update

from api.db import init_db
from api.routes import router
from api.routes_github import router as github_router
from bot.bot_dp import bot, dp
from bot.config import settings

WEBHOOK_PATH = "/webhook/telegram"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Set webhook on startup
    webhook_url = f"{settings.WEBAPP_URL.rstrip('/')}{WEBHOOK_PATH}"
    try:
        await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    except Exception as e:
        print(f"WARNING: Failed to set webhook to Telegram: {e}")
    
    yield
    # We do NOT delete the webhook on shutdown to prevent race conditions during Zero Downtime Deployments

app = FastAPI(lifespan=lifespan)

@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.include_router(router)
app.include_router(github_router)

dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(dist_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_path, "index.html"))
