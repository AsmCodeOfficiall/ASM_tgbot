from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str = "sqlite+aiosqlite:///./api/data/app.db"

    # Developer Telegram IDs for budget distribution (30% each)
    DEV_TELEGRAM_ID_1: int = 0
    DEV_TELEGRAM_ID_2: int = 0
    DEV_TELEGRAM_ID_3: int = 0

    # GitHub webhook HMAC secret (Settings > Webhooks in repo)
    GITHUB_WEBHOOK_SECRET: str = ""

    # Chat where GitHub alerts are sent
    TELEGRAM_ALERT_CHAT_ID: str = ""

    # Chat where daily standup summary is sent (team lead group)
    TELEGRAM_REPORT_CHAT_ID: str = ""

    @field_validator("DEV_TELEGRAM_ID_1", "DEV_TELEGRAM_ID_2", "DEV_TELEGRAM_ID_3", mode="before")
    def empty_string_to_zero(cls, v):
        if v == "" or v is None:
            return 0
        return v

    @field_validator("DATABASE_URL", mode="before")
    def empty_string_to_db(cls, v):
        if v == "" or v is None:
            return "sqlite+aiosqlite:///./api/data/app.db"
        return v

    class Config:
        env_file = ".env"


settings = Settings()
