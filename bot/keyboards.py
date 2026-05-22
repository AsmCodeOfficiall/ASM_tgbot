# Ivan: кнопка Web App — URL з WEBAPP_URL у .env
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.web_app_info import WebAppInfo

from bot.config import settings

keyboard_start = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Відкрити Дашборд", web_app=WebAppInfo(url=settings.WEBAPP_URL))]
    ])