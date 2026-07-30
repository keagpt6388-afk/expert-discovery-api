from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    service_api_keys: str = Field(min_length=16)
    openai_api_key: str = Field(min_length=20)
    openai_model: str = "gpt-5.4"
    request_timeout_seconds: float = Field(default=90, gt=0, le=300)
    result_cache_ttl_seconds: int = Field(default=86400, ge=60, le=604800)

    @property
    def allowed_service_keys(self) -> set[str]:
        return {key.strip() for key in self.service_api_keys.split(",") if key.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
