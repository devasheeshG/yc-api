from typing import List, Literal, Optional

from pydantic import BaseModel, Field



class NotionLead(BaseModel):
    """Maps to the Notion database columns."""
    company_name: str
    batch: str
    website_url: str
    yc_url: str
    qualified: bool
    fit_score: Optional[Literal["HIGH", "MEDIUM", "LOW"]] = None
    reason: str
    status: Optional[str] = None

    @classmethod
    def from_notion_page(cls, page: dict) -> "NotionLead":
        """Parse a Notion API page response into a NotionLead.

        Raises ValueError if required fields are missing or malformed.
        """
        props = page.get("properties")
        if props is None:
            raise ValueError("Page has no 'properties' key")

        title_items = props.get("Company Name", {}).get("title")
        if not title_items:
            raise ValueError("Missing or empty 'Company Name' title")
        company_name = title_items[0]["plain_text"]

        batch_items = props.get("Batch", {}).get("rich_text")
        if not batch_items:
            raise ValueError("Missing or empty 'Batch' rich_text")
        batch = batch_items[0]["plain_text"]

        website_url = props.get("Website URL", {}).get("url")
        if website_url is None:
            raise ValueError("Missing 'Website URL'")

        yc_url = props.get("YC URL", {}).get("url")
        if yc_url is None:
            raise ValueError("Missing 'YC URL'")

        qualified_prop = props.get("Qualified")
        if qualified_prop is None or "checkbox" not in qualified_prop:
            raise ValueError("Missing 'Qualified' checkbox")
        qualified = qualified_prop["checkbox"]

        fit_score_prop = props.get("Fit Score", {}).get("select")
        fit_score = fit_score_prop["name"] if fit_score_prop else None

        reason_items = props.get("Reason", {}).get("rich_text")
        if not reason_items:
            raise ValueError("Missing or empty 'Reason' rich_text")
        reason = reason_items[0]["plain_text"]

        status_prop = props.get("Status", {}).get("select")
        status = status_prop["name"] if status_prop else None

        return cls(
            company_name=company_name,
            batch=batch,
            website_url=website_url,
            yc_url=yc_url,
            qualified=qualified,
            fit_score=fit_score,
            reason=reason,
            status=status,
        )

