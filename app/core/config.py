from typing import Any, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    FRONTEND_URL: str

    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        extra="ignore",
    )

    @field_validator("FIREBASE_PRIVATE_KEY")
    def parse_private_key(cls, v: str) -> str:
        return v.replace("\\n", "\n")

    @property
    def firebase_credentials(self) -> Dict[str, Any]:
        return {
            "type": "service_account",
            "project_id": self.FIREBASE_PROJECT_ID,
            "private_key": self.FIREBASE_PRIVATE_KEY,
            "client_email": self.FIREBASE_CLIENT_EMAIL,
        }

settings = Settings(); # type: ignore
