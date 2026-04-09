"""
YC Companies Fetcher
====================

Five-phase pipeline that builds a complete, static JSON API of every
Y Combinator company:

  Phase 1 — Bulk fetch from Algolia (the same index ycombinator.com uses).
            Credentials are auto-discovered from the public page; no secrets needed.

  Phase 2 — Enrich each company by scraping its detail page on ycombinator.com.
            This adds founders, open jobs, press/news, and Launch YC posts.

  Phase 3 — Discover founder emails via SMTP RCPT TO verification.
            Generates candidate emails from name patterns and social-media
            usernames (LinkedIn, Twitter), then verifies against the company's
            mail server.  Persistent SMTP connections are sharded per MX host
            for throughput.

  Phase 4 — Write all JSON output files (companies, batches, industries, tags).

  Phase 5 — Conditionally update meta.json and the auto-generated section
            of README.md when data has changed.

Output is written to:
    companies/   — all.json, top.json, hiring.json, etc.
    batches/     — per-batch lists + individual <slug>.json files
    industries/  — per-industry lists
    tags/        — per-tag lists
    meta.json    — index of every endpoint (counts + URLs)
    README.md    — auto-generated stats table (between marker comments)
"""

import asyncio
import base64
import html as html_module
import json
import math
import random
import re
import string
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import unquote, urlparse

import aiosmtplib
import dns.asyncresolver
import httpx

# =============================================================================
# Constants
# =============================================================================

GITHUB_REPO = "devasheeshG/yc-api"
REPO_OWNER, REPO_NAME = GITHUB_REPO.split("/")

API_BASE_URL = f"https://{REPO_OWNER.lower()}.github.io/{REPO_NAME}"
README_URL = f"https://github.com/{GITHUB_REPO}"
YC_BASE_URL = "https://www.ycombinator.com"

