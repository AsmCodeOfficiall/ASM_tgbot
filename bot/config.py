from pydantic import BaseModel
from dotenv import load_dotenv
from os import getenv
load_dotenv()


class __Config():
    BOT_TOKEN: str
    WEBAPP_URL: str
    REPORT_CHAT_ID: str


config = __Config(
    BOT_TOKEN = getenv("BOT_TOKEN"),
    WEBAPP_URL = getenv("WEBAPP_URL")
)