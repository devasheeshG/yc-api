"""Pydantic models for every object in the YC API."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, model_validator


def _empty_str_to_none(data: dict) -> dict:
    """Convert empty-string values to None so the SDK always uses None for missing data."""
    return {k: (None if v == "" else v) for k, v in data.items()}


class CompanyStatus(str, Enum):
    """Company operating status."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ACQUIRED = "Acquired"
    PUBLIC = "Public"


class CompanyStage(str, Enum):
    """Company stage."""
    EARLY = "Early"
    GROWTH = "Growth"


class CompanyIndustry(str, Enum):
    """Primary industry."""
    B2B = "B2B"
    CONSUMER = "Consumer"
    EDUCATION = "Education"
    FINTECH = "Fintech"
    GOVERNMENT = "Government"
    HEALTHCARE = "Healthcare"
    INDUSTRIALS = "Industrials"
    REAL_ESTATE_AND_CONSTRUCTION = "Real Estate and Construction"
    UNSPECIFIED = "Unspecified"


class CompanySubindustry(str, Enum):
    """Company sub-industry."""
    B2B = "B2B"
    B2B_ANALYTICS = "B2B -> Analytics"
    B2B_ENGINEERING_PRODUCT_AND_DESIGN = "B2B -> Engineering, Product and Design"
    B2B_FINANCE_AND_ACCOUNTING = "B2B -> Finance and Accounting"
    B2B_HUMAN_RESOURCES = "B2B -> Human Resources"
    B2B_INFRASTRUCTURE = "B2B -> Infrastructure"
    B2B_LEGAL = "B2B -> Legal"
    B2B_MARKETING = "B2B -> Marketing"
    B2B_OFFICE_MANAGEMENT = "B2B -> Office Management"
    B2B_OPERATIONS = "B2B -> Operations"
    B2B_PRODUCTIVITY = "B2B -> Productivity"
    B2B_RECRUITING_AND_TALENT = "B2B -> Recruiting and Talent"
    B2B_RETAIL = "B2B -> Retail"
    B2B_SALES = "B2B -> Sales"
    B2B_SECURITY = "B2B -> Security"
    B2B_SUPPLY_CHAIN_AND_LOGISTICS = "B2B -> Supply Chain and Logistics"
    CONSUMER = "Consumer"
    CONSUMER_APPAREL_AND_COSMETICS = "Consumer -> Apparel and Cosmetics"
    CONSUMER_CONSUMER_ELECTRONICS = "Consumer -> Consumer Electronics"
    CONSUMER_CONTENT = "Consumer -> Content"
    CONSUMER_FOOD_AND_BEVERAGE = "Consumer -> Food and Beverage"
    CONSUMER_GAMING = "Consumer -> Gaming"
    CONSUMER_HOME_AND_PERSONAL = "Consumer -> Home and Personal"
    CONSUMER_JOB_AND_CAREER_SERVICES = "Consumer -> Job and Career Services"
    CONSUMER_SOCIAL = "Consumer -> Social"
    CONSUMER_TRANSPORTATION_SERVICES = "Consumer -> Transportation Services"
    CONSUMER_TRAVEL_LEISURE_AND_TOURISM = "Consumer -> Travel, Leisure and Tourism"
    CONSUMER_VIRTUAL_AND_AUGMENTED_REALITY = "Consumer -> Virtual and Augmented Reality"
    EDUCATION = "Education"
    FINTECH = "Fintech"
    FINTECH_ASSET_MANAGEMENT = "Fintech -> Asset Management"
    FINTECH_BANKING_AND_EXCHANGE = "Fintech -> Banking and Exchange"
    FINTECH_CONSUMER_FINANCE = "Fintech -> Consumer Finance"
    FINTECH_CREDIT_AND_LENDING = "Fintech -> Credit and Lending"
    FINTECH_INSURANCE = "Fintech -> Insurance"
    FINTECH_PAYMENTS = "Fintech -> Payments"
    GOVERNMENT = "Government"
    HEALTHCARE = "Healthcare"
    HEALTHCARE_CONSUMER_HEALTH_AND_WELLNESS = "Healthcare -> Consumer Health and Wellness"
    HEALTHCARE_DIAGNOSTICS = "Healthcare -> Diagnostics"
    HEALTHCARE_DRUG_DISCOVERY_AND_DELIVERY = "Healthcare -> Drug Discovery and Delivery"
    HEALTHCARE_HEALTHCARE_IT = "Healthcare -> Healthcare IT"
    HEALTHCARE_HEALTHCARE_SERVICES = "Healthcare -> Healthcare Services"
    HEALTHCARE_INDUSTRIAL_BIO = "Healthcare -> Industrial Bio"
    HEALTHCARE_MEDICAL_DEVICES = "Healthcare -> Medical Devices"
    HEALTHCARE_THERAPEUTICS = "Healthcare -> Therapeutics"
    INDUSTRIALS = "Industrials"
    INDUSTRIALS_AGRICULTURE = "Industrials -> Agriculture"
    INDUSTRIALS_AUTOMOTIVE = "Industrials -> Automotive"
    INDUSTRIALS_AVIATION_AND_SPACE = "Industrials -> Aviation and Space"
    INDUSTRIALS_CLIMATE = "Industrials -> Climate"
    INDUSTRIALS_DEFENSE = "Industrials -> Defense"
    INDUSTRIALS_DRONES = "Industrials -> Drones"
    INDUSTRIALS_ENERGY = "Industrials -> Energy"
    INDUSTRIALS_MANUFACTURING_AND_ROBOTICS = "Industrials -> Manufacturing and Robotics"
    REAL_ESTATE_AND_CONSTRUCTION = "Real Estate and Construction"
    REAL_ESTATE_AND_CONSTRUCTION_CONSTRUCTION = "Real Estate and Construction -> Construction"
    REAL_ESTATE_AND_CONSTRUCTION_HOUSING_AND_REAL_ESTATE = "Real Estate and Construction -> Housing and Real Estate"
    UNSPECIFIED = "Unspecified"


