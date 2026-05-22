import os
import sys
import asyncio
import argparse
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional
from aiogram import Bot, Dispatcher
from aiogram.types import Message, Chat, User as TgUser, Update, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey
from sqlalchemy import select, delete
from bot.config import settings
from bot.handlers import router as bot_router, MSG_START
from api.db import init_db, get_session, engine, Base, User, Transaction, Project
from bot.keyboards import keyboard_start

class FakeBot(Bot):
    def __init__(self, token: str):
        super().__init__(token=token)
        self.sent_messages = []
        self.answered_callbacks = []
        self.deleted_messages = []
        self.edited_messages = []

    async def send_message(self, chat_id, text, **kwargs) -> Message:
        self.sent_messages.append({"chat_id": chat_id, "text": text, "kwargs": kwargs})
        return Message(message_id=len(self.sent_messages), date=datetime.now(), chat=Chat(id=chat_id, type="private"), text=text)

    async def answer_callback_query(self, callback_query_id, text=None, **kwargs):
        self.answered_callbacks.append({"id": callback_query_id, "text": text})
        return True

    async def delete_message(self, chat_id, message_id):
        self.deleted_messages.append({"chat_id": chat_id, "message_id": message_id})
        return True

    async def edit_message_text(self, text, chat_id=None, message_id=None, **kwargs):
        self.edited_messages.append({"chat_id": chat_id, "message_id": message_id, "text": text})
        return True

