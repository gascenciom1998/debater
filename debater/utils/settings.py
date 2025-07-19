from os import getenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "debater"
    mode: str = getenv("MODE", "development")
    redis_url: str = getenv("REDIS_URL", "redis://localhost:6379")
    openai_api_key: str = getenv("OPENAI_API_KEY")
    ai_model: str = getenv("AI_MODEL", "gpt-4-turbo")
