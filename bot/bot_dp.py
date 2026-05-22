import socket
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from bot.config import settings

class IPv4AiohttpSession(AiohttpSession):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._connector_init["family"] = socket.AF_INET

# We do NOT initialize the session here because Uvicorn creates a new event loop.
# Initializing AiohttpSession at module level causes network requests to hang indefinitely!
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()