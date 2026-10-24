"""Sync + async HTTP client for the YC API."""

from __future__ import annotations

from typing import List, Optional

import httpx

from .models import Company, Meta

API_BASE = "https://devasheeshg.github.io/yc-api"


class YCClient:
    """Typed client for the YC Companies API.

    Usage::

        from yc_api import YCClient

        client = YCClient()
        companies = client.get_all()
        company = client.get_company("winter-2026", "airbnb")
        hiring = client.get_hiring()
    """

    def __init__(self, base_url: str = API_BASE, timeout: float = 30.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_json(self, path: str) -> object:
        with httpx.Client(timeout=self._timeout) as c:
            resp = c.get(f"{self._base}/{path}")
            resp.raise_for_status()
            return resp.json()

    async def _aget_json(self, path: str) -> object:
        async with httpx.AsyncClient(timeout=self._timeout) as c:
            resp = await c.get(f"{self._base}/{path}")
            resp.raise_for_status()
            return resp.json()

    def _parse_companies(self, data: object) -> List[Company]:
        if not isinstance(data, list):
            raise ValueError(f"Expected list, got {type(data).__name__}")
        return [Company.model_validate(item) for item in data]

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    def get_meta(self) -> Meta:
        """Fetch the API index (meta.json)."""
        return Meta.model_validate(self._get_json("meta.json"))

    async def aget_meta(self) -> Meta:
        """Async version of :meth:`get_meta`."""
        return Meta.model_validate(await self._aget_json("meta.json"))

    # ------------------------------------------------------------------
    # Company lists
    # ------------------------------------------------------------------

    def get_all(self) -> List[Company]:
        """Fetch every company."""
        return self._parse_companies(self._get_json("companies/all.json"))

    async def aget_all(self) -> List[Company]:
        """Async version of :meth:`get_all`."""
        return self._parse_companies(await self._aget_json("companies/all.json"))

    def get_top(self) -> List[Company]:
        """Fetch top YC companies."""
        return self._parse_companies(self._get_json("companies/top.json"))

    async def aget_top(self) -> List[Company]:
        return self._parse_companies(await self._aget_json("companies/top.json"))

    def get_hiring(self) -> List[Company]:
        """Fetch companies that are currently hiring."""
        return self._parse_companies(self._get_json("companies/hiring.json"))

    async def aget_hiring(self) -> List[Company]:
        return self._parse_companies(await self._aget_json("companies/hiring.json"))

    def get_nonprofit(self) -> List[Company]:
        """Fetch nonprofit companies."""
        return self._parse_companies(self._get_json("companies/nonprofit.json"))

    async def aget_nonprofit(self) -> List[Company]:
        return self._parse_companies(await self._aget_json("companies/nonprofit.json"))

    # ------------------------------------------------------------------
    # Individual lookups
    # ------------------------------------------------------------------

    def get_company(self, batch_slug: str, company_slug: str) -> Company:
        """Fetch a single company by its batch and company slug."""
        data = self._get_json(f"batches/{batch_slug}/{company_slug}.json")
        return Company.model_validate(data)

    async def aget_company(self, batch_slug: str, company_slug: str) -> Company:
        data = await self._aget_json(f"batches/{batch_slug}/{company_slug}.json")
        return Company.model_validate(data)

    def get_batch(self, batch_slug: str) -> List[Company]:
        """Fetch all companies in a batch (e.g. ``'winter-2026'``)."""
        return self._parse_companies(self._get_json(f"batches/{batch_slug}.json"))

    async def aget_batch(self, batch_slug: str) -> List[Company]:
        return self._parse_companies(await self._aget_json(f"batches/{batch_slug}.json"))

    def get_industry(self, industry_slug: str) -> List[Company]:
        """Fetch all companies in an industry."""
        return self._parse_companies(self._get_json(f"industries/{industry_slug}.json"))

    async def aget_industry(self, industry_slug: str) -> List[Company]:
        return self._parse_companies(await self._aget_json(f"industries/{industry_slug}.json"))

    def get_tag(self, tag_slug: str) -> List[Company]:
        """Fetch all companies with a given tag."""
        return self._parse_companies(self._get_json(f"tags/{tag_slug}.json"))

    async def aget_tag(self, tag_slug: str) -> List[Company]:
        return self._parse_companies(await self._aget_json(f"tags/{tag_slug}.json"))

    # ------------------------------------------------------------------
    # Search helpers
    # ------------------------------------------------------------------

    def search(
        self,
        *,
        batch: Optional[str] = None,
        industry: Optional[str] = None,
        tag: Optional[str] = None,
        hiring: Optional[bool] = None,
        top: Optional[bool] = None,
        nonprofit: Optional[bool] = None,
    ) -> List[Company]:
        """Client-side filter over all companies.

        Fetches the full list once and filters in memory.  For large-scale
        use, prefer the specific ``get_*`` methods which hit pre-built JSON
        endpoints.
        """
        companies = self.get_all()
        return self._filter(companies, batch=batch, industry=industry, tag=tag,
                            hiring=hiring, top=top, nonprofit=nonprofit)

    async def asearch(
        self,
        *,
        batch: Optional[str] = None,
        industry: Optional[str] = None,
        tag: Optional[str] = None,
        hiring: Optional[bool] = None,
        top: Optional[bool] = None,
        nonprofit: Optional[bool] = None,
    ) -> List[Company]:
        companies = await self.aget_all()
        return self._filter(companies, batch=batch, industry=industry, tag=tag,
                            hiring=hiring, top=top, nonprofit=nonprofit)

    @staticmethod
    def _filter(
        companies: List[Company],
        *,
        batch: Optional[str] = None,
        industry: Optional[str] = None,
        tag: Optional[str] = None,
        hiring: Optional[bool] = None,
        top: Optional[bool] = None,
        nonprofit: Optional[bool] = None,
    ) -> List[Company]:
        results = companies
        if batch is not None:
            results = [c for c in results if c.batch == batch]
        if industry is not None:
            results = [c for c in results if industry in (c.industries or [])]
        if tag is not None:
            results = [c for c in results if tag in (c.tags or [])]
        if hiring is not None:
            results = [c for c in results if c.isHiring == hiring]
        if top is not None:
            results = [c for c in results if c.top_company == top]
        if nonprofit is not None:
            results = [c for c in results if c.nonprofit == nonprofit]
        return results
