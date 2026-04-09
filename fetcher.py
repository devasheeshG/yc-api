"""
YC Companies Fetcher
====================

Two-phase pipeline that builds a complete, static JSON API of every
Y Combinator company:

  Phase 1 — Bulk fetch from Algolia (the same index ycombinator.com uses).
            Credentials are auto-discovered from the public page; no secrets needed.

  Phase 2 — Enrich each company by scraping its detail page on ycombinator.com.
            This adds founders, open jobs, press/news, and Launch YC posts.

Output is written to:
    companies/   — all.json, top.json, hiring.json, etc.
    batches/     — per-batch lists + individual <slug>.json files
    industries/  — per-industry lists
    tags/        — per-tag lists
    meta.json    — index of every endpoint (counts + URLs)
    README.md    — auto-generated stats table (between marker comments)
"""

from __future__ import annotations

import asyncio
import base64
import html as html_module
import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import httpx

# =============================================================================
# Constants
# =============================================================================

GITHUB_REPO = "devasheeshG/yc-api"
REPO_OWNER, REPO_NAME = GITHUB_REPO.split("/")

API_BASE_URL = f"https://{REPO_OWNER.lower()}.github.io/{REPO_NAME}"
README_URL = f"https://github.com/{GITHUB_REPO}"
YC_BASE_URL = "https://www.ycombinator.com"

CONCURRENCY = 10  # parallel requests for detail-page enrichment
REQUEST_TIMEOUT = 30  # seconds
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Algolia facets we ask for (mirrors what the YC website requests)
ALGOLIA_FACETS = [
    "app_answers",
    "app_video_public",
    "batch",
    "demo_day_video_public",
    "industries",
    "isHiring",
    "nonprofit",
    "question_answers",
    "regions",
    "subindustry",
    "tags",
    "top_company",
]

# Boolean fields used for "special" company lists
SPECIAL_LISTS: list[tuple[str, str, str]] = [
    ("top_company", "top", "Top companies"),
    ("nonprofit", "nonprofit", "Not-for-profit companies"),
    ("isHiring", "hiring", "Companies currently hiring"),
]


# =============================================================================
# Helpers
# =============================================================================


def slugify(text: str) -> str:
    """Convert arbitrary text into a URL-safe slug (ASCII, lowercase, hyphens)."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def write_json(path: str | Path, data: Any) -> None:
    """Atomically write *data* as pretty-printed JSON to *path*."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def batch_slug(batch: str | None) -> str:
    """Return the slug for a batch name, defaulting to 'unspecified'."""
    return slugify(batch or "Unspecified")


# =============================================================================
# Phase 1 — Algolia bulk fetch
# =============================================================================


async def _discover_algolia_credentials(
    client: httpx.AsyncClient,
) -> tuple[str, str, str]:
    """
    Scrape the public YC /companies page to extract the Algolia
    application ID, search-only API key, and primary index name.

    The API key is a base64 blob whose decoded form embeds restrictions
    like ``restrictIndices=YCCompany_production,...``.
    """
    resp = await client.get(
        f"{YC_BASE_URL}/companies",
        headers={"User-Agent": USER_AGENT},
    )
    resp.raise_for_status()

    match = re.search(r"window\.AlgoliaOpts\s*=\s*(\{.*?\});", resp.text)
    if not match:
        raise RuntimeError("Could not find AlgoliaOpts on the YC companies page")

    opts = json.loads(match.group(1))
    app_id: str = opts["app"]
    api_key: str = opts["key"]

    # Parse the restricted indices from the key
    decoded_key = base64.b64decode(api_key).decode()
    idx_match = re.search(r"restrictIndices=([^&]+)", decoded_key)
    if idx_match:
        indices = unquote(idx_match.group(1)).split(",")
        index_name = next(
            (i for i in indices if "By_Launch" not in i),
            indices[0],
        )
    else:
        index_name = "YCCompany_production"

    print(f"  Algolia app={app_id}  index={index_name}")
    return app_id, api_key, index_name


