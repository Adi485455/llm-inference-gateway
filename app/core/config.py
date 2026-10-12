from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LLM Inference Gateway"
    app_env: str = "development"
    log_level: str = "INFO"

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300
    gateway_api_key: str
    max_concurrent_requests: int = 5


settings = Settings()