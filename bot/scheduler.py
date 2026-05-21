# Gleb: APScheduler — 19:00 розсилка в ЛС, 21:00 зведення тимліду (Europe/Kyiv)
from aiogram import Router
from bot import bot, dp
from states import GetReportFSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message

from config import settings

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from api.db import User

from messages import MSG_REPORT_REQUEST, MSG_REPORT_ACCEPTED

import logging


router_scheduler = Router("schedule_router")


async def reports_request():
    # TODO: GET USER IDs FROM DB
    user_id_list = [...]

    for user_id in user_id_list:
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


async def reports_send():
    # TODO: Get them from somewhere like
    # await db.get_today_reports() idk
    # TODO: Upon receiving format them accordingly
    reports = [...]

    for report in reports:
        await bot.send_message(chat_id=settings.TELEGRAM_REPORT_CHAT_ID, text=report)


@router_scheduler.message(GetReportFSM.waiting_for_report)
async def handle_standup_report(message: Message, state: FSMContext):
    # Grab text user sent
    report_text = message.text
    user_id = message.from_user.id

    try:
    
    # TODO: Save it somewhere like
    # await db.save_report(user_id, report_text) idk

    # Send confirmation to user
        await message.answer(text=MSG_REPORT_ACCEPTED)
    except Exception as e:
        logging.error(f"Error handling user report: {e}")
        
    
    # Clear the state!
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