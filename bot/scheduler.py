# Gleb: APScheduler — 19:00 розсилка в ЛС, 21:00 зведення тимліду (Europe/Kyiv)
from aiogram import Router
from bot.bot_dp import bot, dp
from bot.states import GetReportFSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message

from bot.config import settings

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import aiohttp

from bot.messages import MSG_REPORT_REQUEST, MSG_REPORT_ACCEPTED, MSG_REPORTS_MISSING

from sqlalchemy import select, update
from api.db import async_session, User
import html

import logging


router_scheduler = Router()


async def reports_request():
    async with async_session() as session:
        # 1. (Optional but recommended) Clear yesterday's reports before asking
        await session.execute(
            update(User).values(standup_text=None, standup_notified=False)
        )
        await session.commit()

        # 2. GET USER IDs FROM DB (only select members who are not leaders, using distinct to avoid duplicates)
        from api.db import TeamMember
        result = await session.execute(
            select(User.telegram_id)
            .join(TeamMember, User.id == TeamMember.user_id)
            .where(TeamMember.role != "leader")
            .distinct()
        )
        user_id_list = result.scalars().all()

    for user_id in user_id_list:
        try:
            # Send the standup questions
            await bot.send_message(chat_id=user_id, text=MSG_REPORT_REQUEST)
            
            # Manually construct the FSM context for this specific user

            # !WARNING in private chats user_id == chat_id, for groups they are different
            new_user_storage_key = StorageKey(bot.id, user_id, user_id)

            # In storage param we specify WHERE(in which DP) we need to create new user state
            # Get storate from dp.storage
            # Key is like certain cell in our storage
            state = FSMContext(storage=dp.storage, key=new_user_storage_key)
            
            # Force the user into waiting_for_report state
            await state.set_state(GetReportFSM.waiting_for_report)
        except Exception as e:
            # Always catch exceptions in loops so one blocked bot doesn't break the whole schedule!
            logging.error(f"Failed to send request to {user_id}: {e}")


async def reports_send():
    async with async_session() as session:
        # Fetch users who actually submitted a report today
        result = await session.execute(
            select(User).where(User.standup_text.isnot(None))
        )
        users_with_reports = result.scalars().all()

        reports = []
        for user in users_with_reports:
            user_mention = f"<a href='tg://user?id={user.telegram_id}'>Developer</a>"
            
            # Sanitize the user's input so < and > don't break Telegram
            safe_text = html.escape(user.standup_text)
            
            text = f"👤 <b>{user_mention}</b> (Role: {user.role})\n"
            text += f"📝 <b>Звіт:</b>\n{safe_text}\n"  # Use the safe text here
            text += "──────────────"
            
            reports.append(text)
            user.standup_notified = True

        # Save the 'notified' status to the database
        await session.commit()

    # Send the formatted reports to the Team Lead / Group Chat
    if not reports:
        # Good UX: Let the team lead know the bot actually ran, but no one answered
        await bot.send_message(
            chat_id=settings.TELEGRAM_REPORT_CHAT_ID, 
            text=MSG_REPORTS_MISSING
        )
        return

    # If there are reports, combine them and send!
    final_text = "📊 <b>Звітність команди за сьогодні:</b>\n\n" + "\n\n".join(reports)
    await bot.send_message(
        chat_id=settings.TELEGRAM_REPORT_CHAT_ID,
        text=final_text,
        parse_mode="HTML"
    )


@router_scheduler.message(GetReportFSM.waiting_for_report)
async def handle_standup_report(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Будь ласка, надішліть ваш звіт текстовим повідомленням.")
        return

    if message.text.startswith("/"):
        await state.clear()
        if message.text.startswith("/start"):
            from bot.handlers import start
            await start(message)
        return

    async with async_session() as session:
        # Find the user and update their standup text
        await session.execute(
            update(User)
            .where(User.telegram_id == message.from_user.id)
            .values(standup_text=message.text)
        )
        await session.commit()
    
    await message.answer(text=MSG_REPORT_ACCEPTED)
    await state.clear()

# Create scheduler
scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")


# Add reports collecting job
scheduler.add_job(
    reports_request,
    trigger=CronTrigger(hour=19, minute=0),
    name="reports_request"
)

# Add sending job
scheduler.add_job(
    reports_send,
    trigger=CronTrigger(hour=21, minute=0),
    name="reports_send"
)

async def self_ping():
    """Pings the app to prevent Render from spinning down the free instance."""
    try:
        url = f"{settings.WEBAPP_URL.rstrip('/')}/ping"
        # We use a custom User-Agent to avoid UptimeRobot/Render generic blocking
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logging.info(f"Self-ping to {url}: {response.status}")
    except Exception as e:
        logging.error(f"Self-ping failed: {e}")

# Add keep-awake ping job every 14 minutes
scheduler.add_job(
    self_ping,
    trigger=IntervalTrigger(minutes=14),
    name="self_ping"
)