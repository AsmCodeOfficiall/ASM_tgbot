import traceback
from fastapi import APIRouter
from aiogram.types import Update
from bot.bot_dp import bot, dp
from aiogram.exceptions import TelegramBadRequest

router_test = APIRouter()

@router_test.get("/test_start")
async def test_start_command():
    """
    This endpoint simulates a Telegram /start message to verify if the bot's 
    internal logic and outbound connection to Telegram are working.
    """
    fake_update = {
        "update_id": 999999999,
        "message": {
            "message_id": 1,
            "date": 1716300000,
            "chat": {
                "id": 1,  # Fake chat ID so Telegram rejects it (verifies outbound connection)
                "type": "private"
            },
            "text": "/start",
            "from": {
                "id": 1,
                "is_bot": False,
                "first_name": "TestUser"
            }
        }
    }
    
    try:
        telegram_update = Update(**fake_update)
        # This will trigger the start handler, clear state, and try to send a message
        await dp.feed_update(bot=bot, update=telegram_update)
        return {"status": "success", "message": "Handler completed without sending error (unexpected for fake ID)"}
    except TelegramBadRequest as e:
        if "chat not found" in str(e):
            return {
                "status": "success", 
                "message": "Bot successfully reached Telegram API and processed the /start command. Telegram rejected the fake chat ID as expected."
            }
        return {"status": "error", "error_type": "TelegramBadRequest", "details": str(e)}
    except Exception as e:
        return {
            "status": "error", 
            "error_type": type(e).__name__, 
            "details": str(e), 
            "traceback": traceback.format_exc()
        }
