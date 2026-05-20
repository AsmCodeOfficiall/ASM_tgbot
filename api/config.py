from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str = "sqlite+aiosqlite:///./api/data/app.db"
    DEV_TELEGRAM_ID_1: int = 0
    DEV_TELEGRAM_ID_2: int = 0
    DEV_TELEGRAM_ID_3: int = 0

    class Config:
        env_file = ".env"


settings = Settings()
