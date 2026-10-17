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

#### `CompanyStatus`

- `ACTIVE`
- `INACTIVE`
- `ACQUIRED`
- `PUBLIC`

#### `CompanyStage`

- `EARLY`
- `GROWTH`

#### `CompanyIndustry`

- `B2B`
- `CONSUMER`
- `EDUCATION`
- `FINTECH`
- `GOVERNMENT`
- `HEALTHCARE`
- `INDUSTRIALS`
- `REAL_ESTATE_AND_CONSTRUCTION`
- `UNSPECIFIED`

#### `CompanySubindustry`

- `B2B`
- `B2B_ANALYTICS`
- `B2B_ENGINEERING_PRODUCT_AND_DESIGN`
- `B2B_FINANCE_AND_ACCOUNTING`
- `B2B_HUMAN_RESOURCES`
- `B2B_INFRASTRUCTURE`
- `B2B_LEGAL`
- `B2B_MARKETING`
- `B2B_OFFICE_MANAGEMENT`
- `B2B_OPERATIONS`
- `B2B_PRODUCTIVITY`
- `B2B_RECRUITING_AND_TALENT`
- `B2B_RETAIL`
- `B2B_SALES`
- `B2B_SECURITY`
- `B2B_SUPPLY_CHAIN_AND_LOGISTICS`
- `CONSUMER`
- `CONSUMER_APPAREL_AND_COSMETICS`
- `CONSUMER_CONSUMER_ELECTRONICS`
- `CONSUMER_CONTENT`
- `CONSUMER_FOOD_AND_BEVERAGE`
- `CONSUMER_GAMING`
- `CONSUMER_HOME_AND_PERSONAL`
- `CONSUMER_JOB_AND_CAREER_SERVICES`
- `CONSUMER_SOCIAL`
- `CONSUMER_TRANSPORTATION_SERVICES`
- `CONSUMER_TRAVEL_LEISURE_AND_TOURISM`
- `CONSUMER_VIRTUAL_AND_AUGMENTED_REALITY`
- `EDUCATION`
- `FINTECH`
- `FINTECH_ASSET_MANAGEMENT`
- `FINTECH_BANKING_AND_EXCHANGE`
- `FINTECH_CONSUMER_FINANCE`
- `FINTECH_CREDIT_AND_LENDING`
- `FINTECH_INSURANCE`
- `FINTECH_PAYMENTS`
- `GOVERNMENT`
- `HEALTHCARE`
- `HEALTHCARE_CONSUMER_HEALTH_AND_WELLNESS`
- `HEALTHCARE_DIAGNOSTICS`
- `HEALTHCARE_DRUG_DISCOVERY_AND_DELIVERY`
- `HEALTHCARE_HEALTHCARE_IT`
- `HEALTHCARE_HEALTHCARE_SERVICES`
- `HEALTHCARE_INDUSTRIAL_BIO`
- `HEALTHCARE_MEDICAL_DEVICES`
- `HEALTHCARE_THERAPEUTICS`
- `INDUSTRIALS`
- `INDUSTRIALS_AGRICULTURE`
- `INDUSTRIALS_AUTOMOTIVE`
- `INDUSTRIALS_AVIATION_AND_SPACE`
- `INDUSTRIALS_CLIMATE`
- `INDUSTRIALS_DEFENSE`
- `INDUSTRIALS_DRONES`
- `INDUSTRIALS_ENERGY`
- `INDUSTRIALS_MANUFACTURING_AND_ROBOTICS`
- `REAL_ESTATE_AND_CONSTRUCTION`
- `REAL_ESTATE_AND_CONSTRUCTION_CONSTRUCTION`
- `REAL_ESTATE_AND_CONSTRUCTION_HOUSING_AND_REAL_ESTATE`
- `UNSPECIFIED`

#### `JobType`

- `FULL_TIME`
- `INTERNSHIP`
- `CONTRACT`
- `CO_FOUNDER`

#### `JobRole`

- `DESIGN`
- `ENGINEERING`
- `FINANCE`
- `LEGAL`
- `MARKETING`
- `OPERATIONS`
- `PRODUCT`
- `RECRUITING_HR`
- `SALES`
- `SCIENCE`
- `SUPPORT`

#### `JobVisa`

- `US_ONLY`
- `NOT_REQUIRED`
- `WILL_SPONSOR`

#### `JobExperience`

- `ONE_PLUS`
- `THREE_PLUS`
- `SIX_PLUS`
- `ELEVEN_PLUS`
- `ANY`

## License

MIT
