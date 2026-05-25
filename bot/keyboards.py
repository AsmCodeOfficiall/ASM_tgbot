# Ivan: кнопка Web App — URL з WEBAPP_URL у .env
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.web_app_info import WebAppInfo

from bot.config import settings


def build_start_keyboard(invite_code: str | None = None) -> InlineKeyboardMarkup:
    webapp_url = settings.WEBAPP_URL.rstrip("/")
    if invite_code:
        webapp_url = f"{webapp_url}?invite_code={invite_code}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Відкрити Дашборд", web_app=WebAppInfo(url=webapp_url))]
    ])