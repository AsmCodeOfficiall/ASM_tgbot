# Ivan: кнопка Web App — URL з WEBAPP_URL у .env
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.web_app_info import WebAppInfo

from bot.config import settings

inline_keyboard = []
if settings.WEBAPP_URL:
    inline_keyboard.append([InlineKeyboardButton(text="Відкрити Дашборд", web_app=WebAppInfo(url=settings.WEBAPP_URL))])

keyboard_start = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)