# Ivan: send_message у TELEGRAM_ALERT_CHAT_ID — GitHub і текст стендапу
import logging
from .bot import bot
from config import settings

async def send_github_alert(text: str):
    """Sends the formatted GitHub alert to the team chat."""
    try:
        # Send to the specific Telegram Group
        await bot.send_message(
            chat_id=settings.TELEGRAM_ALERT_CHAT_ID, 
            text=text,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Failed to send GitHub alert to Telegram: {e}")