class JobType(str, Enum):
    """Employment type."""
    FULL_TIME = "Full-time"
    INTERNSHIP = "Internship"
    CONTRACT = "Contract"
    CO_FOUNDER = "Co-founder"


class JobRole(str, Enum):
    """Role category."""
    DESIGN = "Design"
    ENGINEERING = "Engineering"
    FINANCE = "Finance"
    LEGAL = "Legal"
    MARKETING = "Marketing"
    OPERATIONS = "Operations"
    PRODUCT = "Product"
    RECRUITING_HR = "Recruiting & HR"
    SALES = "Sales"
    SCIENCE = "Science"
    SUPPORT = "Support"


class JobVisa(str, Enum):
    """Visa sponsorship status."""
    US_ONLY = "US citizen/visa only"
    NOT_REQUIRED = "US citizenship/visa not required"
    WILL_SPONSOR = "Will sponsor"


class JobExperience(str, Enum):
    """Required experience level."""
    ONE_PLUS = "1+ years"
    THREE_PLUS = "3+ years"
    SIX_PLUS = "6+ years"
    ELEVEN_PLUS = "11+ years"
    ANY = "Any (new grads ok)"


class Partner(BaseModel):
    """YC group partner assigned to a company."""

    name: str
    url: str

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: dict) -> dict:
        return _empty_str_to_none(data) if isinstance(data, dict) else data


class Founder(BaseModel):
    """Company founder."""

    user_id: int
    full_name: str
    title: str
    founder_bio: Optional[str] = None
    is_active: bool
    linkedin_url: Optional[str] = None
    x_url: Optional[str] = None
    avatar_thumb_url: str
    email: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: dict) -> dict:
        return _empty_str_to_none(data) if isinstance(data, dict) else data


class Job(BaseModel):
    """Open job posting."""

    id: int
    title: str
    url: str
    location: str
    type: JobType
    role: JobRole
    role_type: Optional[str] = None
    salary_range: Optional[str] = None
    equity_range: Optional[str] = None
    experience: Optional[JobExperience] = None
    visa: JobVisa
    skills: List[str] = []

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: dict) -> dict:
        return _empty_str_to_none(data) if isinstance(data, dict) else data


class AppAnswer(BaseModel):
    """A single application answer."""

    question: str
    answer: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: dict) -> dict:
        return _empty_str_to_none(data) if isinstance(data, dict) else data


class QuestionAnswer(BaseModel):
    """A single free-response question answer."""

    question: str
    answer: str

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: dict) -> dict:
        return _empty_str_to_none(data) if isinstance(data, dict) else data


class News(BaseModel):
    """Press/news item."""

    title: str
    url: str
    date: str

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: dict) -> dict:
        return _empty_str_to_none(data) if isinstance(data, dict) else data


class Launch(BaseModel):
    """Launch YC post."""

    id: int
    title: str
    tagline: str
    body: str
    url: str
    votes: int
    created_at: str

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: dict) -> dict:
        return _empty_str_to_none(data) if isinstance(data, dict) else data


class Company(BaseModel):
    """A Y Combinator company with all available data."""

    # Core fields (from Algolia)
    id: int
    name: str
    slug: str
    former_names: List[str] = []
    small_logo_thumb_url: str
    website: Optional[str] = None
    all_locations: Optional[str] = None
    long_description: Optional[str] = None
    one_liner: Optional[str] = None
    team_size: Optional[int] = None
    industry: CompanyIndustry
    subindustry: CompanySubindustry
    launched_at: int
    tags: List[str] = []
    tags_highlighted: List[str] = []
    top_company: Optional[bool] = None
    isHiring: bool
    nonprofit: bool
    batch: str
    status: CompanyStatus
    industries: List[str] = []
    regions: List[str] = []
    stage: CompanyStage
    app_video_public: bool
    demo_day_video_public: bool
    app_answers: Optional[List[AppAnswer]] = None
    question_answers: Optional[List[QuestionAnswer]] = None
    url: str
    api: str

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
    app_video_transcript: Optional[str] = None
    dday_video_transcript: Optional[str] = None
    primary_partner: Optional[Partner] = None
    company_photos: List[str] = []
    founders: List[Founder] = []
    jobs: List[Job] = []
    news: List[News] = []
    launches: List[Launch] = []

    model_config = {"extra": "allow"}

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: dict) -> dict:
        return _empty_str_to_none(data) if isinstance(data, dict) else data


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
