# Ivan: старт бота, polling, підключити handlers і scheduler
import asyncio
import logging
from api.db import init_db

from bot.scheduler import scheduler
from bot.bot import dp, bot

from bot.handlers import router
from bot.scheduler import router_scheduler


async def main():
    dp.include_router(router=router)
    dp.include_router(router=router_scheduler)
    
    await init_db() # NOTE: idk how Fledif inits db, correct later
    await dp.start_polling(bot)
    scheduler.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[#] PROG EXIT")