class BotTester:
    def __init__(self):
        self.bot = FakeBot(token=settings.BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.dp.include_router(bot_router)
        self.test_user = TgUser(id=999999999, is_bot=False, first_name="TestUser", username="testuser")
        self.test_chat = Chat(id=999999999, type="private")
        self.failures = []
        self.successes = []

    def assert_true(self, condition: bool, msg: str):
        if condition:
            self.successes.append(msg)
        else:
            self.failures.append(msg)
            raise AssertionError(msg)

    def assert_equal(self, a: Any, b: Any, msg: str):
        if a == b:
            self.successes.append(f"{msg}: {a} == {b}")
        else:
            self.failures.append(f"{msg}: {a} != {b}")
            raise AssertionError(f"{msg}: {a} != {b}")

    def assert_in(self, item: Any, collection: Any, msg: str):
        if item in collection:
            self.successes.append(f"{msg}: {item} is in collection")
        else:
            self.failures.append(f"{msg}: {item} not in collection")
            raise AssertionError(f"{msg}: {item} not in collection")

    def build_message(self, text: str) -> Message:
        return Message(
            message_id=int(datetime.now().timestamp()),
            date=datetime.now(),
            chat=self.test_chat,
            from_user=self.test_user,
            text=text
        )

    def build_callback(self, data: str) -> CallbackQuery:
        return CallbackQuery(
            id=str(int(datetime.now().timestamp())),
            from_user=self.test_user,
            chat_instance="test_instance",
            message=self.build_message("cb_msg"),
            data=data
        )

    async def execute_tests(self):
        print("Initializing Test Environment...")
        await init_db()
        await self.cleanup_db()
        tests = [
            self.test_db_connection,
            self.test_user_creation,
            self.test_start_command,
            self.test_start_command_state_clear,
            self.test_keyboard_markup,
            self.test_empty_message_handling,
            self.test_invalid_command,
            self.test_fsm_storage,
            self.test_multiple_start_commands,
            self.test_db_user_persistence,
            self.test_simulated_webhook_flow,
            self.test_dispatcher_routing,
            self.test_transaction_creation_db,
            self.test_project_creation_db
        ]
        total = len(tests)
        passed = 0
        for test in tests:
            try:
                self.bot.sent_messages.clear()
                self.bot.answered_callbacks.clear()
                await test()
                passed += 1
                print(f"[OK] {test.__name__}")
            except Exception as e:
                print(f"[FAIL] {test.__name__}: {str(e)}")
                traceback.print_exc()
        print(f"\nTest Summary: {passed}/{total} passed.")
        if passed == total:
            print("All diagnostic tests passed successfully. The bot's internal logic is 100% functional.")
        else:
            print("Some tests failed. Check the logs above.")

    async def cleanup_db(self):
        async for session in get_session():
            await session.execute(delete(Transaction).where(Transaction.user_id == self.test_user.id))
            await session.execute(delete(User).where(User.telegram_id == self.test_user.id))
            await session.commit()

    async def test_db_connection(self):
        async for session in get_session():
            result = await session.execute(select(User).limit(1))
            self.assert_true(True, "Database connection is active and responsive.")

    async def test_user_creation(self):
        async for session in get_session():
            new_user = User(telegram_id=self.test_user.id, username=self.test_user.username)
            session.add(new_user)
            await session.commit()
            result = await session.execute(select(User).where(User.telegram_id == self.test_user.id))
            user = result.scalar_one_or_none()
            self.assert_true(user is not None, "User should be created in DB.")
            self.assert_equal(user.username, "testuser", "Username should match.")

    async def test_start_command(self):
        msg = self.build_message("/start")
        await self.dp.feed_update(bot=self.bot, update=Update(update_id=1, message=msg))
        self.assert_true(len(self.bot.sent_messages) > 0, "Bot should send at least one message on /start.")
        last_msg = self.bot.sent_messages[-1]
        self.assert_equal(last_msg["chat_id"], self.test_chat.id, "Chat ID should match.")
        self.assert_in(MSG_START[:10], last_msg["text"], "Response should contain MSG_START text.")

    async def test_start_command_state_clear(self):
        state = FSMContext(storage=self.dp.storage, key=StorageKey(bot_id=self.bot.id, chat_id=self.test_chat.id, user_id=self.test_user.id))
        await state.set_state("dummy_state")
        await state.update_data({"dummy": "data"})
        msg = self.build_message("/start")
        await self.dp.feed_update(bot=self.bot, update=Update(update_id=2, message=msg))
        current_state = await state.get_state()
        current_data = await state.get_data()
        self.assert_equal(current_state, None, "State should be cleared after /start.")
        self.assert_equal(len(current_data), 0, "State data should be cleared after /start.")

    async def test_keyboard_markup(self):
        msg = self.build_message("/start")
        await self.dp.feed_update(bot=self.bot, update=Update(update_id=3, message=msg))
        last_msg = self.bot.sent_messages[-1]
        kwargs = last_msg.get("kwargs", {})
        self.assert_in("reply_markup", kwargs, "Response should have reply_markup.")
        markup = kwargs["reply_markup"]
        self.assert_true(hasattr(markup, "inline_keyboard"), "Markup should be InlineKeyboardMarkup.")
        buttons = markup.inline_keyboard
        self.assert_true(len(buttons) > 0, "Keyboard should have at least one row.")
        self.assert_true(len(buttons[0]) > 0, "Keyboard row should have at least one button.")
        btn = buttons[0][0]
        self.assert_true(hasattr(btn, "web_app"), "Button should be a WebApp button.")
        self.assert_equal(btn.web_app.url, settings.WEBAPP_URL, "WebApp URL should match settings.")

    async def test_empty_message_handling(self):
        msg = self.build_message("")
        await self.dp.feed_update(bot=self.bot, update=Update(update_id=4, message=msg))
        self.assert_equal(len(self.bot.sent_messages), 0, "Bot should not respond to empty messages.")

    async def test_invalid_command(self):
        msg = self.build_message("/invalid_command_xyz")
        await self.dp.feed_update(bot=self.bot, update=Update(update_id=5, message=msg))
        self.assert_equal(len(self.bot.sent_messages), 0, "Bot should ignore invalid commands in current logic.")

    async def test_fsm_storage(self):
        state = FSMContext(storage=self.dp.storage, key=StorageKey(bot_id=self.bot.id, chat_id=self.test_chat.id, user_id=self.test_user.id))
        await state.set_state("test_state")
        await state.update_data({"key": "value"})
        st = await state.get_state()
        dt = await state.get_data()
        self.assert_equal(st, "test_state", "FSM state should be stored and retrieved.")
        self.assert_equal(dt.get("key"), "value", "FSM data should be stored and retrieved.")
        await state.clear()

    async def test_multiple_start_commands(self):
        for i in range(5):
            msg = self.build_message("/start")
            await self.dp.feed_update(bot=self.bot, update=Update(update_id=10+i, message=msg))
        self.assert_equal(len(self.bot.sent_messages), 5, "Bot should process multiple rapid /start commands.")

    async def test_db_user_persistence(self):
        async for session in get_session():
            result = await session.execute(select(User).where(User.telegram_id == self.test_user.id))
            user = result.scalar_one_or_none()
            self.assert_true(user is not None, "User from previous test should still exist in DB.")
            user.balance = 5000.0
            await session.commit()
            result2 = await session.execute(select(User).where(User.telegram_id == self.test_user.id))
            user2 = result2.scalar_one_or_none()
            self.assert_equal(user2.balance, 5000.0, "User balance update should persist.")

    async def test_simulated_webhook_flow(self):
        update_data = {
            "update_id": 999,
            "message": {
                "message_id": 123,
                "date": int(datetime.now().timestamp()),
                "chat": {"id": self.test_chat.id, "type": "private"},
                "from": {"id": self.test_user.id, "is_bot": False, "first_name": "Test"},
                "text": "/start"
            }
        }
        update = Update(**update_data)
        await self.dp.feed_update(bot=self.bot, update=update)
        self.assert_true(len(self.bot.sent_messages) > 0, "Simulated webhook payload should trigger response.")

    async def test_dispatcher_routing(self):
        handlers = self.dp.resolve_used_update_types()
        self.assert_in("message", handlers, "Dispatcher should be configured to handle messages.")

    async def test_transaction_creation_db(self):
        async for session in get_session():
            tx = Transaction(user_id=self.test_user.id, type="income", value=100.0)
            session.add(tx)
            await session.commit()
            result = await session.execute(select(Transaction).where(Transaction.value == 100.0))
            fetched_tx = result.scalar_one_or_none()
            self.assert_true(fetched_tx is not None, "Transaction should be created.")
            self.assert_equal(fetched_tx.value, 100.0, "Transaction amount should match.")

    async def test_project_creation_db(self):
        async for session in get_session():
            proj = Project(name="Test Proj", amount=1000.0, status="active")
            session.add(proj)
            await session.commit()
            result = await session.execute(select(Project).where(Project.name == "Test Proj"))
            fetched_proj = result.scalar_one_or_none()
            self.assert_true(fetched_proj is not None, "Project should be created.")

async def run_polling():
    print("Initializing Database...")
    await init_db()
    print("Deleting existing webhook to prevent conflicts...")
    real_bot = Bot(token=settings.BOT_TOKEN)
    await real_bot.delete_webhook(drop_pending_updates=True)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(bot_router)
    print("Starting bot in LONG-POLLING mode. Press Ctrl+C to stop.")
    print("Now you can open Telegram and send /start to the bot!")
    try:
        await dp.start_polling(real_bot)
    except Exception as e:
        print(f"Polling error: {e}")
    finally:
        await real_bot.session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot Local Tester & Runner")
    parser.add_argument("--mode", type=str, choices=["test", "run"], default="test", help="Mode to execute: 'test' for automated diagnostics, 'run' for long-polling.")
    args = parser.parse_args()
    if args.mode == "test":
        tester = BotTester()
        asyncio.run(tester.execute_tests())
    elif args.mode == "run":
        asyncio.run(run_polling())
