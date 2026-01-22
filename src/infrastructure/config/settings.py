from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # API Config
    app_name: str = "LeadAdapter"
    app_version: str = "1.0.0"
    debug: bool = False

    # OpenAI Config
    openai_api_key: str = Field()
    openai_model: str = Field(default="gpt-5.1")
    openai_timeout: int = Field(default=30)

    # Redis Config (opcional)
    redis_url: str | None = Field(default=None)
    cache_ttl_seconds: int = Field(default=3600)

    # Quality Gate Config
    quality_threshold: float = Field(default=6.0)
    max_generation_attempts: int = Field(default=3)

    # Rate Limiting
    rate_limit_requests: int = Field(default=100)
    rate_limit_window_seconds: int = Field(default=60)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_setting() -> Settings:
    return Settings()  # type: ignore[call-arg]
