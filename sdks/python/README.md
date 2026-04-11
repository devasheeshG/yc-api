# yc-api

Typed Python client for the unofficial [Y Combinator companies API](https://github.com/devasheeshG/yc-api).

## Install

```bash
pip install yc-api
```

## Quick start

```python
from yc_api import YCClient

client = YCClient()

# All companies
companies = client.get_all()

# Currently hiring
hiring = client.get_hiring()

# Single company
company = client.get_company("winter-2026", "airbnb")
print(company.name, company.one_liner)

# Founders with emails
for founder in company.founders:
    if founder.email:
        print(f"  {founder.full_name}: {founder.email}")

# Filter
ai_companies = client.search(tag="AI", hiring=True)
```

## Async

Every method has an async counterpart prefixed with `a`:

```python
import asyncio
from yc_api import YCClient

async def main():
    client = YCClient()
    companies = await client.aget_all()
    print(len(companies))

asyncio.run(main())
```

## Models

All responses are fully typed with [Pydantic](https://docs.pydantic.dev) models:

- `Company` — full company object with founders, jobs, news, launches
- `Founder` — name, bio, social links, SMTP-verified email
- `Job` — title, location, salary/equity range, visa status, skills
- `News` — press articles
- `Launch` — Launch YC posts
- `Partner` — assigned YC group partner
- `Meta` — API index with counts and endpoint URLs

### Enums

- `CompanyStatus` — `Active`, `Inactive`, `Acquired`, `Public`
- `CompanyStage` — `Early`, `Growth`
- `CompanyIndustry` — 9 primary industries (`B2B`, `Consumer`, `Fintech`, etc.)
- `CompanySubindustry` — 59 sub-industry categories (`B2B -> Infrastructure`, `Healthcare -> Diagnostics`, etc.)
- `JobType` — `Full-time`, `Internship`, `Contract`, `Co-founder`
- `JobRole` — 11 role categories (`Engineering`, `Design`, `Product`, etc.)
- `JobVisa` — `US citizen/visa only`, `US citizenship/visa not required`, `Will sponsor`
- `JobExperience` — `1+ years`, `3+ years`, `6+ years`, `11+ years`, `Any (new grads ok)`

## License

MIT
