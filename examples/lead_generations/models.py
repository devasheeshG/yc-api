from typing import List, Literal, Optional

from pydantic import BaseModel, Field
from yc_api import Company


class AgentResult(BaseModel):
    """Structured output from the lead research agent."""

    qualified: bool
    fit_score: Optional[Literal["HIGH", "MEDIUM", "LOW"]] = Field(
        default=None,
        description="Only for qualified leads: HIGH, MEDIUM, or LOW.",
    )
    reason: str = Field(
        description="If qualified: fit rationale (2-3 sentences). If not qualified: disqualification reason.",
    )

    # Detailed data for qualified leads
    qualified_lead_data: Optional[QualifiedLeadData] = Field(
        default=None,
        description="Detailed analysis and outreach content. Required when qualified=true, omit when qualified=false.",
    )

    @classmethod
    def anthropic_json_schema(cls) -> dict:
        """Return a resolved JSON schema compatible with Anthropic's output_config.

        Pydantic's model_json_schema() generates schemas with $defs and $ref pointers
        for nested models, but Anthropic's json_schema output format requires:
            1. All references inlined (no $ref / $defs)
            2. Every object type must have "additionalProperties": false

        This method recursively resolves all $ref pointers by substituting the
        referenced definition inline, strips the top level $defs block, and adds
        additionalProperties: false to every object with properties.
        """
        schema = cls.model_json_schema()
        defs = schema.get("$defs", {})

        def _resolve(node):
            if isinstance(node, dict):
                # Replace $ref with the inlined definition
                if "$ref" in node:
                    ref_name = node["$ref"].split("/")[-1]
                    return _resolve(defs[ref_name])
                # Recurse into all values, dropping the now unnecessary $defs key
                resolved = {k: _resolve(v) for k, v in node.items() if k != "$defs"}
                # Anthropic requires additionalProperties: false on all object types
                if resolved.get("type") == "object" and "properties" in resolved:
                    resolved["additionalProperties"] = False
                return resolved
            if isinstance(node, list):
                return [_resolve(item) for item in node]
            return node

        return _resolve(schema)


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

    @classmethod
    def from_agent_result(cls, result: AgentResult, company: Company) -> "NotionLead":
        """Build a NotionLead from the agent result and the original Company object."""
        return cls(
            company_name=company.name,
            batch=company.batch,
            website_url=company.website,
            yc_url=company.url,
            qualified=result.qualified,
            fit_score=result.fit_score,
            reason=result.reason,
            status="New" if result.qualified else None,
        )