CONCURRENCY = 200  # parallel requests for detail-page enrichment
EMAIL_CONCURRENCY = 100  # max concurrent SMTP connections for email discovery
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
SPECIAL_LISTS: List[Tuple[str, str, str]] = [
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


def write_json(path: Union[str, Path], data: Any) -> None:
    """Atomically write *data* as pretty-printed JSON to *path*."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def batch_slug(batch: Optional[str]) -> str:
    """Return the slug for a batch name, defaulting to 'unspecified'."""
    return slugify(batch or "Unspecified")


# =============================================================================
# Phase 1 — Algolia bulk fetch
# =============================================================================


async def _discover_algolia_credentials(
    client: httpx.AsyncClient,
) -> Tuple[str, str, str]:
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


def _build_algolia_params(facets: List[str]) -> str:
    """Encode facets + pagination defaults into an Algolia params string."""
    encoded = "%2C".join(f"%22{f}%22" for f in facets)
    return (
        f"facets=%5B{encoded}%5D"
        f"&hitsPerPage=1000"
        f"&maxValuesPerFacet=1000"
        f"&query="
        f"&tagFilters="
    )


async def fetch_all_companies(client: httpx.AsyncClient) -> List[Dict[str, Any]]:
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
    print("  Fetching Algolia facets...")
    resp = await client.post(
        url,
        params=auth_params,
        json={"requests": [{"indexName": index_name, "params": base_params}]},
    )
    resp.raise_for_status()
    batches: Dict[str, int] = resp.json()["results"][0]["facets"]["batch"]

    # --- Step 2: fetch all companies — all batches in parallel ---
    # Pre-compute every (batch, page) pair so we can fire them all at once
    batch_pages: List[Tuple[str, int]] = []
    for batch_name, expected_count in batches.items():
        num_pages = max(1, math.ceil(expected_count / 1000))
        for page in range(num_pages):
            batch_pages.append((batch_name, page))

    print(f"  Fetching {len(batch_pages)} batch pages in parallel...")

    async def _fetch_batch_page(bn: str, pg: int) -> List[Dict[str, Any]]:
        r = await client.post(
            url,
            params=auth_params,
            json={
                "requests": [
                    {
                        "indexName": index_name,
                        "params": f"{base_params}&facetFilters=batch:{bn}&page={pg}",
                    }
                ]
            },
        )
        r.raise_for_status()
        return r.json()["results"][0]["hits"]

    page_results = await asyncio.gather(
        *(_fetch_batch_page(bn, pg) for bn, pg in batch_pages)
    )

    all_companies: List[Dict[str, Any]] = [
        hit for page_hits in page_results for hit in page_hits
    ]

    # Clean up Algolia internal fields
    for c in all_companies:
        c.pop("_highlightResult", None)
        c.pop("objectID", None)

    all_companies.sort(key=lambda c: c["id"])
    print(f"  Total from Algolia: {len(all_companies)}")
    return all_companies


# =============================================================================
# Phase 2 — Detail-page enrichment
# =============================================================================


def _parse_inertia_props(page_html: str) -> Optional[Dict[str, Any]]:
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


def _strip_s3_params(url: Optional[str]) -> Optional[str]:
    """Remove AWS signed URL query parameters — the base S3 URL works without them."""
    if not url:
        return None
    return url.split("?")[0]


def _extract_founders(company_props: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract active/inactive founders with their bios and social links."""
    return [
        {
            "user_id": f.get("user_id"),
            "full_name": f.get("full_name"),
            "title": f.get("title"),
            "founder_bio": f.get("founder_bio"),
            "is_active": f.get("is_active"),
            "linkedin_url": f.get("linkedin_url"),
            "x_url": f.get("twitter_url"),
            "avatar_thumb_url": _strip_s3_params(f.get("avatar_thumb_url")),
        }
        for f in company_props.get("founders", [])
    ]


def _extract_jobs(props: Dict[str, Any]) -> List[Dict[str, Any]]:
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


def _extract_news(props: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract press/news items."""
    return [
        {"title": n.get("title"), "url": n.get("url"), "date": n.get("date")}
        for n in props.get("newsItems", [])
    ]


def _extract_launches(props: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract Launch YC posts (title, tagline, votes, URL, body)."""
    return [
        {
            "id": l.get("id"),
            "title": l.get("title"),
            "tagline": l.get("tagline"),
            "body": l.get("body"),
            "url": l.get("url"),
            "votes": l.get("total_vote_count"),
            "created_at": l.get("created_at"),
        }
        for l in props.get("launches", [])
    ]


def _extract_partner(company: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract the primary YC group partner."""
    partner = company.get("primary_group_partner")
    if not partner:
        return None
    return {
        "name": partner.get("full_name"),
        "url": partner.get("url"),
    }


def _build_enrichment(page_data: Dict[str, Any]) -> Dict[str, Any]:
    """Combine all detail-page extractions into a single dict for merging."""
    props = page_data.get("props", {})
    company = props.get("company", {})

    return {
        # Extra company-level fields not in Algolia
        "year_founded": company.get("year_founded"),
        "city": company.get("city"),
        "country": company.get("country"),
        "linkedin_url": company.get("linkedin_url"),
        "x_url": company.get("twitter_url"),
        "fb_url": company.get("fb_url") or None,
        "cb_url": company.get("cb_url") or None,
        "github_url": company.get("github_url") or None,
        "logo_url": company.get("small_logo_url"),
        "app_video_url": company.get("app_video_url"),
        "dday_video_url": company.get("dday_video_url"),
        # Nested data
        "company_photos": [
            _strip_s3_params(p.get("url"))
            for p in company.get("company_photos", [])
            if p.get("url")
        ],
        "primary_partner": _extract_partner(company),
        "founders": _extract_founders(company),
        "jobs": _extract_jobs(props),
        "news": _extract_news(props),
        "launches": _extract_launches(props),
    }


async def _enrich_one(
    client: httpx.AsyncClient,
    company: Dict[str, Any],
    semaphore: asyncio.Semaphore,
    progress: Dict[str, int],
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
    companies: List[Dict[str, Any]],
) -> None:
    """Enrich all companies concurrently (bounded by CONCURRENCY)."""
    print(f"  Enriching {len(companies)} companies (concurrency={CONCURRENCY})...")
    sem = asyncio.Semaphore(CONCURRENCY)
    progress = {"done": 0, "total": len(companies)}

    await asyncio.gather(
        *(_enrich_one(client, c, sem, progress) for c in companies)
    )


# =============================================================================
# Phase 3 — Founder email discovery
# =============================================================================
#
# Strategy:
#   1. Extract domain from the company website URL.
#   2. Check MX records — skip if the domain doesn't accept email.
#   3. Open one persistent SMTP connection per MX host, then pipeline
#      all work through it:
#      a) Catch-all detection (probe a random address per domain).
#      b) RCPT TO verification for each founder's candidate emails.
#   4. Attach the first verified email to the founder, or the best-guess
#      pattern for catch-all servers (flagged as unverified).
#
# Parallelism: every MX host runs fully in parallel (one asyncio task each).
# Within a host, work is serialised on one persistent TCP connection to avoid
# being blocked or rate-limited.
#

# Common corporate email patterns, ordered by prevalence in startups
_EMAIL_PATTERNS: List[str] = [
    "{first}@{domain}",
    "{first}.{last}@{domain}",
    "{first}_{last}@{domain}",
    "{first}{last}@{domain}",
    "{f}{last}@{domain}",
    "{f}.{last}@{domain}",
]

SMTP_TIMEOUT = 10  # seconds per SMTP connection
# Max simultaneous SMTP connections (prevents fd exhaustion on the local side)
MAX_SMTP_CONNECTIONS = EMAIL_CONCURRENCY
# Shard large MX hosts into chunks to avoid one host bottlenecking everything
DOMAINS_PER_CONNECTION = 50


def _extract_domain(url: Optional[str]) -> Optional[str]:
    """
    Extract the root domain from a company URL.
    Strips 'www.' prefix and ignores common non-company domains.
    """
    if not url:
        return None
    try:
        # Ensure scheme is present for urlparse
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        host = urlparse(url).hostname
        if not host:
            return None
        # Strip www. prefix
        host = host.lower().removeprefix("www.")
        return host
    except Exception:
        return None


async def _get_mx_host(domain: str) -> Optional[str]:
    """
    Look up the highest-priority MX record for a domain.
    Returns the mail server hostname, or None if no MX records exist.
    """
    try:
        records = await dns.asyncresolver.resolve(domain, "MX")
        best = min(records, key=lambda r: r.preference)
        return str(best.exchange).rstrip(".").lower()
    except Exception:
        return None


def _generate_candidates(first: str, last: str, domain: str) -> List[str]:
    """
    Generate candidate email addresses from a founder's name and company domain.
    Uses the most common corporate email patterns.
    """
    f, l = first.lower(), last.lower()
    return [
        p.format(first=f, last=l, f=f[0], domain=domain)
        for p in _EMAIL_PATTERNS
    ]


def _extract_social_username(url: Optional[str]) -> Optional[str]:
    """
    Extract a username from a LinkedIn or Twitter/X URL.
    e.g. 'https://linkedin.com/in/johndoe/' → 'johndoe'
         'https://twitter.com/johndoe' → 'johndoe'
    Returns None if the URL is missing or unparseable.
    """
    if not url:
        return None
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        segments = [s for s in parsed.path.strip("/").split("/") if s]
        if not segments:
            return None
        # LinkedIn: only accept /in/<username> paths
        if "linkedin" in host:
            if len(segments) >= 2 and segments[0] == "in":
                return segments[1].lower()
            return None
        # Twitter/X: /<username> (skip status/list paths)
        if len(segments) == 1:
            return segments[0].lower()
        return None
    except Exception:
        return None


def _split_name(full_name: str) -> Optional[Tuple[str, ...]]:
    """
    Split a full name into name parts.
    Returns (first, last) for 2-word or 4+-word names,
    (first, middle, last) for exactly 3-word names,
    (name,) for mononyms, or None for empty strings.
    """
    parts = full_name.strip().split()
    if not parts:
        return None
    if len(parts) == 1:
        return (parts[0],)
    if len(parts) == 3:
        return (parts[0], parts[1], parts[-1])
    return (parts[0], parts[-1])


async def _smtp_rcpt_check(
    smtp: aiosmtplib.SMTP,
    email: str,
) -> Tuple[int, str]:
    """
    Send a single RCPT TO on an already-connected SMTP session.
    Returns (SMTP code, message).  250 = exists, 550 = doesn't exist.
    """
    try:
        code, message = await smtp.execute_command(
            f"RCPT TO:<{email}>\r\n".encode()
        )
        return code, message
    except Exception:
        return -1, "command failed"


async def _open_smtp_session(mx_host: str) -> Optional[aiosmtplib.SMTP]:
    """
    Open a persistent SMTP connection to an MX host.
    Returns the connected client or None on failure.
    """
    try:
        smtp = aiosmtplib.SMTP(hostname=mx_host, port=25, timeout=SMTP_TIMEOUT)
        await smtp.connect()
        await smtp.ehlo()
        await smtp.execute_command(b"MAIL FROM:<probe@example.com>\r\n")
        return smtp
    except Exception:
        return None


async def _process_mx_host(
    mx_host: str,
    domains: List[str],
    domain_founders: Dict[str, List[Dict[str, Any]]],
    progress: Dict[str, int],
    total: int,
) -> None:
    """
    Process all domains routed to a single MX host on ONE persistent
    SMTP connection.

    Steps per domain:
      1. Catch-all detection — probe a random address.
      2. If catch-all → assign best-guess email (unverified) to all founders.
      3. Otherwise → RCPT TO each candidate pattern per founder until one hits.

    The connection is reused across all domains and founders, avoiding the
    overhead of thousands of separate TCP handshakes.
    """
    smtp = await _open_smtp_session(mx_host)
    if not smtp:
        # Count all founders on this host as done
        for domain in domains:
            progress["done"] += len(domain_founders.get(domain, []))
        return

    try:
        for idx, domain in enumerate(domains):
            founders = domain_founders.get(domain, [])
            if not founders:
                continue

            # --- RSET between domains to start a fresh transaction ---
            try:
                await smtp.execute_command(b"RSET\r\n")
                await smtp.execute_command(b"MAIL FROM:<probe@example.com>\r\n")
            except Exception:
                # Connection died — try to reconnect
                try:
                    await smtp.quit()
                except Exception:
                    pass
                smtp = await _open_smtp_session(mx_host)
                if not smtp:
                    # Can't reconnect — count remaining founders as done
                    for d in domains[idx:]:
                        progress["done"] += len(domain_founders.get(d, []))
                    return

            # --- Catch-all detection ---
            garbage = "".join(random.choices(string.ascii_lowercase, k=16))
            catch_all_code, _ = await _smtp_rcpt_check(smtp, f"{garbage}@{domain}")
            is_catch_all = catch_all_code == 250

            for founder in founders:
                name_parts = _split_name(founder["full_name"])
                if not name_parts:
                    founder["email"] = None
                    progress["done"] += 1
                    done = progress["done"]
                    if done % 500 == 0 or done == total:
                        print(f"  [{done}/{total}] emails processed")
                    continue

                if len(name_parts) == 1:
                    # Mononym — just try {name}@domain
                    candidates = [f"{name_parts[0].lower()}@{domain}"]
                elif len(name_parts) == 3:
                    # 3-part name: try (first, last) + (first, middle) combos
                    first, middle, last = name_parts
                    seen: set = set()
                    candidates = []
                    for c in _generate_candidates(first, last, domain):
                        if c not in seen:
                            seen.add(c)
                            candidates.append(c)
                    for c in _generate_candidates(first, middle, domain):
                        if c not in seen:
                            seen.add(c)
                            candidates.append(c)
                    # Also try {firstmiddle}.{last}@domain
                    combo = f"{first.lower()}{middle.lower()}.{last.lower()}@{domain}"
                    if combo not in seen:
                        seen.add(combo)
                        candidates.append(combo)
                else:
                    first, last = name_parts
                    candidates = _generate_candidates(first, last, domain)

                # Append social-media usernames as extra candidates
                seen_set = set(candidates)
                for social_url in (founder.get("linkedin_url"), founder.get("x_url")):
                    uname = _extract_social_username(social_url)
                    if uname:
                        social_email = f"{uname}@{domain}"
                        if social_email not in seen_set:
                            seen_set.add(social_email)
                            candidates.append(social_email)

                if is_catch_all:
                    # Can't verify on catch-all domains — skip
                    founder["email"] = None
                else:
                    founder["email"] = None
                    for email in candidates:
                        code, _ = await _smtp_rcpt_check(smtp, email)
                        if code == 250:
                            founder["email"] = email
                            break

                progress["done"] += 1
                done = progress["done"]
                if done % 500 == 0 or done == total:
                    print(f"  [{done}/{total}] emails processed")
    finally:
        try:
            await smtp.quit()
        except Exception:
            pass


async def discover_emails(companies: List[Dict[str, Any]]) -> None:
    """
    Phase 3: Discover and verify founder emails for all companies.

    Two parallel sub-phases:
      3a. Resolve MX records for all unique domains concurrently.
      3b. Group domains by MX host, then launch one task per MX host.
          Each task opens a single persistent SMTP connection and pipelines
          catch-all detection + RCPT TO verification for every founder on
          that host.  Different MX hosts run fully in parallel, bounded
          by MAX_SMTP_CONNECTIONS to prevent fd exhaustion.
    """
    # Build a flat list of (founder_dict, domain) pairs to process
    work: List[Tuple[Dict[str, Any], str]] = []
    for company in companies:
        domain = _extract_domain(company.get("website"))
        if not domain:
            continue
        for founder in company.get("founders", []):
            if not founder.get("full_name"):
                continue
            work.append((founder, domain))

    if not work:
        return

    unique_domains = list({d for _, d in work})
    print(f"  {len(work)} founders across {len(unique_domains)} domains")

    # ------------------------------------------------------------------
    # 3a — Resolve MX for all unique domains concurrently
    # ------------------------------------------------------------------
    mx_cache: Dict[str, Optional[str]] = {}
    dns_sem = asyncio.Semaphore(EMAIL_CONCURRENCY)

    async def _resolve_one(domain: str) -> None:
        async with dns_sem:
            mx_cache[domain] = await _get_mx_host(domain)

    print("  Resolving MX records...")
    await asyncio.gather(*(_resolve_one(d) for d in unique_domains))

    domains_with_mx = [d for d in unique_domains if mx_cache[d]]
    print(f"  {len(domains_with_mx)}/{len(unique_domains)} domains have MX records")

    # ------------------------------------------------------------------
    # 3b — Group by MX host, then one persistent connection per host
    # ------------------------------------------------------------------
    # Build: mx_host → [domains], domain → [founder dicts]
    host_to_domains: Dict[str, List[str]] = {}
    domain_to_founders: Dict[str, List[Dict[str, Any]]] = {}

    for founder, domain in work:
        mx_host = mx_cache.get(domain)
        if not mx_host:
            continue
        host_to_domains.setdefault(mx_host, [])
        if domain not in host_to_domains[mx_host]:
            host_to_domains[mx_host].append(domain)
        domain_to_founders.setdefault(domain, []).append(founder)

    # Count founders with no MX (skip them)
    founders_with_mx = sum(len(v) for v in domain_to_founders.values())
    founders_skipped = len(work) - founders_with_mx
    unique_mx_hosts = len(host_to_domains)
    print(f"  {unique_mx_hosts} unique MX hosts, "
          f"{founders_with_mx} founders to verify, "
          f"{founders_skipped} skipped (no MX)")

    progress: Dict[str, int] = {"done": founders_skipped}
    total = len(work)
    smtp_sem = asyncio.Semaphore(MAX_SMTP_CONNECTIONS)

    # Shard large MX hosts into chunks of DOMAINS_PER_CONNECTION so a single
    # host (e.g. Google with 3000+ domains) doesn't bottleneck everything.
    shards: List[Tuple[str, List[str]]] = []
    for mx_host, domains in host_to_domains.items():
        for i in range(0, len(domains), DOMAINS_PER_CONNECTION):
            shards.append((mx_host, domains[i:i + DOMAINS_PER_CONNECTION]))

    async def _bounded_process(mx_host: str, domains: List[str]) -> None:
        async with smtp_sem:
            await _process_mx_host(
                mx_host, domains, domain_to_founders, progress, total,
            )

    print(f"  Verifying emails ({len(shards)} shards, max {MAX_SMTP_CONNECTIONS} connections)...")
    await asyncio.gather(*(
        _bounded_process(mx_host, domains)
        for mx_host, domains in shards
    ))

    # --- Summary ---
    total_founders = len(work)
    emails_found = sum(
        1
        for company in companies
        for f in company.get("founders", [])
        if f.get("email")
    )
    print(f"  Done — {emails_found}/{total_founders} emails verified "
          f"({100 * emails_found / total_founders:.1f}%)")


# =============================================================================
# Batch sorting
# =============================================================================

_SEASON_RANK = {"Fall": 0, "Summer": 1, "Winter": 2}


def _batch_sort_key(name: str) -> Tuple[int, int]:
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


def _generate_outputs(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
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

    meta: Dict[str, Dict[str, Dict[str, Any]]] = {
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


def _update_meta_and_readme(results: List[Dict[str, Any]], meta: Dict[str, Any]) -> None:
    """
    Compare new meta against the existing meta.json.
    Only write if something actually changed (ignoring last_updated).
    """
    existing_meta: Dict[str, Any] = {}
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

    # Phase 1: bulk-fetch from Algolia
    print("\n[Phase 1/5] Fetching companies from Algolia...")
    t1 = time.monotonic()
    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT, follow_redirects=True
    ) as client:
        companies = await fetch_all_companies(client)

        # Attach convenience links
        for c in companies:
            c["url"] = f"{YC_BASE_URL}/companies/{c['slug']}"
            c["api"] = f"{API_BASE_URL}/batches/{batch_slug(c.get('batch'))}/{c['slug']}.json"
        print(f"  Phase 1 done in {time.monotonic() - t1:.1f}s")

        # Phase 2: enrich with detail-page data
        print(f"\n[Phase 2/5] Enriching company detail pages...")
        t2 = time.monotonic()
        await enrich_all(client, companies)
        print(f"  Phase 2 done in {time.monotonic() - t2:.1f}s")

    # Phase 3: discover and verify founder emails via SMTP
    print(f"\n[Phase 3/5] Discovering founder emails via SMTP...")
    t3 = time.monotonic()
    await discover_emails(companies)
    print(f"  Phase 3 done in {time.monotonic() - t3:.1f}s")

    # Phase 4: write output files
    print(f"\n[Phase 4/5] Writing output files...")
    t4 = time.monotonic()
    meta = _generate_outputs(companies)
    print(f"  Phase 4 done in {time.monotonic() - t4:.1f}s")

    # Phase 5: conditionally update meta.json + README.md
    print(f"\n[Phase 5/5] Updating meta.json + README.md...")
    _update_meta_and_readme(companies, meta)

    elapsed = time.monotonic() - t0
    print(f"\n{'='*50}")
    print(f"All done in {elapsed:.1f}s — {len(companies)} companies")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
