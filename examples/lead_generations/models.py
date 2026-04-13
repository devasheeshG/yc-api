from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator
from yc_api import Company

class QualificationAssessment(BaseModel):
    """Assessment of whether the company uses LLMs and how memory fits."""
    llm_usage: str = Field(description="How does the company use LLMs? Customer-facing, internal workflows, or both? Be specific about what features or products involve LLMs.")
    memory_fit: str = Field(description="How would persistent memory across sessions improve their LLM usage? Which specific interactions would benefit?")
    stage_and_timing: str = Field(description="Company stage, team size, and readiness to adopt new infrastructure.")


class TheirProblem(BaseModel):
    core_challenge: str = Field(description="Specific memory/context problem tied to their product.")
    current_likely_approach: str = Field(description="What they are probably doing today, with evidence.")
    pain_points: List[str] = Field(description="Pain points tied to their actual product.")


class IntegrationPoint(BaseModel):
    where: str = Field(description="Specific part of their product.")
    how: str = Field(description="How Recallr plugs in.")
    value_delivered: str = Field(description="Concrete outcome for the user.")


class Integration(BaseModel):
    integration_points: List[IntegrationPoint]


class EmailMessage(BaseModel):
    """A single email with subject line and body as separate fields."""
    subject: str = Field(description="Email subject line. Must follow the Subject Line Playbook formulas.")
    body: str = Field(description="Email body text. Do NOT include the subject line here.")


class SocialMessage(BaseModel):
    """A single LinkedIn or Twitter message. No subject line, just the message text."""
    body: str = Field(description="The message text. Must be under 260 characters.")


class EmailChannel(BaseModel):
    """4-message email sequence for a single founder."""
    initial_message: EmailMessage = Field(description="First outreach email.")
    follow_up_1: EmailMessage = Field(description="First follow-up email.")
    follow_up_2: EmailMessage = Field(description="Second follow-up email.")
    follow_up_3: EmailMessage = Field(description="Third follow-up email (breakup).")


class SocialChannel(BaseModel):
    """4-message sequence for LinkedIn or Twitter."""
    initial_message: SocialMessage = Field(description="First outreach message.")
    follow_up_1: SocialMessage = Field(description="First follow-up message.")
    follow_up_2: SocialMessage = Field(description="Second follow-up message.")
    follow_up_3: SocialMessage = Field(description="Third follow-up message.")


class FounderOutreach(BaseModel):
    """Outreach content for a single founder across all channels."""

    founder_name: str = Field(description="Full name of the founder.")
    founder_email: Optional[str] = Field(default=None, description="Founder's email address, taken directly from the YC input data.")
    founder_linkedin_url: Optional[str] = Field(default=None, description="Founder's LinkedIn profile URL, taken directly from the YC input data.")
    founder_twitter_url: Optional[str] = Field(default=None, description="Founder's X/Twitter profile URL, taken directly from the YC input data.")
    email: EmailChannel = Field(description="Email outreach sequence for this founder.")
    linkedin: SocialChannel = Field(description="LinkedIn outreach sequence for this founder.")
    twitter: SocialChannel = Field(description="X/Twitter outreach sequence for this founder.")


class QualifiedLeadData(BaseModel):
    """Detailed analysis data, only present for qualified leads."""
    company_description: str = Field(
        description="5-6 sentence summary of what the company does, their product, target market, and how they use AI. Written for the founder to quickly understand the company at a glance.",
    )
    qualification: QualificationAssessment
    their_problem: TheirProblem
    integration: Integration
    outreach: List[FounderOutreach] = Field(description="Per-founder outreach content across LinkedIn, Twitter and Email.")


class AgentResult(BaseModel):
    """Structured output from the lead research agent."""

    qualified: bool = Field(description="Whether the company is a qualified lead for Recallr.")
    fit_score: Optional[Literal["HIGH", "MEDIUM", "LOW"]] = Field(
        default=None,
        description="Only for qualified leads: HIGH, MEDIUM, or LOW.",
    )
    reason: str = Field(
        description="If qualified: fit rationale (2-3 sentences). If not qualified: disqualification reason (3-4 sentences).",
        max_length=5000,
    )

    # Detailed data for qualified leads
    qualified_lead_data: Optional[QualifiedLeadData] = Field(
        default=None,
        description="Detailed analysis and outreach content. Required when qualified=true, omit when qualified=false.",
    )

    @model_validator(mode="after")
    def validate_qualified_fields(self) -> "AgentResult":
        if self.qualified:
            if self.fit_score is None:
                raise ValueError("fit_score is required when qualified=true")
            if self.qualified_lead_data is None:
                raise ValueError("qualified_lead_data is required when qualified=true")
        else:
            if self.fit_score is not None:
                raise ValueError("fit_score must be omitted when qualified=false")
            if self.qualified_lead_data is not None:
                raise ValueError("qualified_lead_data must be omitted when qualified=false")
        return self


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

    def to_notion_properties(self) -> dict:
        """Serialize to Notion API page properties dict."""
        properties: dict = {
            "Company Name": {"title": [{"text": {"content": self.company_name}}]},
            "Batch": {"rich_text": [{"text": {"content": self.batch}}]},
            "Website URL": {"url": self.website_url},
            "YC URL": {"url": self.yc_url},
            "Qualified": {"checkbox": self.qualified},
            "Reason": {"rich_text": [{"text": {"content": self.reason}}]},
        }

        if self.status is not None:
            properties["Status"] = {"select": {"name": self.status}}

        if self.fit_score is not None:
            properties["Fit Score"] = {"select": {"name": self.fit_score}}

        return properties
