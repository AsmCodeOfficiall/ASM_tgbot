import asyncio
import logging

from bot.scheduler import scheduler
from bot.bot_dp import dp, bot
from bot.handlers import router
from bot.scheduler import router_scheduler

async def main():
    dp.include_router(router=router)
    dp.include_router(router=router_scheduler)
    scheduler.start()
    logging.info("Bot setup complete (Webhook mode)")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
