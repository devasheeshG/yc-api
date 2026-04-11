# @devasheeshg/yc-api

Typed TypeScript/JavaScript client for the unofficial [Y Combinator companies API](https://github.com/devasheeshG/yc-api).

## Install

```bash
npm install @devasheeshg/yc-api
```

## Quick start

```ts
import { YCClient } from '@devasheeshg/yc-api';

const client = new YCClient();

// All companies
const companies = await client.getAll();

// Currently hiring
const hiring = await client.getHiring();

// Single company
const company = await client.getCompany('winter-2026', 'airbnb');
console.log(company.name, company.one_liner);

// Founders with emails
for (const founder of company.founders) {
    if (founder.email) {
        console.log(`  ${founder.full_name}: ${founder.email}`);
    }
}

// Filter
const aiHiring = await client.search({ tag: 'AI', hiring: true });
```

## Types

All responses are fully typed with TypeScript interfaces:

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
- `JobType` — `FullTime`, `Internship`, `Contract`, `CoFounder`
- `JobRole` — 11 role categories (`Engineering`, `Design`, `Product`, etc.)
- `JobVisa` — `USOnly`, `NotRequired`, `WillSponsor`
- `JobExperience` — `OnePlus`, `ThreePlus`, `SixPlus`, `ElevenPlus`, `Any`

## License

MIT
