from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Anthropic
    ANTHROPIC_API_KEY: str
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com"
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    ANTHROPIC_MAX_TOKENS: int = 16384
    ANTHROPIC_THINKING_BUDGET: int = 8192

    # Brave Search
    BRAVE_SEARCH_API_KEY: str
    BRAVE_SEARCH_MAX_RESULTS: int = 10
    BRAVE_SEARCH_RPM: int = 30

    # Notion
    NOTION_API_KEY: str
    NOTION_DATABASE_ID: str

    # Web Scraper Tool
    WEBSITE_SCRAPE_MAX_LENGTH: int = 20_000
    WEBSITE_SCRAPE_RPM: int = 120

    # Parallelism
    MAX_PARALLEL_COMPANIES: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
