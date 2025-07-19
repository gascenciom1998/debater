from os import getenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "debater"
    mode: str
    dbpath: str
    redis_url: str = getenv("REDIS_URL", "redis://localhost:6379")
    openai_api_key: str = getenv("OPENAI_API_KEY")

    class Config:
        env_file = f"debater/envs/{getenv('MODE')}.env"
