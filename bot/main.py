# Ivan: старт бота, polling, підключити handlers і scheduler
import asyncio
import logging
from api.db import init_db

from bot.scheduler import scheduler
from bot.bot_dp import dp, bot

from bot.handlers import router
from bot.scheduler import router_scheduler


async def main():
    dp.include_router(router=router)
    dp.include_router(router=router_scheduler)

    scheduler.start()
    # await init_db() # Fledif inits db in run.py lifespan, so bot doesn't need to
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[#] PROG EXIT")
