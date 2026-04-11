import asyncio
import json
import re

from anthropic import AsyncAnthropic as AsyncAnthropicClient
import httpx
from notion_client import AsyncClient as NotionAsyncClient
from yc_api import YCClient, Company, CompanyStatus

from config import get_settings
from logger import get_logger
from prompts import SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, handle_tool_call

settings = get_settings()
logger = get_logger()

MODEL = "claude-sonnet-4-6"
MAX_AGENT_TURNS = 50

async def main() -> None:
    yc = YCClient()

    # Fetch all companies
    companies = yc.get_all()
    logger.info(f"Fetched {len(companies)} total companies")

    # Filter: active/public only
    companies = [c for c in companies if c.status in [CompanyStatus.ACTIVE, CompanyStatus.PUBLIC]]
    logger.info(f"Filtered to {len(companies)} active companies")

    # Sort: newest first
    companies = sorted(companies, key=lambda c: c.id or 0, reverse=True)
    logger.info(f"Sorted {len(companies)} companies by id descending")

    # Initialize async clients
    notion = NotionAsyncClient(auth=settings.NOTION_API_KEY)
    anthropic_client = AsyncAnthropicClient(
        api_key=settings.ANTHROPIC_API_KEY,
        base_url=settings.ANTHROPIC_BASE_URL,
    )

    await notion.aclose()
    logger.info("All companies processed.")


if __name__ == "__main__":
    asyncio.run(main())
