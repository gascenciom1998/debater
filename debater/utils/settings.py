from os import getenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "debater"
    mode: str
    dbpath: str

    class Config:
        env_file = f"debater/envs/{getenv('MODE')}.env"