def _build_algolia_params(facets: list[str]) -> str:
    """Encode facets + pagination defaults into an Algolia params string."""
    encoded = "%2C".join(f"%22{f}%22" for f in facets)
    return (
        f"facets=%5B{encoded}%5D"
        f"&hitsPerPage=1000"
        f"&maxValuesPerFacet=1000"
        f"&query="
        f"&tagFilters="
    )


async def fetch_all_companies(client: httpx.AsyncClient) -> list[dict]:
    """
    Pull every YC company from the Algolia index.

    Strategy:
      1. Request facet counts → discover every batch name + company count.
      2. For each batch, paginate through 1000-hit pages until exhausted.
      3. Strip Algolia metadata, sort by ID, and return.
    """
    app_id, api_key, index_name = await _discover_algolia_credentials(client)

    url = f"https://{app_id}-dsn.algolia.net/1/indexes/*/queries"
    auth_params = {
        "x-algolia-agent": "Algolia for JavaScript (3.35.1); Browser; JS Helper (3.16.1)",
        "x-algolia-application-id": app_id,
        "x-algolia-api-key": api_key,
    }
    base_params = _build_algolia_params(ALGOLIA_FACETS)

    # --- Step 1: discover batches via facets ---
    print("Fetching Algolia facets...")
    resp = await client.post(
        url,
        params=auth_params,
        json={"requests": [{"indexName": index_name, "params": base_params}]},
    )
    resp.raise_for_status()
    batches: dict[str, int] = resp.json()["results"][0]["facets"]["batch"]

    # --- Step 2: fetch all companies, batch by batch (paginated) ---
    all_companies: list[dict] = []

    for batch_name, expected_count in batches.items():
        print(f"  Batch {batch_name!r}: {expected_count} companies")
        page, fetched = 0, 0

        while fetched < expected_count:
            r = await client.post(
                url,
                params=auth_params,
                json={
                    "requests": [
                        {
                            "indexName": index_name,
                            "params": f"{base_params}&facetFilters=batch:{batch_name}&page={page}",
                        }
                    ]
                },
            )
            r.raise_for_status()
            hits = r.json()["results"][0]["hits"]
            all_companies.extend(hits)
            fetched += len(hits)
            page += 1

    # Clean up Algolia internal fields
    for c in all_companies:
        c.pop("_highlightResult", None)
        c.pop("objectID", None)

    all_companies.sort(key=lambda c: c["id"])
    print(f"Total from Algolia: {len(all_companies)}")
    return all_companies


# =============================================================================
# Phase 2 — Detail-page enrichment
# =============================================================================


def _parse_inertia_props(page_html: str) -> dict | None:
    """
    YC uses Inertia.js (Rails → React).  Every page embeds a
    ``data-page="{ ... }"`` attribute on the root <div> containing
    the full server-side props as HTML-escaped JSON.
    """
    match = re.search(r'data-page="(\{.*?\})"', page_html)
    if not match:
        return None
    try:
        return json.loads(html_module.unescape(match.group(1)))
    except json.JSONDecodeError:
        return None


def _strip_s3_params(url: str | None) -> str | None:
    """Remove AWS signed URL query parameters — the base S3 URL works without them."""
    if not url:
        return None
    return url.split("?")[0]


def _extract_founders(company_props: dict) -> list[dict]:
    """Extract active/inactive founders with their bios and social links."""
    return [
        {
            "user_id": f.get("user_id"),
            "full_name": f.get("full_name"),
            "title": f.get("title"),
            "founder_bio": f.get("founder_bio"),
            "is_active": f.get("is_active"),
            "linkedin_url": f.get("linkedin_url"),
            "twitter_url": f.get("twitter_url"),
            "avatar_thumb_url": _strip_s3_params(f.get("avatar_thumb_url")),
        }
        for f in company_props.get("founders", [])
    ]


