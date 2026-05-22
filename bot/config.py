from pydantic_settings import BaseSettings


class __Settings(BaseSettings):
    BOT_TOKEN: str
    WEBAPP_URL: str = ""
    TELEGRAM_REPORT_CHAT_ID: str = ""
    TELEGRAM_ALERT_CHAT_ID: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = __Settings()