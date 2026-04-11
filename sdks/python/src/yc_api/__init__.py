"""Typed Python client for the unofficial Y Combinator companies API."""

from .client import YCClient
from .models import (
    AppAnswer,
    Company,
    CompanyIndustry,
    CompanyStage,
    CompanyStatus,
    Founder,
    Job,
    JobRole,
    JobType,
    JobVisa,
    Launch,
    Meta,
    MetaEntry,
    News,
    Partner,
    QuestionAnswer,
)

__all__ = [
    "AppAnswer",
    "CompanyIndustry",
    "CompanyStage",
    "CompanyStatus",
    "YCClient",
    "Company",
    "Founder",
    "Job",
    "JobRole",
    "JobType",
    "JobVisa",
    "Launch",
    "Meta",
    "MetaEntry",
    "News",
    "Partner",
    "QuestionAnswer",
]
