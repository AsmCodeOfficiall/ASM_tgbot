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
from utils.trace import execution_trace, add_trace, set_error

@asynccontextmanager
async def lifespan(app: FastAPI):
    add_trace("Lifespan started")
    add_trace("Initializing DB...")
    await init_db()
    add_trace("DB initialized")
    
    add_trace("Including routers...")
    dp.include_router(bot_router)
    dp.include_router(router_scheduler)
    add_trace("Routers included")
    
    add_trace("Starting scheduler...")
    scheduler.start()
    add_trace("Scheduler started")
    
    # Delete webhook to ensure polling works
    try:
        add_trace("Deleting webhook...")
        await bot.delete_webhook(drop_pending_updates=False)
        add_trace("Webhook deleted")
    except Exception as e:
        add_trace(f"WARNING: Failed to delete webhook: {e}")
        
    add_trace("Starting polling task...")
    polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    add_trace("Polling task created")
    
    yield
    
    add_trace("Lifespan shutting down...")
    polling_task.cancel()
    add_trace("Polling task cancelled")
    await bot.session.close()
    add_trace("Bot session closed")
    scheduler.shutdown()
    add_trace("Scheduler shutdown")

app = FastAPI(lifespan=lifespan)

from aiogram.types import ErrorEvent
import traceback

@dp.errors()
async def global_error_handler(event: ErrorEvent):
    # Format the traceback from the exception object
    tb_str = "".join(traceback.format_exception(type(event.exception), event.exception, event.exception.__traceback__))
    set_error(tb_str)
    add_trace(f"AIOGRAM ERROR: {tb_str}")
    print(f"AIOGRAM ERROR: {tb_str}")

@app.get("/debug_error")
def get_debug_error():
    from utils.trace import last_error
    return {"last_error": last_error}

@app.get("/trace")
def get_trace():
    return {"trace": execution_trace}

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
