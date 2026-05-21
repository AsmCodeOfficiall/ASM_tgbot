# Ivan: старт бота, polling, підключити handlers і scheduler
import asyncio
import logging
from api.db import init_db

from scheduler import scheduler
from bot_dp import dp, bot

from handlers import router
from scheduler import router_scheduler


async def main():
    dp.include_router(router=router)
    dp.include_router(router=router_scheduler)

    scheduler.start()
    await init_db() # NOTE: idk how Fledif inits db, correct later
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[#] PROG EXIT")