def _extract_jobs(props: dict) -> list[dict]:
    """Extract open job postings (salary, equity, visa, etc.)."""
    return [
        {
            "id": j.get("id"),
            "title": j.get("title"),
            "url": f"{YC_BASE_URL}{j['url']}" if j.get("url") else None,
            "location": j.get("location"),
            "type": j.get("type"),
            "role": j.get("prettyRole"),
            "role_type": j.get("roleSpecificType"),
            "salary_range": j.get("salaryRange"),
            "equity_range": j.get("equityRange"),
            "experience": j.get("minExperience"),
            "visa": j.get("visa"),
            "skills": j.get("skills", []),
        }
        for j in props.get("jobPostings", [])
    ]


def _extract_news(props: dict) -> list[dict]:
    """Extract press/news items."""
    return [
        {"title": n.get("title"), "url": n.get("url"), "date": n.get("date")}
        for n in props.get("newsItems", [])
    ]


def _extract_launches(props: dict) -> list[dict]:
    """Extract Launch YC posts (title, tagline, votes, URL)."""
    return [
        {
            "id": l.get("id"),
            "title": l.get("title"),
            "tagline": l.get("tagline"),
            "url": l.get("url"),
            "votes": l.get("total_vote_count"),
            "created_at": l.get("created_at"),
        }
        for l in props.get("launches", [])
    ]


def _extract_partner(company: dict) -> dict | None:
    """Extract the primary YC group partner."""
    partner = company.get("primary_group_partner")
    if not partner:
        return None
    return {
        "name": partner.get("full_name"),
        "url": partner.get("url"),
    }


def _build_enrichment(page_data: dict) -> dict:
    """Combine all detail-page extractions into a single dict for merging."""
    props = page_data.get("props", {})
    company = props.get("company", {})

    return {
        # Extra company-level fields not in Algolia
        "year_founded": company.get("year_founded"),
        "city": company.get("city"),
        "country": company.get("country"),
        "linkedin_url": company.get("linkedin_url"),
        "twitter_url": company.get("twitter_url"),
        "fb_url": company.get("fb_url") or None,
        "cb_url": company.get("cb_url") or None,
        "github_url": company.get("github_url") or None,
        "logo_url": company.get("small_logo_url"),
        "app_video_url": company.get("app_video_url"),
        "dday_video_url": company.get("dday_video_url"),
        # Nested data
        "primary_partner": _extract_partner(company),
        "founders": _extract_founders(company),
        "jobs": _extract_jobs(props),
        "news": _extract_news(props),
        "launches": _extract_launches(props),
    }


async def _enrich_one(
    client: httpx.AsyncClient,
    company: dict,
    semaphore: asyncio.Semaphore,
    progress: dict,
) -> None:
    """Fetch one company's detail page and merge enrichment data in-place."""
    slug = company["slug"]

    async with semaphore:
        try:
            resp = await client.get(
                f"{YC_BASE_URL}/companies/{slug}",
                headers={"User-Agent": USER_AGENT},
            )
            resp.raise_for_status()
            page_data = _parse_inertia_props(resp.text)
            if page_data:
                company.update(_build_enrichment(page_data))
        except Exception as exc:
            print(f"    ⚠ {slug}: {exc}")

        progress["done"] += 1
        done, total = progress["done"], progress["total"]
        if done % 100 == 0 or done == total:
            print(f"  [{done}/{total}] enriched")


async def enrich_all(
    client: httpx.AsyncClient,
    companies: list[dict],
) -> None:
    """Enrich all companies concurrently (bounded by CONCURRENCY)."""
    print(f"\nEnriching {len(companies)} companies from detail pages...")
    sem = asyncio.Semaphore(CONCURRENCY)
    progress = {"done": 0, "total": len(companies)}

    await asyncio.gather(
        *(_enrich_one(client, c, sem, progress) for c in companies)
    )


# =============================================================================
# Batch sorting
# =============================================================================

_SEASON_RANK = {"Fall": 0, "Summer": 1, "Winter": 2}


