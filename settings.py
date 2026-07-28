from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache

class AppSetting(BaseSettings):
    cors_origins:list[str] = Field(alias="cors.origins")

@lru_cache
def get_settings():
    return AppSetting() # pyright: ignore
