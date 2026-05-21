from aiogram import Bot, Dispatcher
from bot.config import config


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()