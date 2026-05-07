from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/recruiting"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    upload_dir: Path = Path("uploads")
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()
