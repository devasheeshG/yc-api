import asyncio
import time
from typing import Any, Dict, List

import httpx
from html_to_markdown import convert

from config import get_settings
from logger import get_logger

settings = get_settings()
logger = get_logger()


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
