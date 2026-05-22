# Ivan: кнопка Web App — URL з WEBAPP_URL у .env
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import settings


keyboard_start = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Open website", url=settings.WEBAPP_URL)]
    ])