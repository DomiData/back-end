from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, FilePath

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    FRONTEND_URL: str
    POPULATE_DB: bool = False
    GOOGLE_API_KEY: str
    FIREBASE_CREDENTIALS_PATH: FilePath

    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        extra="ignore",
    )


settings = Settings()  # type: ignore
