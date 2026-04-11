import asyncio
import json
from typing import List, Optional

from anthropic import AsyncAnthropic as AsyncAnthropicClient
import httpx
from notion_client import AsyncClient as NotionAsyncClient
from yc_api import YCClient, Company, CompanyStatus

from config import get_settings
from logger import get_logger
from models import AgentResult, NotionLead
from prompts import SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, handle_tool_call

settings = get_settings()
logger = get_logger()

MODEL = "claude-sonnet-4-6"
MAX_AGENT_TURNS = 50
YC_DIRECTORY_BASE = "https://www.ycombinator.com/companies"
async def run_agent(
    anthropic_client: AsyncAnthropicClient,
    http_client: httpx.AsyncClient,
    company: Company,
) -> AgentResult:

async def main() -> None:
    yc = YCClient()

    # Fetch all companies from the YC directory
    companies = yc.get_all()
    logger.info(f"Fetched {len(companies)} total companies")

    # Keep only active/public companies
    companies = [c for c in companies if c.status in [CompanyStatus.ACTIVE, CompanyStatus.PUBLIC]]
    logger.info(f"Filtered to {len(companies)} active companies")

    # Process newest first (highest id = most recent batch)
    companies = sorted(companies, key=lambda c: c.id or 0, reverse=True)

    # Initialize async clients
    notion_client = NotionAsyncClient(auth=settings.NOTION_API_KEY)
    anthropic_client = AsyncAnthropicClient(
        api_key=settings.ANTHROPIC_API_KEY,
        base_url=settings.ANTHROPIC_BASE_URL,
    )

    # Discover the data_source_id from the Notion database
    db = await notion_client.databases.retrieve(database_id=settings.NOTION_DATABASE_ID)
    data_source_id = db["data_sources"][0]["id"]
    logger.info(f"Notion data_source_id: {data_source_id}")

    # Verify all required columns exist in the Notion database
    REQUIRED_COLUMNS = {
        "Company Name": "title",
        "Batch": "rich_text",
        "Website URL": "url",
        "YC URL": "url",
        "Qualified": "checkbox",
        "Fit Score": "select",
        "Reason": "rich_text",
        "Status": "select",
    }
    db_properties = db["properties"]
    missing = []
    for col_name, col_type in REQUIRED_COLUMNS.items():
        prop = db_properties.get(col_name)
        if prop is None:
            missing.append(f"{col_name} ({col_type})")
        elif prop["type"] != col_type:
            missing.append(f"{col_name} (expected {col_type}, got {prop['type']})")
    if missing:
        logger.error(f"Notion database is missing required columns: {', '.join(missing)}")
        await notion_client.aclose()
        return

    # Deduplicate by collecting company names already in Notion
    processed_names: set = set()
    start_cursor = None
    while True:
        query_body = {"page_size": 100}
        if start_cursor:
            query_body["start_cursor"] = start_cursor

        resp = await notion_client.request(
            path=f"data_sources/{data_source_id}/query",
            method="POST",
            body=query_body,
        )

        for page in resp["results"]:
            title_items = page["properties"]["Company Name"]["title"]
            if title_items:
                name = title_items[0]["plain_text"].strip().lower()
                if name:
                    processed_names.add(name)

        if not resp["has_more"]:
            break
        start_cursor = resp["next_cursor"]

    logger.info(f"Found {len(processed_names)} already-processed companies in Notion")

    # Filter out already-processed companies by name
    companies = [c for c in companies if (c.name or "").strip().lower() not in processed_names]
    logger.info(f"{len(companies)} new companies to process")

    if not companies:
        logger.info("No new companies to process. Done.")
        await notion_client.aclose()
        return

    # Process companies in parallel with bounded concurrency
    semaphore = asyncio.Semaphore(settings.MAX_PARALLEL_COMPANIES)
    completed = 0

    async def _bounded(company: Company, http: httpx.AsyncClient) -> None:
        nonlocal completed
        async with semaphore:
            await process_company(company, anthropic_client, http, notion_client, data_source_id)
        completed += 1
        logger.info(f"Completed {completed}/{len(companies)}")

    async with httpx.AsyncClient() as http_client:
        async with asyncio.TaskGroup() as tg:
            for c in companies:
                tg.create_task(_bounded(c, http_client))

    await notion_client.aclose()
    logger.info("All companies processed.")


if __name__ == "__main__":
    asyncio.run(main())
