from aiogram import Bot, Dispatcher
from bot.config import settings


bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()