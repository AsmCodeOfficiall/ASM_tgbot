# Ivan: /start + прийом відповідей стендапу (що зробив / які проблеми)
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.messages import MSG_START

from bot.keyboards import keyboard_start
from aiogram import F
from aiogram.types import CallbackQuery
from bot.states import GetReportFSM
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(text=MSG_START, 
                         reply_markup=keyboard_start
                         )

@router.callback_query(F.data == "write_report")
async def write_report_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✍️ Опиши, що ти зробив сьогодні і чи є якісь блокери/проблеми:")
    await state.set_state(GetReportFSM.waiting_for_report)
    await callback.answer()