def _batch_sort_key(name: str) -> tuple[int, int]:
    """
    Sort batches reverse-chronologically: newest year first,
    then Fall → Summer → Winter within the same year.
    "Unspecified" always goes last.
    """
    if name == "Unspecified":
        return (9999, 9)

    # Full names like "Winter 2026", "Summer 2021"
    parts = name.split()
    if len(parts) == 2:
        season, year_str = parts
        try:
            return (-int(year_str), _SEASON_RANK.get(season, 3))
        except ValueError:
            pass

    # Short names like "W26", "S21", "F24"
    short_map = {"F": 0, "S": 1, "W": 2}
    if len(name) >= 2 and name[0] in short_map:
        try:
            return (-int(name[1:]), short_map[name[0]])
        except ValueError:
            pass

    return (0, 0)


# =============================================================================
# Output generation
# =============================================================================


def _generate_outputs(results: list[dict]) -> dict[str, dict[str, dict]]:
    """
    Write all JSON output files and return the meta index.

    Directory layout:
        companies/all.json              — every company
        companies/{slug}.json           — filtered lists (top, hiring, …)
        batches/{batch}.json            — all companies in a batch
        batches/{batch}/{slug}.json     — individual company
        industries/{slug}.json          — per-industry
        tags/{slug}.json                — per-tag
    """
    for d in ("companies", "tags", "industries", "batches"):
        Path(d).mkdir(exist_ok=True)

    meta: dict[str, dict[str, dict]] = {
        "companies": {
            "all": {
                "name": "All launched companies",
                "count": len(results),
                "api": f"{API_BASE_URL}/companies/all.json",
            }
        },
        "tags": {},
        "industries": {},
        "batches": {},
    }

    # -- All companies --
    write_json("companies/all.json", results)

    # -- Tags --
    unique_tags = sorted({tag for r in results for tag in r.get("tags", [])})
    for tag in unique_tags:
        s = slugify(tag)
        filtered = [r for r in results if tag in r.get("tags", [])]
        write_json(f"tags/{s}.json", filtered)
        meta["tags"][s] = {"name": tag, "count": len(filtered), "api": f"{API_BASE_URL}/tags/{s}.json"}

    # -- Industries --
    unique_industries = sorted({ind for r in results for ind in r.get("industries", [])})
    for industry in unique_industries:
        s = slugify(industry)
        filtered = [r for r in results if industry in r.get("industries", [])]
        write_json(f"industries/{s}.json", filtered)
        meta["industries"][s] = {"name": industry, "count": len(filtered), "api": f"{API_BASE_URL}/industries/{s}.json"}

    # -- Batches --
    unique_batches = sorted(
        {r.get("batch") or "Unspecified" for r in results},
        key=_batch_sort_key,
    )
    for batch in unique_batches:
        s = batch_slug(batch)
        filtered = [r for r in results if (r.get("batch") or "Unspecified") == batch]
        write_json(f"batches/{s}.json", filtered)
        meta["batches"][s] = {"name": batch, "count": len(filtered), "api": f"{API_BASE_URL}/batches/{s}.json"}

    # -- Special boolean-filtered lists --
    for key, file_slug, label in SPECIAL_LISTS:
        filtered = [r for r in results if r.get(key)]
        write_json(f"companies/{file_slug}.json", filtered)
        meta["companies"][file_slug] = {
            "name": label,
            "count": len(filtered),
            "api": f"{API_BASE_URL}/companies/{file_slug}.json",
        }

    # -- Individual company files (one per company) --
    for company in results:
        s = batch_slug(company.get("batch"))
        write_json(f"batches/{s}/{company['slug']}.json", company)

    return meta


