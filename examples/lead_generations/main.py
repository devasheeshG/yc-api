import json

import anthropic
from yc_api import YCClient, Company, CompanyStatus

from config import get_settings
from logger import get_logger

settings = get_settings()
logger = get_logger()

MODEL = "claude-sonnet-4-6"
MAX_AGENT_TURNS = 50

def main() -> None:
    yc = YCClient()

    # Fetch all companies from the YC API
    companies = yc.get_all()
    logger.info(f"Fetched {len(companies)} total companies")

    # Filter: keep only active companies
    companies = [c for c in companies if c.status in [CompanyStatus.ACTIVE, CompanyStatus.PUBLIC]]
    logger.info(f"Filtered to {len(companies)} active companies")

    # Sort: newest first (by id descending)
    companies = sorted(companies, key=lambda c: c.id or 0, reverse=True)
    logger.info(f"Sorted {len(companies)} companies by id descending")


if __name__ == "__main__":
    main()
