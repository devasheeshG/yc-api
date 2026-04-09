"""Typed Python client for the unofficial Y Combinator companies API."""

from .client import YCClient
from .models import (
    Company,
    Founder,
    Job,
    Launch,
    Meta,
    MetaEntry,
    News,
    Partner,
)

__all__ = [
    "YCClient",
    "Company",
    "Founder",
    "Job",
    "Launch",
    "Meta",
    "MetaEntry",
    "News",
    "Partner",
]
