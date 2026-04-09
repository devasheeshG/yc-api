"""Pydantic models for every object in the YC API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Partner(BaseModel):
    """YC group partner assigned to a company."""

    name: Optional[str] = None
    url: Optional[str] = None


class Founder(BaseModel):
    """Company founder."""

    user_id: Optional[int] = None
    full_name: Optional[str] = None
    title: Optional[str] = None
    founder_bio: Optional[str] = None
    is_active: Optional[bool] = None
    linkedin_url: Optional[str] = None
    x_url: Optional[str] = None
    avatar_thumb_url: Optional[str] = None
    email: Optional[str] = None


class Job(BaseModel):
    """Open job posting."""

    id: Optional[int] = None
    title: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    type: Optional[str] = None
    role: Optional[str] = None
    role_type: Optional[str] = None
    salary_range: Optional[str] = None
    equity_range: Optional[str] = None
    experience: Optional[str] = None
    visa: Optional[str] = None
    skills: List[str] = []


class News(BaseModel):
    """Press/news item."""

    title: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None


class Launch(BaseModel):
    """Launch YC post."""

    id: Optional[int] = None
    title: Optional[str] = None
    tagline: Optional[str] = None
    body: Optional[str] = None
    url: Optional[str] = None
    votes: Optional[int] = None
    created_at: Optional[str] = None


class Company(BaseModel):
    """A Y Combinator company with all available data."""

    # Core fields (from Algolia)
    id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    former_names: List[str] = []
    small_logo_thumb_url: Optional[str] = None
    website: Optional[str] = None
    all_locations: Optional[str] = None
    long_description: Optional[str] = None
    one_liner: Optional[str] = None
    team_size: Optional[int] = None
    industry: Optional[str] = None
    subindustry: Optional[str] = None
    launched_at: Optional[int] = None
    tags: List[str] = []
    tags_highlighted: List[str] = []
    top_company: Optional[bool] = None
    isHiring: Optional[bool] = None
    nonprofit: Optional[bool] = None
    batch: Optional[str] = None
    status: Optional[str] = None
    industries: List[str] = []
    regions: List[str] = []
    stage: Optional[str] = None
    app_video_public: Optional[bool] = None
    demo_day_video_public: Optional[bool] = None
    app_answers: Optional[Dict[str, Any]] = None
    question_answers: Optional[bool] = None
    url: Optional[str] = None
    api: Optional[str] = None

    # Enriched fields (from detail page scraping)
    year_founded: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    x_url: Optional[str] = None
    fb_url: Optional[str] = None
    cb_url: Optional[str] = None
    github_url: Optional[str] = None
    logo_url: Optional[str] = None
    app_video_url: Optional[str] = None
    dday_video_url: Optional[str] = None
    primary_partner: Optional[Partner] = None
    company_photos: List[str] = []
    founders: List[Founder] = []
    jobs: List[Job] = []
    news: List[News] = []
    launches: List[Launch] = []

    model_config = {"extra": "allow"}


class MetaEntry(BaseModel):
    """A single entry in the meta.json index."""

    name: str
    count: int
    api: str


class Meta(BaseModel):
    """Top-level meta.json response."""

    last_updated: Optional[str] = None
    readme: Optional[str] = None
    companies: Dict[str, MetaEntry] = {}
    tags: Dict[str, MetaEntry] = {}
    industries: Dict[str, MetaEntry] = {}
    batches: Dict[str, MetaEntry] = {}
