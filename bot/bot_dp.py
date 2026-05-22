import socket
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from bot.config import settings

class IPv4AiohttpSession(AiohttpSession):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._connector_init["family"] = socket.AF_INET

session = IPv4AiohttpSession()
bot = Bot(token=settings.BOT_TOKEN, session=session)
dp = Dispatcher()