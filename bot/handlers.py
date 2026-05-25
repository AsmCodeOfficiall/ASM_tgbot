# Ivan: /start + прийом відповідей стендапу (що зробив / які проблеми)
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.messages import MSG_START

from bot.keyboards import build_start_keyboard
from api.db import async_session
from api.routes import join_team_by_invite_code


router = Router()


def _parse_start_payload(text: str | None) -> str | None:
    if not text:
        return None
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else None


@router.message(CommandStart())
async def start(message: Message):
    payload = _parse_start_payload(message.text)
    invite_code = None
    welcome_text = MSG_START

    if payload and payload.startswith("invite_"):
        invite_code = payload[len("invite_"):]
        user_data = {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
        }

        try:
            async with async_session() as session:
                await join_team_by_invite_code(
                    session,
                    user_data,
                    invite_code,
                    payout_percent=0.0,
                )
            welcome_text = (
                MSG_START
                + "\n\nВи приєдналися до команди. Відкрийте дашборд, щоб одразу встановити свій персональний відсоток виплат."
            )
        except ValueError as exc:
            welcome_text = (
                MSG_START
                + f"\n\nНе вдалося приєднатися до команди: {exc}. Відкрийте дашборд, щоб продовжити."
            )

    await message.answer(text=welcome_text, reply_markup=build_start_keyboard(invite_code))
