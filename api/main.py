from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiogram.types import Update

from api.db import init_db
from api.routes import router
from api.routes_github import router as github_router
from bot.bot_dp import bot, dp
from bot.config import settings
from bot.handlers import router as bot_router
from bot.scheduler import router_scheduler, scheduler

WEBHOOK_PATH = "/webhook/telegram"

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    dp.include_router(bot_router)
    dp.include_router(router_scheduler)
    scheduler.start()

    # Delete webhook to ensure polling works
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception as e:
        print(f"WARNING: Failed to delete webhook: {e}")
    
    # Start polling in background
    polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    
    yield
    
    polling_task.cancel()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

import traceback

last_webhook_error = None

@app.get("/debug_error")
def get_debug_error():
    return {"last_error": last_webhook_error}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes_test import router_test

app.include_router(router)
app.include_router(github_router)
app.include_router(router_test)


dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(dist_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_path, "index.html"))
