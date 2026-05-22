from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str = "sqlite+aiosqlite:///./api/data/app.db"
    DEV_TELEGRAM_ID_1: int = 0
    DEV_TELEGRAM_ID_2: int = 0
    DEV_TELEGRAM_ID_3: int = 0

    from pydantic import field_validator

    @field_validator("DEV_TELEGRAM_ID_1", "DEV_TELEGRAM_ID_2", "DEV_TELEGRAM_ID_3", mode="before")
    def empty_string_to_zero(cls, v):
        if v == "" or v is None:
            return 0
        return v

    class Config:
        env_file = ".env"


settings = Settings()
