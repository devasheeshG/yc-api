from yc_api import YCClient, CompanyStatus

from logger import get_logger

logger = get_logger()

def main() -> None:
    client = YCClient()

    # Fetch all companies from the YC API
    companies = client.get_all()
    logger.info(f"Fetched {len(companies)} total companies")

    # Filter: keep only active companies
    companies = [c for c in companies if c.status in [CompanyStatus.ACTIVE, CompanyStatus.PUBLIC]]
    logger.info(f"Filtered to {len(companies)} active companies")

    # Sort: newest first (by id descending)
    companies = sorted(companies, key=lambda c: c.id or 0, reverse=True)
    logger.info(f"Sorted {len(companies)} companies by id descending")


if __name__ == "__main__":
    main()