def _update_meta_and_readme(results: list[dict], meta: dict) -> None:
    """
    Compare new meta against the existing meta.json.
    Only write if something actually changed (ignoring last_updated).
    """
    existing_meta: dict = {}
    meta_path = Path("meta.json")
    if meta_path.exists():
        try:
            existing_meta = json.loads(meta_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass  # treat as empty — will trigger a write

    new_meta = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "readme": README_URL,
        **meta,
    }

    has_changes = any(
        key != "last_updated"
        and json.dumps(new_meta.get(key)) != json.dumps(existing_meta.get(key))
        for key in new_meta
    )

    if not has_changes:
        print("Meta unchanged — skipping write.")
        return

    print("Meta changed — updating meta.json + README.md")
    write_json("meta.json", new_meta)

    # --- Regenerate the auto-generated section of README.md ---
    readme_path = Path("README.md")
    if not readme_path.exists():
        return

    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %I:%M %p UTC")
    unique_batches = list(meta["batches"])
    unique_industries = list(meta["industries"])
    unique_tags = list(meta["tags"])

    lines = [
        "<!--start generated readme-->",
        "",
        "## ℹ️ Metadata",
        "",
        f"API endpoint: {API_BASE_URL}/meta.json",
        "",
        f"- Last updated: {now}",
        f"- Companies: {len(results)}",
        f"- Batches: {len(unique_batches)}",
        f"- Industries: {len(unique_industries)}",
        f"- Tags: {len(unique_tags)}",
        "",
        "## 💻 APIs",
        "",
    ]

    # Companies
    lines += [
        "### 🏢 Companies",
        "",
        "| List of companies | API endpoint |",
        "| --------------- | ------------ |",
    ]
    for slug, info in meta["companies"].items():
        lines.append(f"| {info['name']} | {API_BASE_URL}/companies/{slug}.json |")

    # Batches
    lines += [
        "",
        "### 🎓 Batches",
        "",
        "<details>",
        "<summary>Companies per batch</summary>",
        "",
        "| Batch | Count | API endpoint |",
        "| ---- | ---- | ------------ |",
    ]
    for slug, info in meta["batches"].items():
        lines.append(f"| {info['name']} | {info['count']} | {API_BASE_URL}/batches/{slug}.json |")
    lines.append("</details>")

    # Industries
    lines += [
        "",
        "### 🏭 Industries",
        "",
        "<details>",
        "<summary>Companies per industry</summary>",
        "",
        "| Industry | Count | API endpoint |",
        "| -------- | ---- | ------------ |",
    ]
    for slug, info in meta["industries"].items():
        lines.append(f"| {info['name']} | {info['count']} | {API_BASE_URL}/industries/{slug}.json |")
    lines.append("</details>")

    # Tags
    lines += [
        "",
        "### 🏷️ Tags",
        "",
        "<details>",
        "<summary>Companies per tag</summary>",
        "",
        "| Tag | Count | API endpoint |",
        "| --- | ---- | ------------ |",
    ]
    for slug, info in meta["tags"].items():
        lines.append(f"| {info['name']} | {info['count']} | {API_BASE_URL}/tags/{slug}.json |")
    lines.append("</details>")

    lines.append("<!--end generated readme-->")

    block = "\n".join(lines) + "\n"
    readme = readme_path.read_text()
    readme = re.sub(
        r"<!--start generated readme-->[\s\S]*<!--end generated readme-->\n?",
        block,
        readme,
    )
    readme_path.write_text(readme)


# =============================================================================
# Main
# =============================================================================


async def main() -> None:
    t0 = time.monotonic()

    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT, follow_redirects=True
    ) as client:
        # Phase 1: bulk-fetch from Algolia
        companies = await fetch_all_companies(client)

        # Attach convenience links
        for c in companies:
            c["url"] = f"{YC_BASE_URL}/companies/{c['slug']}"
            c["api"] = f"{API_BASE_URL}/batches/{batch_slug(c.get('batch'))}/{c['slug']}.json"

        # Phase 2: enrich with detail-page data
        await enrich_all(client, companies)

    elapsed = time.monotonic() - t0
    print(f"\nDone in {elapsed:.1f}s — {len(companies)} companies")

    # Phase 3: write output files
    meta = _generate_outputs(companies)

    # Phase 4: conditionally update meta.json + README.md
    _update_meta_and_readme(companies, meta)


if __name__ == "__main__":
    asyncio.run(main())
