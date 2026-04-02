from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parents[2] / ".env",
            Path(__file__).resolve().parents[1] / ".env",
        ),
        extra="ignore",
    )

    database_url: str = Field(validation_alias="DATABASE_URL")
    secret_key: str = Field(validation_alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=15,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    time_zone: str = Field(default="Europe/Moscow", validation_alias="TIME_ZONE")
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080",
        validation_alias="CORS_ORIGINS",
    )
    redis_host: str = Field(default="redis", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.time_zone)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
