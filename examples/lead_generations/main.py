import asyncio
import json
import re
from typing import List, Dict, Optional
from urllib.parse import quote

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
            text_block = next((b for b in assistant_content if b.type == "text"), None)
            if text_block is None or not text_block.text:
                block_types = [b.type for b in assistant_content]
                logger.warning(f"No text block in response (block types: {block_types}), retrying...")
                messages.pop()
                messages.append({
                    "role": "user",
                    "content": [{"type": "text", "text": "Please research the company and produce the complete output in text block."}],
                })
                turn += 1
                continue
            logger.info(f"Agent finished after {turn + 1} turns")
            try:
                raw_text = text_block.text.strip()
                matches = re.findall(r'```(?:json)?\s*([\s\S]*?)```', raw_text)
                text = matches[-1] if matches else raw_text
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

    # Build Notion page body blocks from structured qualified_lead_data
    children: List[Dict] = []
    if result.qualified_lead_data:
        data = result.qualified_lead_data

        def _heading1(text: str) -> Dict:
            return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

        def _heading2(text: str) -> Dict:
            return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

        def _heading3(text: str) -> Dict:
            return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

        def _paragraph(text: str) -> List[Dict]:
            blocks = []
            for i in range(0, len(text), 2000):
                blocks.append({
                    "object": "block", "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": text[i:i + 2000]}}]},
                })
            return blocks

        def _bulleted(text: str) -> Dict:
            return {
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]},
            }

        def _bulleted_link(label: str, url: str) -> Dict:
            return {
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [
                    {"type": "text", "text": {"content": f"{label}: "}},
                    {"type": "text", "text": {"content": url, "link": {"url": url}}},
                ]},
            }

        def _divider() -> Dict:
            return {"object": "block", "type": "divider", "divider": {}}

        def _callout(text: str, emoji: str) -> List[Dict]:
            rich_text = [
                {"type": "text", "text": {"content": text[i:i + 2000]}}
                for i in range(0, len(text), 2000)
            ]
            return [{"object": "block", "type": "callout", "callout": {"rich_text": rich_text, "icon": {"type": "emoji", "emoji": emoji}, "color": "gray_background"}}]

        def _code_block(text: str, language: str = "json") -> List[Dict]:
            rich_text = [
                {"type": "text", "text": {"content": text[i:i + 2000]}}
                for i in range(0, len(text), 2000)
            ]
            return [{"object": "block", "type": "code", "code": {"rich_text": rich_text, "language": language}}]

        def _send_email_link(to: str, subject: str, body: str) -> Dict:
            mailto_url = f"mailto:{to}?subject={quote(subject, safe='')}&body={quote(body, safe='')}"
            return {
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Send Email", "link": {"url": mailto_url}}}]},
            }

        # Company Description
        children.append(_heading1("Company Description"))
        children.extend(_paragraph(data.company_description))

        children.append(_divider())

        # Qualification Assessment
        q = data.qualification
        children.append(_heading1("Qualification Assessment"))
        children.append(_heading3("LLM Usage"))
        children.extend(_paragraph(q.llm_usage))
        children.append(_heading3("Memory Fit"))
        children.extend(_paragraph(q.memory_fit))
        children.append(_heading3("Stage and Timing"))
        children.extend(_paragraph(q.stage_and_timing))

        children.append(_divider())

        # Their Problem: core challenge, what they likely do today, and specific pain points
        children.append(_heading1("Their Problem"))
        children.append(_heading3("Core Challenge"))
        children.extend(_paragraph(data.their_problem.core_challenge))
        children.append(_heading3("Current Likely Approach"))
        children.extend(_paragraph(data.their_problem.current_likely_approach))
        children.append(_heading3("Pain Points"))
        for point in data.their_problem.pain_points:
            children.append(_bulleted(point))

        children.append(_divider())

        # Integration: each integration point with where it plugs in, how, and value delivered
        children.append(_heading1("Integration"))
        for idx, ip in enumerate(data.integration.integration_points, 1):
            children.append(_heading3(f"Integration Point {idx}: {ip.where}"))
            children.append(_bulleted(f"How: {ip.how}"))
            children.append(_bulleted(f"Value Delivered: {ip.value_delivered}"))

        children.append(_divider())

        # Outreach: one section per founder, each with three channels (email, linkedin, twitter).
        # Each channel has an initial message and three follow-ups.
        children.append(_heading1("Outreach"))
        for founder in data.outreach:
            children.append(_heading2(founder.founder_name))
            if founder.founder_email:
                children.append(_bulleted_link("Email", founder.founder_email))
            if founder.founder_linkedin_url:
                children.append(_bulleted_link("LinkedIn", founder.founder_linkedin_url))
            if founder.founder_twitter_url:
                children.append(_bulleted_link("Twitter/X", founder.founder_twitter_url))

            # Email channel: show subject + body separately
            children.append(_heading3("Email"))
            for label, msg in [("Initial Message", founder.email.initial_message), ("Follow-up 1", founder.email.follow_up_1), ("Follow-up 2", founder.email.follow_up_2), ("Follow-up 3", founder.email.follow_up_3)]:
                children.append(_bulleted(f"{label}:"))
                children.extend(_callout(f"Subject: {msg.subject}\n\n{msg.body}", "✉️"))
                to_email = founder.founder_email or "placeholder@example.com"
                children.append(_send_email_link(to_email, msg.subject, msg.body))

            # LinkedIn channel: optional subject + body
            children.append(_heading3("LinkedIn"))
            for label, msg in [("Initial Message", founder.linkedin.initial_message), ("Follow-up 1", founder.linkedin.follow_up_1), ("Follow-up 2", founder.linkedin.follow_up_2), ("Follow-up 3", founder.linkedin.follow_up_3)]:
                children.append(_bulleted(f"{label}:"))
                text = f"Subject: {msg.subject}\n\n{msg.body}" if msg.subject else msg.body
                children.extend(_callout(text, "💼"))

            # Twitter/X channel: body only
            children.append(_heading3("Twitter/X"))
            for label, msg in [("Initial Message", founder.twitter.initial_message), ("Follow-up 1", founder.twitter.follow_up_1), ("Follow-up 2", founder.twitter.follow_up_2), ("Follow-up 3", founder.twitter.follow_up_3)]:
                children.append(_bulleted(f"{label}:"))
                children.extend(_callout(msg.body, "🐦"))

            children.append(_divider())

        # Append full AgentResult JSON for programmatic access later
        result_json = result.model_dump_json(indent=2)
        children.append(_heading1("Raw Data (JSON)"))
        children.extend(_code_block(result_json))

    # Push to Notion — create page with first batch, then append remaining blocks
    BATCH_SIZE = 100
    try:
        first_batch = children[:BATCH_SIZE]
        page = await notion_client.pages.create(
            parent={"data_source_id": data_source_id},
            properties=lead.to_notion_properties(),
            children=first_batch,
        )

        # Append remaining blocks in batches of 100
        remaining = children[BATCH_SIZE:]
        page_id = page["id"]
        for i in range(0, len(remaining), BATCH_SIZE):
            batch = remaining[i:i + BATCH_SIZE]
            await notion_client.blocks.children.append(block_id=page_id, children=batch)

        logger.info(
            f"{'Qualified' if lead.qualified else 'Unqualified'} lead pushed "
            f"({len(children)} blocks in {1 + (max(0, len(children) - BATCH_SIZE) + BATCH_SIZE - 1) // BATCH_SIZE} requests)"
        )

    except Exception as e:
        logger.error(f"Notion push failed: {e}")


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
