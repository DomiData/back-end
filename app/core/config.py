from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180

    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        extra="ignore",
    )

settings = Settings();
