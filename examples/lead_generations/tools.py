import asyncio
import time
from typing import Any, Dict, List

import httpx
import tiktoken
from html_to_markdown import convert
from html_to_markdown.options import ConversionOptions

from config import get_settings
from logger import get_logger

settings = get_settings()
logger = get_logger()
tknzr = tiktoken.get_encoding("cl100k_base")


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "web_search",
        "description": (
            "Search the web using Brave Search API. Returns titles, URLs, and "
            "descriptions for the top results. Use this to research companies, "
            "founders, products, news, and anything else."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "scrape_url",
        "description": (
            "Fetch a web page and return its content as clean markdown. "
            "Use this to read company websites, blog posts, news articles, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch and convert to markdown.",
                },
            },
            "required": ["url"],
        },
    },
]

class RateLimiter:
    """Token-bucket rate limiter for async calls (requests per minute)."""

    def __init__(self, rpm: int):
        self._interval = 60.0 / rpm if rpm > 0 else 0
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            wait = self._interval - (now - self._last_call)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_call = time.monotonic()


search_limiter = RateLimiter(settings.BRAVE_SEARCH_RPM)
scrape_limiter = RateLimiter(settings.WEBSITE_SCRAPE_RPM)

async def web_search(query: str, http_client: httpx.AsyncClient) -> str:
    """Search the web using Brave Search API."""
    await search_limiter.acquire()

    resp = await http_client.get(
        "https://api.search.brave.com/res/v1/web/search",
        params={"q": query, "count": settings.BRAVE_SEARCH_MAX_RESULTS},
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": settings.BRAVE_SEARCH_API_KEY,
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    results = data.get("web", {}).get("results", [])
    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. [{r['title']}]({r['url']})\n   {r['description']}")

    return "\n\n".join(lines)

async def scrape_url(url: str, http_client: httpx.AsyncClient) -> str:
    """Fetch a URL and return its content as clean markdown."""
    await scrape_limiter.acquire()

    try:
        resp = await http_client.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=20,
            follow_redirects=True,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        return f"Error fetching {url}: {e}"

    content_type = resp.headers["content-type"]
    if not content_type.startswith(("text/html", "application/xhtml")):
        return f"Non-HTML content type: {content_type}. Cannot parse."

    # convert() is sync Rust FFI — fast, no executor needed
    md = (convert(resp.text, options=ConversionOptions(skip_images=True, extract_metadata=False))["content"] or "").strip()

    if len(md) > settings.WEBSITE_SCRAPE_MAX_LENGTH:
        md = md[: settings.WEBSITE_SCRAPE_MAX_LENGTH] + "\n\n... [content truncated]"

    return md if md else "Page returned no readable content."

async def handle_tool_call(
    name: str, input_data: Dict[str, Any], http_client: httpx.AsyncClient
) -> str:
    """Route a tool call to the right handler and return the result string."""
    logger.info(f"Tool call: {name} ({input_data})")

    try:
        if name == "web_search":
            result = await web_search(input_data["query"], http_client)
        elif name == "scrape_url":
            result = await scrape_url(input_data["url"], http_client)
        else:
            result = f"Unknown tool: {name}"
    except Exception as e:
        logger.error(f"Tool error: {name} — {e}")
        return f"Error executing {name}: {e}"

    logger.debug(f"Tool result: {name} — {len(tknzr.encode(result))} tokens")
    return result
