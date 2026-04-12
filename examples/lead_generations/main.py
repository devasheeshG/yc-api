import asyncio
import json
import re
from typing import List, Dict, Optional

from anthropic import AsyncAnthropic as AsyncAnthropicClient
import httpx
from notion_client import AsyncClient as NotionAsyncClient
from pydantic import ValidationError
from yc_api import YCClient, Company, CompanyStatus

from config import get_settings
from logger import current_company, get_logger
from models import AgentResult, NotionLead
from prompts import SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, handle_tool_call

settings = get_settings()
logger = get_logger()


async def run_agent(
    anthropic_client: AsyncAnthropicClient,
    http_client: httpx.AsyncClient,
    company: Company,
) -> Optional[AgentResult]:
    """Run the research agent for a single company.

    The agent researches the company using web_search and scrape_url tools,
    then outputs a JSON block validated against the AgentResult schema.
    """
    # Serialize the company to JSON for the agent prompt
    company_json = company.model_dump_json(indent=4)
    logger.info(f"Running agent for: {company.name} ({company.batch})")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Research the following YC company and produce the complete outreach package.\n\n"
                        f"```json\n{company_json}\n```"
                    ),
                }
            ],
        }
    ]

    turn = 0
    while True:
        response = await anthropic_client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            thinking={"type": "enabled", "budget_tokens": settings.ANTHROPIC_THINKING_BUDGET},
            cache_control={"type": "ephemeral"},
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOL_DEFINITIONS
        )

        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        if response.stop_reason == "end_turn":
            logger.info(f"Agent finished after {turn + 1} turns")
            try:
                text = re.sub(r'^```json\s*|^```\s*', '', assistant_content[0].text, flags=re.MULTILINE).strip()
                raw = json.loads(text)
                return AgentResult.model_validate(raw)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Failed to parse agent result: {e}, retrying...")
                messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": f"Your output failed validation: {e}\n\nPlease fix and try again."}],
                })
                turn += 1

        elif response.stop_reason == "tool_use":
            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    result = await handle_tool_call(block.name, block.input, http_client)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
            turn += 1

        elif response.stop_reason == "max_tokens":
            logger.warning(f"Hit max_tokens at turn {turn}, asking agent to continue...")
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": f"Your output was cut off. Please make sure the JSON is complete and under {settings.ANTHROPIC_MAX_TOKENS} tokens."}],
            })
            turn += 1

        else:
            logger.error(f"Agent stopped: stop_reason={response.stop_reason}, turn={turn}")
            return None


async def process_company(
    company: Company,
    anthropic_client: AsyncAnthropicClient,
    http_client: httpx.AsyncClient,
    notion_client: NotionAsyncClient,
    data_source_id: str,
) -> None:
    """Run the agent for one company and push the result to Notion."""
    current_company.set(company.name)
    try:
        result = await run_agent(anthropic_client, http_client, company)
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        return

    if result is None:
        logger.error("No result returned")
        return

    # Build the Notion lead from the agent result
    lead = NotionLead.from_agent_result(result, company)

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
        timeout=httpx.Timeout(2400.0, connect=20.0),
    )

    # Discover the data_source_id from the Notion database
    db = await notion_client.databases.retrieve(database_id=settings.NOTION_DATABASE_ID)
    data_source_id = db["data_sources"][0]["id"]
    logger.info(f"Notion data_source_id: {data_source_id}")

    # Verify all required columns exist via the data source schema
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
    ds = await notion_client.request(path=f"data_sources/{data_source_id}", method="GET")
    ds_properties = ds["properties"]
    missing = []
    for col_name, col_type in REQUIRED_COLUMNS.items():
        prop = ds_properties.get(col_name)
        if prop is None:
            missing.append(f"{col_name} ({col_type})")
        elif prop["type"] != col_type:
            missing.append(f"{col_name} (expected {col_type}, got {prop['type']})")
    if missing:
        logger.error(f"Notion data source is missing required columns: {', '.join(missing)}")
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
