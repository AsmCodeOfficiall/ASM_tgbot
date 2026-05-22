# Ivan: /start + прийом відповідей стендапу (що зробив / які проблеми)
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.messages import MSG_START

from bot.keyboards import keyboard_start


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(text=MSG_START, 
                         reply_markup=keyboard_start
                         )
