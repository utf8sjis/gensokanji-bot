from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Post backend
    x_post_backend: str = Field(default="twitter")

    # Twitter API credentials
    twitter_api_key: str = Field(default="")
    twitter_api_key_secret: str = Field(default="")
    twitter_access_token: str = Field(default="")
    twitter_access_token_secret: str = Field(default="")

    # Xquik API credentials
    xquik_api_key: str = Field(default="")
    xquik_account: str = Field(default="")
    xquik_create_tweet_url: str = Field(default="https://xquik.com/api/v1/x/tweets")

    # Supabase credentials
    database_url: str = Field(default="")
    database_key: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
