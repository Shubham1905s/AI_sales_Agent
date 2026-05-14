from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    DATA_FILE: str = "data/leads.json"

    APP_ENV: str = "development"

    model_config = ConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
