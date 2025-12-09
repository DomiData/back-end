from pydantic import BaseSettings, PostgreSQLDsn, SettingsConfigDict
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DATABASE_URL: PostgreSQLDsn
    SECRET_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_CLIENT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
    )

settings = Settings();
