<div align="center">

<img src="logo.svg" alt="YC Logo" width="80" height="80">

# yc-api

**Query every YC startup in one line of code.**

A free, open JSON API over the entire Y Combinator Startup Directory — built for founders, indie hackers, and researchers.

[![GitHub stars](https://img.shields.io/github/stars/devasheeshG/yc-api?style=flat)](https://github.com/devasheeshG/yc-api/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Updated daily](https://img.shields.io/badge/updated-daily-FF6600)](https://devasheeshg.github.io/yc-api/meta.json)
[![Python SDK](https://img.shields.io/pypi/v/yc-api?label=pip&color=blue)](https://pypi.org/project/yc-api/)
[![npm](https://img.shields.io/npm/v/yc-api?label=npm&color=blue)](https://www.npmjs.com/package/yc-api)

[Quickstart](#-quickstart) · [Recipes](#-recipes) · [SDKs](#-sdks) · [Schema](#-schema) · [Contributing](#-contributing)

</div>

---

## Why this exists

YC data is scattered — a clunky directory, huge JSON dumps, random scrapers. If you want to answer "which AI startups from the last 3 batches are hiring?" you're stuck writing a scraper from scratch every time.

**yc-api** fixes that. It's a clean, static JSON API served from GitHub Pages — no auth, no rate limits, no API keys. Auto-updated daily. Every company includes founders (with SMTP-verified emails), open jobs, press, Launch YC posts, social links, and 50+ fields of metadata scraped directly from ycombinator.com.

**5,800+ companies · 48 batches · 59 industries · 331 tags · Updated daily**

## ⚡ Quickstart

### curl

```bash
# Get all YC companies currently hiring
curl -s https://devasheeshg.github.io/yc-api/companies/hiring.json | python3 -m json.tool | head -50
```

### Python

```bash
pip install yc-api
```

```python
from yc_api import YCClient

client = YCClient()

# All AI companies that are hiring
for company in client.search(tag="AI", hiring=True):
    print(f"{company.name} ({company.batch}) — {company.one_liner}")
```

### TypeScript / JavaScript

```bash
npm install yc-api
```

```ts
import { YCClient } from "yc-api";

const client = new YCClient();
const hiring = await client.search({ tag: "AI", hiring: true });
hiring.forEach((c) => console.log(`${c.name} (${c.batch}) — ${c.one_liner}`));
```

### Raw JSON (no SDK needed)

Every endpoint is a static `.json` file — just fetch it:

```
https://devasheeshg.github.io/yc-api/companies/all.json     # every company
https://devasheeshg.github.io/yc-api/companies/hiring.json  # currently hiring
https://devasheeshg.github.io/yc-api/companies/top.json     # top companies
https://devasheeshg.github.io/yc-api/batches/winter-2026.json  # filter by batch
https://devasheeshg.github.io/yc-api/tags/ai.json           # filter by tag
https://devasheeshg.github.io/yc-api/industries/fintech.json # filter by industry
```

## 🧑‍🍳 Recipes

### Find AI startups from the last 3 batches that are hiring

```python
from yc_api import YCClient

client = YCClient()
recent_ai = [
    c for c in client.search(tag="AI", hiring=True)
    if c.batch in ("Winter 2026", "Spring 2026", "Fall 2025")
]
print(f"{len(recent_ai)} AI startups hiring from last 3 batches")
for c in recent_ai[:10]:
    print(f"  {c.name} — {c.one_liner}")
```

### Build a lead list with founder emails

```python
from yc_api import YCClient

client = YCClient()
for company in client.search(tag="Developer Tools", hiring=True):
    for founder in company.founders:
        if founder.email:
            print(f"{founder.full_name},{founder.email},{company.name},{company.website}")
```

### Get all open engineering jobs with visa sponsorship

```python
from yc_api import YCClient

client = YCClient()
for company in client.get_hiring():
    for job in company.jobs:
        if job.role == "Engineering" and "sponsor" in (job.visa or "").lower():
            salary = job.salary_range or "Not listed"
            print(f"{company.name} — {job.title} ({salary})")
```

### Map YC's top companies by industry

```python
from collections import Counter
from yc_api import YCClient

client = YCClient()
industries = Counter(c.industry for c in client.get_top())
for industry, count in industries.most_common(10):
    print(f"  {industry}: {count}")
```

### Find startups with Launch YC posts sorted by upvotes

```python
from yc_api import YCClient

client = YCClient()
launched = []
for company in client.get_all():
    for launch in company.launches:
        launched.append((launch.votes, company.name, launch.title, launch.url))

for votes, name, title, url in sorted(launched, reverse=True)[:20]:
    print(f"  🔼 {votes:>4}  {name} — {title}")
```

## 💡 Use cases

| Use case | What you'd build |
| --- | --- |
| **Prospecting & cold outreach** | Generate lead lists with founder emails, filter by industry/batch/hiring status |
| **Market mapping** | Cluster companies by tag, industry, or region to spot trends |
| **YC dashboards** | Build internal tools showing batch breakdowns, hiring trends, top companies |
| **Job hunting** | Find open roles at YC companies that sponsor visas and match your skills |
| **Research** | Analyze YC batch sizes, industry trends, founder demographics over time |

## 📦 SDKs

| Language | Package | Install |
| --- | --- | --- |
| Python | [`yc-api`](https://pypi.org/project/yc-api/) | `pip install yc-api` |
| TypeScript/JS | [`yc-api`](https://www.npmjs.com/package/yc-api) | `npm install yc-api` |

Both SDKs are fully typed, support async, and wrap every endpoint. See [Python SDK docs](sdks/python/) or [Node SDK docs](sdks/node/) for details.

---

<!--start generated readme-->

## ℹ️ Metadata

API endpoint: https://devasheeshg.github.io/yc-api/meta.json

- Last updated: April 09, 2026 at 01:18 PM UTC
- Companies: 5833
- Batches: 48
- Industries: 59
- Tags: 331

## 💻 APIs

### 🏢 Companies

| List of companies | API endpoint |
| --------------- | ------------ |
| All launched companies | https://devasheeshg.github.io/yc-api/companies/all.json |
| Top companies | https://devasheeshg.github.io/yc-api/companies/top.json |
| Not-for-profit companies | https://devasheeshg.github.io/yc-api/companies/nonprofit.json |
| Companies currently hiring | https://devasheeshg.github.io/yc-api/companies/hiring.json |

### 🎓 Batches

<details>
<summary>Companies per batch</summary>

| Batch | Count | API endpoint |
| ---- | ---- | ------------ |
| Summer 2026 | 1 | https://devasheeshg.github.io/yc-api/batches/summer-2026.json |
| Winter 2026 | 199 | https://devasheeshg.github.io/yc-api/batches/winter-2026.json |
| Spring 2026 | 83 | https://devasheeshg.github.io/yc-api/batches/spring-2026.json |
| Fall 2025 | 148 | https://devasheeshg.github.io/yc-api/batches/fall-2025.json |
| Summer 2025 | 166 | https://devasheeshg.github.io/yc-api/batches/summer-2025.json |
| Winter 2025 | 168 | https://devasheeshg.github.io/yc-api/batches/winter-2025.json |
| Spring 2025 | 144 | https://devasheeshg.github.io/yc-api/batches/spring-2025.json |
| Fall 2024 | 93 | https://devasheeshg.github.io/yc-api/batches/fall-2024.json |
| Summer 2024 | 248 | https://devasheeshg.github.io/yc-api/batches/summer-2024.json |
| Winter 2024 | 250 | https://devasheeshg.github.io/yc-api/batches/winter-2024.json |
| Summer 2023 | 220 | https://devasheeshg.github.io/yc-api/batches/summer-2023.json |
| Winter 2023 | 275 | https://devasheeshg.github.io/yc-api/batches/winter-2023.json |
| Summer 2022 | 234 | https://devasheeshg.github.io/yc-api/batches/summer-2022.json |
| Winter 2022 | 399 | https://devasheeshg.github.io/yc-api/batches/winter-2022.json |
| Summer 2021 | 391 | https://devasheeshg.github.io/yc-api/batches/summer-2021.json |
| Winter 2021 | 336 | https://devasheeshg.github.io/yc-api/batches/winter-2021.json |
| Summer 2020 | 208 | https://devasheeshg.github.io/yc-api/batches/summer-2020.json |
| Winter 2020 | 229 | https://devasheeshg.github.io/yc-api/batches/winter-2020.json |
| Summer 2019 | 176 | https://devasheeshg.github.io/yc-api/batches/summer-2019.json |
| Winter 2019 | 195 | https://devasheeshg.github.io/yc-api/batches/winter-2019.json |
| Summer 2018 | 131 | https://devasheeshg.github.io/yc-api/batches/summer-2018.json |
| Winter 2018 | 146 | https://devasheeshg.github.io/yc-api/batches/winter-2018.json |
| Summer 2017 | 125 | https://devasheeshg.github.io/yc-api/batches/summer-2017.json |
| Winter 2017 | 116 | https://devasheeshg.github.io/yc-api/batches/winter-2017.json |
| Summer 2016 | 102 | https://devasheeshg.github.io/yc-api/batches/summer-2016.json |
| Winter 2016 | 122 | https://devasheeshg.github.io/yc-api/batches/winter-2016.json |
| Summer 2015 | 105 | https://devasheeshg.github.io/yc-api/batches/summer-2015.json |
| Winter 2015 | 111 | https://devasheeshg.github.io/yc-api/batches/winter-2015.json |
| Summer 2014 | 78 | https://devasheeshg.github.io/yc-api/batches/summer-2014.json |
| Winter 2014 | 74 | https://devasheeshg.github.io/yc-api/batches/winter-2014.json |
| Summer 2013 | 52 | https://devasheeshg.github.io/yc-api/batches/summer-2013.json |
| Winter 2013 | 46 | https://devasheeshg.github.io/yc-api/batches/winter-2013.json |
| Summer 2012 | 83 | https://devasheeshg.github.io/yc-api/batches/summer-2012.json |
| Winter 2012 | 66 | https://devasheeshg.github.io/yc-api/batches/winter-2012.json |
| Summer 2011 | 60 | https://devasheeshg.github.io/yc-api/batches/summer-2011.json |
| Winter 2011 | 45 | https://devasheeshg.github.io/yc-api/batches/winter-2011.json |
| Summer 2010 | 36 | https://devasheeshg.github.io/yc-api/batches/summer-2010.json |
| Winter 2010 | 27 | https://devasheeshg.github.io/yc-api/batches/winter-2010.json |
| Summer 2009 | 26 | https://devasheeshg.github.io/yc-api/batches/summer-2009.json |
| Winter 2009 | 16 | https://devasheeshg.github.io/yc-api/batches/winter-2009.json |
| Summer 2008 | 22 | https://devasheeshg.github.io/yc-api/batches/summer-2008.json |
| Winter 2008 | 21 | https://devasheeshg.github.io/yc-api/batches/winter-2008.json |
| Summer 2007 | 19 | https://devasheeshg.github.io/yc-api/batches/summer-2007.json |
| Winter 2007 | 13 | https://devasheeshg.github.io/yc-api/batches/winter-2007.json |
| Summer 2006 | 11 | https://devasheeshg.github.io/yc-api/batches/summer-2006.json |
| Winter 2006 | 7 | https://devasheeshg.github.io/yc-api/batches/winter-2006.json |
| Summer 2005 | 9 | https://devasheeshg.github.io/yc-api/batches/summer-2005.json |
| Unspecified | 1 | https://devasheeshg.github.io/yc-api/batches/unspecified.json |
</details>

### 🏭 Industries

<details>
<summary>Companies per industry</summary>

| Industry | Count | API endpoint |
| -------- | ---- | ------------ |
| Agriculture | 30 | https://devasheeshg.github.io/yc-api/industries/agriculture.json |
| Analytics | 123 | https://devasheeshg.github.io/yc-api/industries/analytics.json |
| Apparel and Cosmetics | 50 | https://devasheeshg.github.io/yc-api/industries/apparel-and-cosmetics.json |
| Asset Management | 53 | https://devasheeshg.github.io/yc-api/industries/asset-management.json |
| Automotive | 21 | https://devasheeshg.github.io/yc-api/industries/automotive.json |
| Aviation and Space | 60 | https://devasheeshg.github.io/yc-api/industries/aviation-and-space.json |
| B2B | 2972 | https://devasheeshg.github.io/yc-api/industries/b2b.json |
| Banking and Exchange | 69 | https://devasheeshg.github.io/yc-api/industries/banking-and-exchange.json |
| Climate | 52 | https://devasheeshg.github.io/yc-api/industries/climate.json |
| Construction | 47 | https://devasheeshg.github.io/yc-api/industries/construction.json |
| Consumer | 868 | https://devasheeshg.github.io/yc-api/industries/consumer.json |
| Consumer Electronics | 43 | https://devasheeshg.github.io/yc-api/industries/consumer-electronics.json |
| Consumer Finance | 86 | https://devasheeshg.github.io/yc-api/industries/consumer-finance.json |
| Consumer Health and Wellness | 114 | https://devasheeshg.github.io/yc-api/industries/consumer-health-and-wellness.json |
| Content | 113 | https://devasheeshg.github.io/yc-api/industries/content.json |
| Credit and Lending | 74 | https://devasheeshg.github.io/yc-api/industries/credit-and-lending.json |
| Defense | 12 | https://devasheeshg.github.io/yc-api/industries/defense.json |
| Diagnostics | 55 | https://devasheeshg.github.io/yc-api/industries/diagnostics.json |
| Drones | 20 | https://devasheeshg.github.io/yc-api/industries/drones.json |
| Drug Discovery and Delivery | 55 | https://devasheeshg.github.io/yc-api/industries/drug-discovery-and-delivery.json |
| Education | 125 | https://devasheeshg.github.io/yc-api/industries/education.json |
| Energy | 46 | https://devasheeshg.github.io/yc-api/industries/energy.json |
| Engineering, Product and Design | 594 | https://devasheeshg.github.io/yc-api/industries/engineering-product-and-design.json |
| Finance and Accounting | 129 | https://devasheeshg.github.io/yc-api/industries/finance-and-accounting.json |
| Fintech | 622 | https://devasheeshg.github.io/yc-api/industries/fintech.json |
| Food and Beverage | 94 | https://devasheeshg.github.io/yc-api/industries/food-and-beverage.json |
| Gaming | 70 | https://devasheeshg.github.io/yc-api/industries/gaming.json |
| Government | 40 | https://devasheeshg.github.io/yc-api/industries/government.json |
| Healthcare | 666 | https://devasheeshg.github.io/yc-api/industries/healthcare.json |
| Healthcare IT | 140 | https://devasheeshg.github.io/yc-api/industries/healthcare-it.json |
| Healthcare Services | 69 | https://devasheeshg.github.io/yc-api/industries/healthcare-services.json |
| Home and Personal | 125 | https://devasheeshg.github.io/yc-api/industries/home-and-personal.json |
| Housing and Real Estate | 82 | https://devasheeshg.github.io/yc-api/industries/housing-and-real-estate.json |
| Human Resources | 85 | https://devasheeshg.github.io/yc-api/industries/human-resources.json |
| Industrial Bio | 32 | https://devasheeshg.github.io/yc-api/industries/industrial-bio.json |
| Industrials | 369 | https://devasheeshg.github.io/yc-api/industries/industrials.json |
| Infrastructure | 285 | https://devasheeshg.github.io/yc-api/industries/infrastructure.json |
| Insurance | 58 | https://devasheeshg.github.io/yc-api/industries/insurance.json |
| Job and Career Services | 19 | https://devasheeshg.github.io/yc-api/industries/job-and-career-services.json |
| Legal | 54 | https://devasheeshg.github.io/yc-api/industries/legal.json |
| Manufacturing and Robotics | 99 | https://devasheeshg.github.io/yc-api/industries/manufacturing-and-robotics.json |
| Marketing | 160 | https://devasheeshg.github.io/yc-api/industries/marketing.json |
| Medical Devices | 44 | https://devasheeshg.github.io/yc-api/industries/medical-devices.json |
| Office Management | 24 | https://devasheeshg.github.io/yc-api/industries/office-management.json |
| Operations | 143 | https://devasheeshg.github.io/yc-api/industries/operations.json |
| Payments | 123 | https://devasheeshg.github.io/yc-api/industries/payments.json |
| Productivity | 224 | https://devasheeshg.github.io/yc-api/industries/productivity.json |
| Real Estate and Construction | 153 | https://devasheeshg.github.io/yc-api/industries/real-estate-and-construction.json |
| Recruiting and Talent | 74 | https://devasheeshg.github.io/yc-api/industries/recruiting-and-talent.json |
| Retail | 131 | https://devasheeshg.github.io/yc-api/industries/retail.json |
| Sales | 137 | https://devasheeshg.github.io/yc-api/industries/sales.json |
| Security | 111 | https://devasheeshg.github.io/yc-api/industries/security.json |
| Social | 111 | https://devasheeshg.github.io/yc-api/industries/social.json |
| Supply Chain and Logistics | 131 | https://devasheeshg.github.io/yc-api/industries/supply-chain-and-logistics.json |
| Therapeutics | 64 | https://devasheeshg.github.io/yc-api/industries/therapeutics.json |
| Transportation Services | 27 | https://devasheeshg.github.io/yc-api/industries/transportation-services.json |
| Travel, Leisure and Tourism | 35 | https://devasheeshg.github.io/yc-api/industries/travel-leisure-and-tourism.json |
| Unspecified | 18 | https://devasheeshg.github.io/yc-api/industries/unspecified.json |
| Virtual and Augmented Reality | 21 | https://devasheeshg.github.io/yc-api/industries/virtual-and-augmented-reality.json |
</details>

### 🏷️ Tags

<details>
<summary>Companies per tag</summary>

| Tag | Count | API endpoint |
| --- | ---- | ------------ |
| 3D Printed Foods | 1 | https://devasheeshg.github.io/yc-api/tags/3d-printed-foods.json |
| 3D Printing | 12 | https://devasheeshg.github.io/yc-api/tags/3d-printing.json |
| AI | 778 | https://devasheeshg.github.io/yc-api/tags/ai.json |
| AI Assistant | 154 | https://devasheeshg.github.io/yc-api/tags/ai-assistant.json |
| AI-Enhanced Learning | 45 | https://devasheeshg.github.io/yc-api/tags/ai-enhanced-learning.json |
| AI-powered Drug Discovery | 39 | https://devasheeshg.github.io/yc-api/tags/ai-powered-drug-discovery.json |
| AIOps | 56 | https://devasheeshg.github.io/yc-api/tags/aiops.json |
| API | 139 | https://devasheeshg.github.io/yc-api/tags/api.json |
| APIs | 9 | https://devasheeshg.github.io/yc-api/tags/apis.json |
| AR | 6 | https://devasheeshg.github.io/yc-api/tags/ar.json |
| Advanced Materials | 7 | https://devasheeshg.github.io/yc-api/tags/advanced-materials.json |
| Advertising | 42 | https://devasheeshg.github.io/yc-api/tags/advertising.json |
| Aerospace | 33 | https://devasheeshg.github.io/yc-api/tags/aerospace.json |
| Agriculture | 31 | https://devasheeshg.github.io/yc-api/tags/agriculture.json |
| Air Taxis | 5 | https://devasheeshg.github.io/yc-api/tags/air-taxis.json |
| Airlines | 4 | https://devasheeshg.github.io/yc-api/tags/airlines.json |
| Airplanes | 10 | https://devasheeshg.github.io/yc-api/tags/airplanes.json |
| Alternative Battery Tech | 2 | https://devasheeshg.github.io/yc-api/tags/alternative-battery-tech.json |
| Alternative Fuels | 1 | https://devasheeshg.github.io/yc-api/tags/alternative-fuels.json |
| Analytics | 183 | https://devasheeshg.github.io/yc-api/tags/analytics.json |
| Anti-Aging | 7 | https://devasheeshg.github.io/yc-api/tags/anti-aging.json |
| Apparel | 4 | https://devasheeshg.github.io/yc-api/tags/apparel.json |
| Architecture | 4 | https://devasheeshg.github.io/yc-api/tags/architecture.json |
| Art Trading Platforms | 1 | https://devasheeshg.github.io/yc-api/tags/art-trading-platforms.json |
| Artificial Intelligence | 906 | https://devasheeshg.github.io/yc-api/tags/artificial-intelligence.json |
| Assistive Tech | 6 | https://devasheeshg.github.io/yc-api/tags/assistive-tech.json |
| Augmented Reality | 23 | https://devasheeshg.github.io/yc-api/tags/augmented-reality.json |
| Auto Commerce | 5 | https://devasheeshg.github.io/yc-api/tags/auto-commerce.json |
| Automation | 86 | https://devasheeshg.github.io/yc-api/tags/automation.json |
| Automotive | 23 | https://devasheeshg.github.io/yc-api/tags/automotive.json |
| Autonomous Delivery | 8 | https://devasheeshg.github.io/yc-api/tags/autonomous-delivery.json |
| Autonomous Trucking | 11 | https://devasheeshg.github.io/yc-api/tags/autonomous-trucking.json |
| B2B | 1081 | https://devasheeshg.github.io/yc-api/tags/b2b.json |
| Banking as a Service | 26 | https://devasheeshg.github.io/yc-api/tags/banking-as-a-service.json |
| Batteryless IoT Sensors | 2 | https://devasheeshg.github.io/yc-api/tags/batteryless-iot-sensors.json |
| Beauty | 10 | https://devasheeshg.github.io/yc-api/tags/beauty.json |
| Big Data | 27 | https://devasheeshg.github.io/yc-api/tags/big-data.json |
| Billing | 7 | https://devasheeshg.github.io/yc-api/tags/billing.json |
| Biometrics | 7 | https://devasheeshg.github.io/yc-api/tags/biometrics.json |
| Bioplastic | 3 | https://devasheeshg.github.io/yc-api/tags/bioplastic.json |
| Biotech | 134 | https://devasheeshg.github.io/yc-api/tags/biotech.json |
| Biotechnology | 15 | https://devasheeshg.github.io/yc-api/tags/biotechnology.json |
| Blockchain | 2 | https://devasheeshg.github.io/yc-api/tags/blockchain.json |
| Booking | 2 | https://devasheeshg.github.io/yc-api/tags/booking.json |
| COVID-19 | 4 | https://devasheeshg.github.io/yc-api/tags/covid-19.json |
| CRISPR | 4 | https://devasheeshg.github.io/yc-api/tags/crispr.json |
| CRM | 23 | https://devasheeshg.github.io/yc-api/tags/crm.json |
| Calendar | 8 | https://devasheeshg.github.io/yc-api/tags/calendar.json |
| Call Center | 9 | https://devasheeshg.github.io/yc-api/tags/call-center.json |
| Cannabis | 7 | https://devasheeshg.github.io/yc-api/tags/cannabis.json |
| Carbon Capture and Removal | 13 | https://devasheeshg.github.io/yc-api/tags/carbon-capture-and-removal.json |
| Careers | 5 | https://devasheeshg.github.io/yc-api/tags/careers.json |
| Cashierless Checkout | 5 | https://devasheeshg.github.io/yc-api/tags/cashierless-checkout.json |
| Cell Therapy | 5 | https://devasheeshg.github.io/yc-api/tags/cell-therapy.json |
| Cellular Agriculture | 6 | https://devasheeshg.github.io/yc-api/tags/cellular-agriculture.json |
| Chat | 6 | https://devasheeshg.github.io/yc-api/tags/chat.json |
| Chatbot | 10 | https://devasheeshg.github.io/yc-api/tags/chatbot.json |
| Chatbots | 3 | https://devasheeshg.github.io/yc-api/tags/chatbots.json |
| China | 3 | https://devasheeshg.github.io/yc-api/tags/china.json |
| Civic Tech | 8 | https://devasheeshg.github.io/yc-api/tags/civic-tech.json |
| Clean Meat | 1 | https://devasheeshg.github.io/yc-api/tags/clean-meat.json |
| Climate | 142 | https://devasheeshg.github.io/yc-api/tags/climate.json |
| ClimateTech | 30 | https://devasheeshg.github.io/yc-api/tags/climatetech.json |
| Cloud Computing | 45 | https://devasheeshg.github.io/yc-api/tags/cloud-computing.json |
| Cloud Gaming | 3 | https://devasheeshg.github.io/yc-api/tags/cloud-gaming.json |
| Cloud Workload Protection | 5 | https://devasheeshg.github.io/yc-api/tags/cloud-workload-protection.json |
| Coding Bootcamps | 2 | https://devasheeshg.github.io/yc-api/tags/coding-bootcamps.json |
| Collaboration | 45 | https://devasheeshg.github.io/yc-api/tags/collaboration.json |
| Commercial Space Launch | 6 | https://devasheeshg.github.io/yc-api/tags/commercial-space-launch.json |
| Community | 58 | https://devasheeshg.github.io/yc-api/tags/community.json |
| Compliance | 72 | https://devasheeshg.github.io/yc-api/tags/compliance.json |
| Computational Storage | 1 | https://devasheeshg.github.io/yc-api/tags/computational-storage.json |
| Computer Vision | 77 | https://devasheeshg.github.io/yc-api/tags/computer-vision.json |
| Construction | 63 | https://devasheeshg.github.io/yc-api/tags/construction.json |
| Consumer | 240 | https://devasheeshg.github.io/yc-api/tags/consumer.json |
| Consumer Finance | 30 | https://devasheeshg.github.io/yc-api/tags/consumer-finance.json |
| Consumer Health Services | 104 | https://devasheeshg.github.io/yc-api/tags/consumer-health-services.json |
| Consumer Products | 13 | https://devasheeshg.github.io/yc-api/tags/consumer-products.json |
| Conversational AI | 42 | https://devasheeshg.github.io/yc-api/tags/conversational-ai.json |
| Conversational Banking | 2 | https://devasheeshg.github.io/yc-api/tags/conversational-banking.json |
| Creator Economy | 32 | https://devasheeshg.github.io/yc-api/tags/creator-economy.json |
| Crowdfunding | 9 | https://devasheeshg.github.io/yc-api/tags/crowdfunding.json |
| Crowdsourcing | 4 | https://devasheeshg.github.io/yc-api/tags/crowdsourcing.json |
| Crypto / Web3 | 91 | https://devasheeshg.github.io/yc-api/tags/crypto-web3.json |
| Cryptocurrency | 10 | https://devasheeshg.github.io/yc-api/tags/cryptocurrency.json |
| Cryptography | 3 | https://devasheeshg.github.io/yc-api/tags/cryptography.json |
| Cultivated Meat | 2 | https://devasheeshg.github.io/yc-api/tags/cultivated-meat.json |
| Culture | 2 | https://devasheeshg.github.io/yc-api/tags/culture.json |
| Cultured Meat | 3 | https://devasheeshg.github.io/yc-api/tags/cultured-meat.json |
| Customer Service | 21 | https://devasheeshg.github.io/yc-api/tags/customer-service.json |
| Customer Success | 26 | https://devasheeshg.github.io/yc-api/tags/customer-success.json |
| Customer Support | 31 | https://devasheeshg.github.io/yc-api/tags/customer-support.json |
| Customization | 2 | https://devasheeshg.github.io/yc-api/tags/customization.json |
| Cyber Insurance | 1 | https://devasheeshg.github.io/yc-api/tags/cyber-insurance.json |
| Cybersecurity | 40 | https://devasheeshg.github.io/yc-api/tags/cybersecurity.json |
| DAO | 2 | https://devasheeshg.github.io/yc-api/tags/dao.json |
| Data Engineering | 97 | https://devasheeshg.github.io/yc-api/tags/data-engineering.json |
| Data Labeling | 16 | https://devasheeshg.github.io/yc-api/tags/data-labeling.json |
| Data Science | 32 | https://devasheeshg.github.io/yc-api/tags/data-science.json |
| Data Visualization | 32 | https://devasheeshg.github.io/yc-api/tags/data-visualization.json |
| Databases | 26 | https://devasheeshg.github.io/yc-api/tags/databases.json |
| Dating | 6 | https://devasheeshg.github.io/yc-api/tags/dating.json |
| DeFi | 13 | https://devasheeshg.github.io/yc-api/tags/defi.json |
| Deep Learning | 38 | https://devasheeshg.github.io/yc-api/tags/deep-learning.json |
| Deepfake Detection | 1 | https://devasheeshg.github.io/yc-api/tags/deepfake-detection.json |
| Delivery | 54 | https://devasheeshg.github.io/yc-api/tags/delivery.json |
| Dental | 4 | https://devasheeshg.github.io/yc-api/tags/dental.json |
| Design | 31 | https://devasheeshg.github.io/yc-api/tags/design.json |
| Design Tools | 63 | https://devasheeshg.github.io/yc-api/tags/design-tools.json |
| DevOps | 49 | https://devasheeshg.github.io/yc-api/tags/devops.json |
| DevSecOps | 34 | https://devasheeshg.github.io/yc-api/tags/devsecops.json |
| Developer Tools | 529 | https://devasheeshg.github.io/yc-api/tags/developer-tools.json |
| Diagnostics | 32 | https://devasheeshg.github.io/yc-api/tags/diagnostics.json |
| Digital Freight Brokerage | 2 | https://devasheeshg.github.io/yc-api/tags/digital-freight-brokerage.json |
| Digital Health | 111 | https://devasheeshg.github.io/yc-api/tags/digital-health.json |
| Diversity & Inclusion | 3 | https://devasheeshg.github.io/yc-api/tags/diversity-inclusion.json |
| Documents | 33 | https://devasheeshg.github.io/yc-api/tags/documents.json |
| Drones | 29 | https://devasheeshg.github.io/yc-api/tags/drones.json |
| Drug Delivery | 6 | https://devasheeshg.github.io/yc-api/tags/drug-delivery.json |
| Drug discovery | 32 | https://devasheeshg.github.io/yc-api/tags/drug-discovery.json |
| E-commerce | 187 | https://devasheeshg.github.io/yc-api/tags/e-commerce.json |
| Edge Computing Semiconductors | 4 | https://devasheeshg.github.io/yc-api/tags/edge-computing-semiconductors.json |
| Edtech | 20 | https://devasheeshg.github.io/yc-api/tags/edtech.json |
| Education | 162 | https://devasheeshg.github.io/yc-api/tags/education.json |
| Election Tech | 2 | https://devasheeshg.github.io/yc-api/tags/election-tech.json |
| Electric Vehicles | 22 | https://devasheeshg.github.io/yc-api/tags/electric-vehicles.json |
| Electronics | 10 | https://devasheeshg.github.io/yc-api/tags/electronics.json |
| Email | 30 | https://devasheeshg.github.io/yc-api/tags/email.json |
| Emerging Markets | 8 | https://devasheeshg.github.io/yc-api/tags/emerging-markets.json |
| Energy | 42 | https://devasheeshg.github.io/yc-api/tags/energy.json |
| Energy Storage | 14 | https://devasheeshg.github.io/yc-api/tags/energy-storage.json |
| Enterprise | 106 | https://devasheeshg.github.io/yc-api/tags/enterprise.json |
| Enterprise Software | 108 | https://devasheeshg.github.io/yc-api/tags/enterprise-software.json |
| Entertainment | 51 | https://devasheeshg.github.io/yc-api/tags/entertainment.json |
| Fashion | 20 | https://devasheeshg.github.io/yc-api/tags/fashion.json |
| Feedback | 7 | https://devasheeshg.github.io/yc-api/tags/feedback.json |
| Femtech | 5 | https://devasheeshg.github.io/yc-api/tags/femtech.json |
| Fertility Tech | 8 | https://devasheeshg.github.io/yc-api/tags/fertility-tech.json |
| FinOps | 29 | https://devasheeshg.github.io/yc-api/tags/finops.json |
| Finance | 85 | https://devasheeshg.github.io/yc-api/tags/finance.json |
| Fintech | 690 | https://devasheeshg.github.io/yc-api/tags/fintech.json |
| Fitness | 21 | https://devasheeshg.github.io/yc-api/tags/fitness.json |
| Food | 10 | https://devasheeshg.github.io/yc-api/tags/food.json |
| Food & Beverage | 28 | https://devasheeshg.github.io/yc-api/tags/food-beverage.json |
| Food Service Robots & Machines | 10 | https://devasheeshg.github.io/yc-api/tags/food-service-robots-machines.json |
| Food Tech | 48 | https://devasheeshg.github.io/yc-api/tags/food-tech.json |
| Fraud Detection | 8 | https://devasheeshg.github.io/yc-api/tags/fraud-detection.json |
| Fraud Prevention | 4 | https://devasheeshg.github.io/yc-api/tags/fraud-prevention.json |
| Fundraising | 3 | https://devasheeshg.github.io/yc-api/tags/fundraising.json |
| Furniture | 6 | https://devasheeshg.github.io/yc-api/tags/furniture.json |
| Fusion Energy | 3 | https://devasheeshg.github.io/yc-api/tags/fusion-energy.json |
| Gaming | 87 | https://devasheeshg.github.io/yc-api/tags/gaming.json |
| Gardening | 2 | https://devasheeshg.github.io/yc-api/tags/gardening.json |
| Gene Therapy | 12 | https://devasheeshg.github.io/yc-api/tags/gene-therapy.json |
| Generative AI | 257 | https://devasheeshg.github.io/yc-api/tags/generative-ai.json |
| Genetic Engineering | 2 | https://devasheeshg.github.io/yc-api/tags/genetic-engineering.json |
| Genomics | 27 | https://devasheeshg.github.io/yc-api/tags/genomics.json |
| Geographic Information System | 4 | https://devasheeshg.github.io/yc-api/tags/geographic-information-system.json |
| Ghost Kitchens | 11 | https://devasheeshg.github.io/yc-api/tags/ghost-kitchens.json |
| GovTech | 46 | https://devasheeshg.github.io/yc-api/tags/govtech.json |
| GraphQL | 3 | https://devasheeshg.github.io/yc-api/tags/graphql.json |
| Grocery | 31 | https://devasheeshg.github.io/yc-api/tags/grocery.json |
| HR Tech | 77 | https://devasheeshg.github.io/yc-api/tags/hr-tech.json |
| Hard Tech | 93 | https://devasheeshg.github.io/yc-api/tags/hard-tech.json |
| Hardware | 138 | https://devasheeshg.github.io/yc-api/tags/hardware.json |
| Health & Wellness | 44 | https://devasheeshg.github.io/yc-api/tags/health-wellness.json |
| Health Insurance | 27 | https://devasheeshg.github.io/yc-api/tags/health-insurance.json |
| Health Tech | 170 | https://devasheeshg.github.io/yc-api/tags/health-tech.json |
| Healthcare | 200 | https://devasheeshg.github.io/yc-api/tags/healthcare.json |
| Healthcare IT | 36 | https://devasheeshg.github.io/yc-api/tags/healthcare-it.json |
| Home Automation | 4 | https://devasheeshg.github.io/yc-api/tags/home-automation.json |
| Home Services | 11 | https://devasheeshg.github.io/yc-api/tags/home-services.json |
| Housing | 20 | https://devasheeshg.github.io/yc-api/tags/housing.json |
| Human Resources | 22 | https://devasheeshg.github.io/yc-api/tags/human-resources.json |
| Hydrogen Energy | 3 | https://devasheeshg.github.io/yc-api/tags/hydrogen-energy.json |
| Identity | 15 | https://devasheeshg.github.io/yc-api/tags/identity.json |
| Immigration | 6 | https://devasheeshg.github.io/yc-api/tags/immigration.json |
| Income Share Agreements | 4 | https://devasheeshg.github.io/yc-api/tags/income-share-agreements.json |
| India | 36 | https://devasheeshg.github.io/yc-api/tags/india.json |
| Indoor Mapping | 3 | https://devasheeshg.github.io/yc-api/tags/indoor-mapping.json |
| Industrial | 25 | https://devasheeshg.github.io/yc-api/tags/industrial.json |
| Industrial Workplace Safety | 4 | https://devasheeshg.github.io/yc-api/tags/industrial-workplace-safety.json |
| Infrastructure | 109 | https://devasheeshg.github.io/yc-api/tags/infrastructure.json |
| Insurance | 70 | https://devasheeshg.github.io/yc-api/tags/insurance.json |
| International | 6 | https://devasheeshg.github.io/yc-api/tags/international.json |
| Investing | 56 | https://devasheeshg.github.io/yc-api/tags/investing.json |
| Investments | 6 | https://devasheeshg.github.io/yc-api/tags/investments.json |
| IoT | 44 | https://devasheeshg.github.io/yc-api/tags/iot.json |
| IoT Security | 2 | https://devasheeshg.github.io/yc-api/tags/iot-security.json |
| Kids | 9 | https://devasheeshg.github.io/yc-api/tags/kids.json |
| Kubernetes | 14 | https://devasheeshg.github.io/yc-api/tags/kubernetes.json |
| Lab-on-a-chip | 1 | https://devasheeshg.github.io/yc-api/tags/lab-on-a-chip.json |
| Latin America | 21 | https://devasheeshg.github.io/yc-api/tags/latin-america.json |
| Legal | 37 | https://devasheeshg.github.io/yc-api/tags/legal.json |
| LegalTech | 53 | https://devasheeshg.github.io/yc-api/tags/legaltech.json |
| Lending | 17 | https://devasheeshg.github.io/yc-api/tags/lending.json |
| Lidar | 1 | https://devasheeshg.github.io/yc-api/tags/lidar.json |
| Live | 5 | https://devasheeshg.github.io/yc-api/tags/live.json |
| Livestock Health | 1 | https://devasheeshg.github.io/yc-api/tags/livestock-health.json |
| Location-based | 2 | https://devasheeshg.github.io/yc-api/tags/location-based.json |
| Logistics | 128 | https://devasheeshg.github.io/yc-api/tags/logistics.json |
| ML | 15 | https://devasheeshg.github.io/yc-api/tags/ml.json |
| Machine Learning | 227 | https://devasheeshg.github.io/yc-api/tags/machine-learning.json |
| Manufacturing | 81 | https://devasheeshg.github.io/yc-api/tags/manufacturing.json |
| Maritime | 3 | https://devasheeshg.github.io/yc-api/tags/maritime.json |
| Market Research | 14 | https://devasheeshg.github.io/yc-api/tags/market-research.json |
| Marketing | 100 | https://devasheeshg.github.io/yc-api/tags/marketing.json |
| Marketplace | 302 | https://devasheeshg.github.io/yc-api/tags/marketplace.json |
| Media | 44 | https://devasheeshg.github.io/yc-api/tags/media.json |
| Medical Devices | 68 | https://devasheeshg.github.io/yc-api/tags/medical-devices.json |
| Medical Robotics | 5 | https://devasheeshg.github.io/yc-api/tags/medical-robotics.json |
| Mental Health | 10 | https://devasheeshg.github.io/yc-api/tags/mental-health.json |
| Mental Health Tech | 37 | https://devasheeshg.github.io/yc-api/tags/mental-health-tech.json |
| Messaging | 43 | https://devasheeshg.github.io/yc-api/tags/messaging.json |
| Metaverse | 8 | https://devasheeshg.github.io/yc-api/tags/metaverse.json |
| Microfluidics | 5 | https://devasheeshg.github.io/yc-api/tags/microfluidics.json |
| Microinsurance | 3 | https://devasheeshg.github.io/yc-api/tags/microinsurance.json |
| Mining | 5 | https://devasheeshg.github.io/yc-api/tags/mining.json |
| Mobility | 13 | https://devasheeshg.github.io/yc-api/tags/mobility.json |
| Monitoring | 15 | https://devasheeshg.github.io/yc-api/tags/monitoring.json |
| Music | 20 | https://devasheeshg.github.io/yc-api/tags/music.json |
| NFT | 5 | https://devasheeshg.github.io/yc-api/tags/nft.json |
| NLP | 21 | https://devasheeshg.github.io/yc-api/tags/nlp.json |
| Nanomedicine | 5 | https://devasheeshg.github.io/yc-api/tags/nanomedicine.json |
| Nanosensors | 4 | https://devasheeshg.github.io/yc-api/tags/nanosensors.json |
| Nanotechnology | 10 | https://devasheeshg.github.io/yc-api/tags/nanotechnology.json |
| Navigation | 4 | https://devasheeshg.github.io/yc-api/tags/navigation.json |
| Neobank | 49 | https://devasheeshg.github.io/yc-api/tags/neobank.json |
| Networks | 4 | https://devasheeshg.github.io/yc-api/tags/networks.json |
| Neurotechnology | 14 | https://devasheeshg.github.io/yc-api/tags/neurotechnology.json |
| Next-gen Network Security | 5 | https://devasheeshg.github.io/yc-api/tags/next-gen-network-security.json |
| No-code | 38 | https://devasheeshg.github.io/yc-api/tags/no-code.json |
| Nonprofit | 25 | https://devasheeshg.github.io/yc-api/tags/nonprofit.json |
| Note-taking | 4 | https://devasheeshg.github.io/yc-api/tags/note-taking.json |
| Notifications | 2 | https://devasheeshg.github.io/yc-api/tags/notifications.json |
| Oncology | 20 | https://devasheeshg.github.io/yc-api/tags/oncology.json |
| Open Source | 161 | https://devasheeshg.github.io/yc-api/tags/open-source.json |
| Operations | 30 | https://devasheeshg.github.io/yc-api/tags/operations.json |
| Payments | 146 | https://devasheeshg.github.io/yc-api/tags/payments.json |
| Payroll | 18 | https://devasheeshg.github.io/yc-api/tags/payroll.json |
| Pediatrics | 3 | https://devasheeshg.github.io/yc-api/tags/pediatrics.json |
| Personalization | 10 | https://devasheeshg.github.io/yc-api/tags/personalization.json |
| Plant-based Meat | 2 | https://devasheeshg.github.io/yc-api/tags/plant-based-meat.json |
| Podcasts | 7 | https://devasheeshg.github.io/yc-api/tags/podcasts.json |
| Primary Care | 8 | https://devasheeshg.github.io/yc-api/tags/primary-care.json |
| Privacy | 19 | https://devasheeshg.github.io/yc-api/tags/privacy.json |
| Procurement | 11 | https://devasheeshg.github.io/yc-api/tags/procurement.json |
| Productivity | 165 | https://devasheeshg.github.io/yc-api/tags/productivity.json |
| Proptech | 83 | https://devasheeshg.github.io/yc-api/tags/proptech.json |
| Psychedelics | 1 | https://devasheeshg.github.io/yc-api/tags/psychedelics.json |
| Quantum Computing | 4 | https://devasheeshg.github.io/yc-api/tags/quantum-computing.json |
| Radar | 3 | https://devasheeshg.github.io/yc-api/tags/radar.json |
| Real Estate | 77 | https://devasheeshg.github.io/yc-api/tags/real-estate.json |
| Recommendation System | 4 | https://devasheeshg.github.io/yc-api/tags/recommendation-system.json |
| Recruiting | 68 | https://devasheeshg.github.io/yc-api/tags/recruiting.json |
| Referrals | 2 | https://devasheeshg.github.io/yc-api/tags/referrals.json |
| Regtech | 20 | https://devasheeshg.github.io/yc-api/tags/regtech.json |
| Reinforcement Learning | 29 | https://devasheeshg.github.io/yc-api/tags/reinforcement-learning.json |
| Remittances | 6 | https://devasheeshg.github.io/yc-api/tags/remittances.json |
| Remote | 6 | https://devasheeshg.github.io/yc-api/tags/remote.json |
| Remote Work | 16 | https://devasheeshg.github.io/yc-api/tags/remote-work.json |
| Renewable Energy | 17 | https://devasheeshg.github.io/yc-api/tags/renewable-energy.json |
| Restaurant Tech | 13 | https://devasheeshg.github.io/yc-api/tags/restaurant-tech.json |
| Retail | 49 | https://devasheeshg.github.io/yc-api/tags/retail.json |
| Retail Tech | 19 | https://devasheeshg.github.io/yc-api/tags/retail-tech.json |
| Reviews | 3 | https://devasheeshg.github.io/yc-api/tags/reviews.json |
| Ridesharing | 2 | https://devasheeshg.github.io/yc-api/tags/ridesharing.json |
| Robotic Process Automation | 33 | https://devasheeshg.github.io/yc-api/tags/robotic-process-automation.json |
| Robotic Surgery | 3 | https://devasheeshg.github.io/yc-api/tags/robotic-surgery.json |
| Robotics | 102 | https://devasheeshg.github.io/yc-api/tags/robotics.json |
| Rocketry | 3 | https://devasheeshg.github.io/yc-api/tags/rocketry.json |
| SEO | 3 | https://devasheeshg.github.io/yc-api/tags/seo.json |
| SMB | 15 | https://devasheeshg.github.io/yc-api/tags/smb.json |
| SMS | 7 | https://devasheeshg.github.io/yc-api/tags/sms.json |
| SaaS | 1106 | https://devasheeshg.github.io/yc-api/tags/saas.json |
| Sales | 117 | https://devasheeshg.github.io/yc-api/tags/sales.json |
| Sales Enablement | 34 | https://devasheeshg.github.io/yc-api/tags/sales-enablement.json |
| Satellites | 19 | https://devasheeshg.github.io/yc-api/tags/satellites.json |
| Scheduling | 10 | https://devasheeshg.github.io/yc-api/tags/scheduling.json |
| Search | 19 | https://devasheeshg.github.io/yc-api/tags/search.json |
| Security | 87 | https://devasheeshg.github.io/yc-api/tags/security.json |
| Security Orchestration, Automation and Response (SOAR) | 1 | https://devasheeshg.github.io/yc-api/tags/security-orchestration-automation-and-response-soar.json |
| Self-Driving Vehicles | 5 | https://devasheeshg.github.io/yc-api/tags/self-driving-vehicles.json |
| Semiconductors | 11 | https://devasheeshg.github.io/yc-api/tags/semiconductors.json |
| Skincare | 1 | https://devasheeshg.github.io/yc-api/tags/skincare.json |
| Sleep Tech | 9 | https://devasheeshg.github.io/yc-api/tags/sleep-tech.json |
| Small Modular Reactors | 2 | https://devasheeshg.github.io/yc-api/tags/small-modular-reactors.json |
| Smart Clothing | 5 | https://devasheeshg.github.io/yc-api/tags/smart-clothing.json |
| Smart Home Assistants | 7 | https://devasheeshg.github.io/yc-api/tags/smart-home-assistants.json |
| Smart Locks | 1 | https://devasheeshg.github.io/yc-api/tags/smart-locks.json |
| Social | 72 | https://devasheeshg.github.io/yc-api/tags/social.json |
| Social Media | 32 | https://devasheeshg.github.io/yc-api/tags/social-media.json |
| Social Network | 23 | https://devasheeshg.github.io/yc-api/tags/social-network.json |
| Solar Power | 19 | https://devasheeshg.github.io/yc-api/tags/solar-power.json |
| Space Exploration | 16 | https://devasheeshg.github.io/yc-api/tags/space-exploration.json |
| Speech Recognition | 5 | https://devasheeshg.github.io/yc-api/tags/speech-recognition.json |
| Sports Tech | 19 | https://devasheeshg.github.io/yc-api/tags/sports-tech.json |
| Stocks | 3 | https://devasheeshg.github.io/yc-api/tags/stocks.json |
| Subscriptions | 39 | https://devasheeshg.github.io/yc-api/tags/subscriptions.json |
| Supply Chain | 79 | https://devasheeshg.github.io/yc-api/tags/supply-chain.json |
| Sustainability | 14 | https://devasheeshg.github.io/yc-api/tags/sustainability.json |
| Sustainable Agriculture | 2 | https://devasheeshg.github.io/yc-api/tags/sustainable-agriculture.json |
| Sustainable Fashion | 9 | https://devasheeshg.github.io/yc-api/tags/sustainable-fashion.json |
| Sustainable Tourism | 3 | https://devasheeshg.github.io/yc-api/tags/sustainable-tourism.json |
| Swarm AI | 1 | https://devasheeshg.github.io/yc-api/tags/swarm-ai.json |
| Swarm Robotics | 1 | https://devasheeshg.github.io/yc-api/tags/swarm-robotics.json |
| Synthetic Biology | 30 | https://devasheeshg.github.io/yc-api/tags/synthetic-biology.json |
| Talent Acquisition | 7 | https://devasheeshg.github.io/yc-api/tags/talent-acquisition.json |
| Team Collaboration | 15 | https://devasheeshg.github.io/yc-api/tags/team-collaboration.json |
| Telecommunications | 27 | https://devasheeshg.github.io/yc-api/tags/telecommunications.json |
| Telehealth | 28 | https://devasheeshg.github.io/yc-api/tags/telehealth.json |
| Telemedicine | 30 | https://devasheeshg.github.io/yc-api/tags/telemedicine.json |
| Therapeutics | 44 | https://devasheeshg.github.io/yc-api/tags/therapeutics.json |
| Ticketing | 2 | https://devasheeshg.github.io/yc-api/tags/ticketing.json |
| Time Series | 3 | https://devasheeshg.github.io/yc-api/tags/time-series.json |
| Trading | 9 | https://devasheeshg.github.io/yc-api/tags/trading.json |
| Transportation | 38 | https://devasheeshg.github.io/yc-api/tags/transportation.json |
| Travel | 47 | https://devasheeshg.github.io/yc-api/tags/travel.json |
| Trust & Safety | 2 | https://devasheeshg.github.io/yc-api/tags/trust-safety.json |
| Unmanned Vehicle | 3 | https://devasheeshg.github.io/yc-api/tags/unmanned-vehicle.json |
| VR Health | 2 | https://devasheeshg.github.io/yc-api/tags/vr-health.json |
| Vertical Farming | 3 | https://devasheeshg.github.io/yc-api/tags/vertical-farming.json |
| Video | 91 | https://devasheeshg.github.io/yc-api/tags/video.json |
| Virtual Reality | 13 | https://devasheeshg.github.io/yc-api/tags/virtual-reality.json |
| Warehouse Management Tech | 13 | https://devasheeshg.github.io/yc-api/tags/warehouse-management-tech.json |
| Weather | 3 | https://devasheeshg.github.io/yc-api/tags/weather.json |
| Web Development | 24 | https://devasheeshg.github.io/yc-api/tags/web-development.json |
| Women's Health | 15 | https://devasheeshg.github.io/yc-api/tags/womens-health.json |
| Workflow Automation | 66 | https://devasheeshg.github.io/yc-api/tags/workflow-automation.json |
| eLearning | 49 | https://devasheeshg.github.io/yc-api/tags/elearning.json |
| eSports | 2 | https://devasheeshg.github.io/yc-api/tags/esports.json |
</details>
<!--end generated readme-->

---

## 📀 Schema

Each endpoint (except `meta.json`) returns an array of company objects with 50+ fields.
Every company object includes:

| Property                | Type       | Description                                                  |
| ----------------------- | ---------- | ------------------------------------------------------------ |
| `id`                    | number     | Unique company ID                                            |
| `name`                  | string     | Company name                                                 |
| `slug`                  | string     | URL-friendly slug (e.g. `"airbnb"`)                          |
| `former_names`          | string[]   | Previous names, if the company was renamed                   |
| `small_logo_thumb_url`  | string     | Square thumbnail logo URL                                    |
| `website`               | string\|null | Company website URL                                        |
| `all_locations`         | string     | Locations separated by semicolons (e.g. `"San Francisco, CA, USA; New York, NY, USA"`) |
| `long_description`      | string\|null | Full company description                                   |
| `one_liner`             | string     | One-line company description                                 |
| `team_size`             | number\|null | Number of employees                                        |
| `industry`              | string     | Primary industry                                             |
| `subindustry`           | string     | Subindustry (e.g. `"Consumer -> Travel, Leisure and Tourism"`) |
| `launched_at`           | number     | Launch date as a Unix timestamp                              |
| `tags`                  | string[]   | Company tags                                                 |
| `tags_highlighted`      | string[]   | Highlighted tags                                             |
| `top_company`           | boolean\|null | Whether this is a YC top company                           |
| `isHiring`              | boolean    | Whether the company is currently hiring                      |
| `nonprofit`             | boolean    | Whether the company is a nonprofit                           |
| `batch`                 | string     | YC batch (e.g. `"Winter 2026"`)                              |
| `status`                | string     | Company status (`"Active"`, `"Inactive"`, `"Acquired"`, `"Public"`) |
| `industries`            | string[]   | All industries the company belongs to                        |
| `regions`               | string[]   | Geographic regions                                           |
| `stage`                 | string     | Company stage (`"Early"`, `"Growth"`, etc.)                  |
| `app_video_public`      | boolean    | Whether the application video is public                      |
| `demo_day_video_public` | boolean    | Whether the demo day video is public                         |
| `app_answers`           | app_answer[]\|null | Application Q&A, if public                            |
| `question_answers`      | question_answer[]\|null | Free-response Q&A, if public                     |
| `url`                   | string     | Company page on ycombinator.com                              |
| `api`                   | string     | This API's endpoint for the company                          |
| `year_founded`          | number\|null | Year the company was founded                               |
| `city`                  | string\|null | City                                                       |
| `country`               | string\|null | Country code (e.g. `"US"`)                                 |
| `linkedin_url`          | string\|null | LinkedIn URL                                               |
| `x_url`                 | string\|null | X (Twitter) URL                                            |
| `fb_url`                | string\|null | Facebook URL                                               |
| `cb_url`                | string\|null | Crunchbase URL                                             |
| `github_url`            | string\|null | GitHub URL                                                 |
| `logo_url`              | string\|null | Logo image URL                                             |
| `app_video_url`         | string\|null | Application video URL                                      |
| `dday_video_url`        | string\|null | Demo day video URL                                         |
| `primary_partner`       | partner\|null | Assigned YC group partner                                 |
| `company_photos`        | string[]   | Company photo URLs                                           |
| `founders`              | founder[]  | List of founders                                             |
| `jobs`                  | job[]      | List of open job postings                                    |
| `news`                  | news[]     | List of press/news articles                                  |
| `launches`              | launch[]   | List of Launch YC posts                                      |

### `app_answer` object

| Property   | Type   | Description                              |
| ---------- | ------ | ---------------------------------------- |
| `question` | string | Application question                     |
| `answer`   | string | Founder's answer                         |

### `question_answer` object

| Property   | Type   | Description                              |
| ---------- | ------ | ---------------------------------------- |
| `question` | string | Free-response question                   |
| `answer`   | string | Founder's answer                         |

### `partner` object

| Property | Type   | Description                                    |
| -------- | ------ | ---------------------------------------------- |
| `name`   | string | Partner's full name (e.g. `"Garry Tan"`)       |
| `url`    | string | Profile page on ycombinator.com                |

### `founder` object

| Property           | Type        | Description                           |
| ------------------ | ----------- | ------------------------------------- |
| `user_id`          | number      | YC internal user ID                   |
| `full_name`        | string      | Founder's full name                   |
| `title`            | string      | Title (e.g. `"Founder/CEO"`)         |
| `founder_bio`      | string\|null | Short bio                            |
| `is_active`        | boolean     | Whether the founder is currently active |
| `linkedin_url`     | string\|null | LinkedIn URL                         |
| `x_url`            | string\|null | X (Twitter) URL                      |
| `avatar_thumb_url` | string\|null | Founder's avatar image URL           |
| `email`            | string\|null | SMTP-verified email address, or `null` if not found |

> **Note:** Only SMTP-verified emails are included (~4.5% of founders). Email discovery generates common name patterns (e.g. `first@domain`, `first.last@domain`) and verifies each via SMTP `RCPT TO`. Catch-all domains and unverifiable patterns return `null`.

### `job` object

| Property       | Type        | Description                                       |
| -------------- | ----------- | ------------------------------------------------- |
| `id`           | number      | Job posting ID                                    |
| `title`        | string      | Job title (e.g. `"Founding Engineer"`)            |
| `url`          | string      | Full URL to the job posting                       |
| `location`     | string      | Job location                                      |
| `type`         | string      | Employment type (`"Full-time"`, `"Part-time"`, etc.) |
| `role`         | string      | Role category (`"Engineering"`, `"Design"`, etc.) |
| `role_type`    | string\|null | Specific role type (`"Full stack"`, `"Backend"`, etc.) |
| `salary_range` | string\|null | Salary range (e.g. `"$120K - $160K"`)            |
| `equity_range` | string\|null | Equity range (e.g. `"1.00% - 3.00%"`)           |
| `experience`   | string\|null | Required experience (e.g. `"1+ years"`)           |
| `visa`         | string      | Visa sponsorship status                           |
| `skills`       | string[]    | Required skills                                   |

### `news` object

| Property | Type   | Description                                   |
| -------- | ------ | --------------------------------------------- |
| `title`  | string | Article headline                              |
| `url`    | string | Link to the article                           |
| `date`   | string | Publication date (e.g. `"Oct 12, 2025"`)      |

### `launch` object

| Property     | Type   | Description                              |
| ------------ | ------ | ---------------------------------------- |
| `id`         | number | Launch post ID                           |
| `title`      | string | Launch post title                        |
| `tagline`    | string | Short tagline                            |
| `body`       | string | Full post content (markdown)             |
| `url`        | string | Full URL to the Launch YC post           |
| `votes`      | number | Number of upvotes                        |
| `created_at` | string | ISO 8601 timestamp (e.g. `"2024-03-15T12:00:00Z"`) |

### Example

`GET` https://devasheeshg.github.io/yc-api/batches/winter-2009/airbnb.json

```json
{
  "id": 271,
  "name": "Airbnb",
  "slug": "airbnb",
  "former_names": [],
  "small_logo_thumb_url": "https://bookface-images.s3.amazonaws.com/small_logos/3e9a0092bee2ccf926e650e59c06503ec6b9ee65.png",
  "website": "http://airbnb.com",
  "all_locations": "San Francisco, CA, USA",
  "long_description": "Founded in August of 2008 and based in San Francisco, California, Airbnb is a trusted community marketplace for people to list, discover, and book unique accommodations around the world — online or from a mobile phone. Whether an apartment for a night, a castle for a week, or a villa for a month, Airbnb connects people to unique travel experiences, at any price point, in more than 33,000 cities and 192 countries. And with world-class customer service and a growing community of users, Airbnb is the easiest way for people to monetize their extra space and showcase it to an audience of millions.  \r\n\r\nNo global movement springs from individuals. It takes an entire team united behind something big. Together, we work hard, we laugh a lot, we brainstorm nonstop, we use hundreds of Post-Its a week, and we give the best high-fives in town. Headquartered in San Francisco, we have satellite offices in Dublin, London, Barcelona, Paris, Milan, Copenhagen, Berlin, Moscow, São Paolo, Sydney, and Singapore.",
  "one_liner": "Book accommodations around the world.",
  "team_size": 6132,
  "industry": "Consumer",
  "subindustry": "Consumer -> Travel, Leisure and Tourism",
  "launched_at": 1326790856,
  "tags": [
    "Marketplace",
    "Travel"
  ],
  "tags_highlighted": [],
  "top_company": true,
  "isHiring": false,
  "nonprofit": false,
  "batch": "Winter 2009",
  "status": "Public",
  "industries": [
    "Consumer",
    "Travel, Leisure and Tourism"
  ],
  "regions": [
    "United States of America",
    "America / Canada"
  ],
  "stage": "Growth",
  "app_video_public": false,
  "demo_day_video_public": false,
  "app_answers": null,
  "question_answers": false,
  "url": "https://www.ycombinator.com/companies/airbnb",
  "api": "https://devasheeshg.github.io/yc-api/batches/winter-2009/airbnb.json",
  "year_founded": 2008,
  "city": "San Francisco",
  "country": "US",
  "linkedin_url": "https://www.linkedin.com/company/airbnb/",
  "x_url": "https://twitter.com/Airbnb",
  "fb_url": "https://www.facebook.com/airbnb/",
  "cb_url": "https://www.crunchbase.com/organization/airbnb",
  "github_url": null,
  "logo_url": "https://bookface-images.s3.amazonaws.com/small_logos/3e9a0092bee2ccf926e650e59c06503ec6b9ee65.png",
  "app_video_url": null,
  "dday_video_url": null,
  "company_photos": [
    "https://bookface-images.s3.us-west-2.amazonaws.com/attachments/8a7236c94b4d9b78b67ce66e02cbca497e632d99.png"
  ],
  "primary_partner": {
    "name": "Garry Tan",
    "url": "https://www.ycombinator.com/people/garry-tan"
  },
  "founders": [
    {
      "user_id": 21981,
      "full_name": "Brian Chesky",
      "title": "Founder/CEO",
      "founder_bio": "Brian Chesky is the co-founder,  Head of Community, and  CEO of Airbnb, which he started with Joe Gebbia and Nathan Blecharczyk in 2008. Brian sets the company’s strategy to connect people to unique travel experiences, and drives Airbnb’s mission to create a world where anyone can belong anywhere. Originally from New York, Brian graduated from the Rhode Island School of Design where he received a Bachelor of Fine Arts in Industrial Design.",
      "is_active": true,
      "linkedin_url": "https://www.linkedin.com/in/brianchesky/",
      "x_url": "https://twitter.com/bchesky",
      "avatar_thumb_url": "https://bookface-images.s3.us-west-2.amazonaws.com/avatars/7415ee0d3978ae738c766fc109863385303b066a.jpg",
      "email": null
    },
    {
      "user_id": 21988,
      "full_name": "Nathan Blecharczyk",
      "title": "Founder/CTO",
      "founder_bio": "Nathan Blecharczyk is the co-founder, Chief Strategy Officer, and Chairman of Airbnb China. Nathan plays a leading role in driving key strategic initiatives across the global business. Previously he oversaw the creation of Airbnb’s engineering, data science, and performance marketing teams. Nathan became an entrepreneur in his youth, running a business while he was in high school that sold to clients in more than 20 countries. He earned a degree in Computer Science from Harvard University.",
      "is_active": true,
      "linkedin_url": "https://www.linkedin.com/in/blecharczyk/",
      "x_url": "https://twitter.com/nathanblec",
      "avatar_thumb_url": "https://bookface-images.s3.us-west-2.amazonaws.com/avatars/43dd0e2c9396adccf8b4e456d806245942afc1ed.jpg",
      "email": null
    },
    {
      "user_id": 21984,
      "full_name": "Joe Gebbia",
      "title": "Founder/CPO",
      "founder_bio": "Joe Gebbia is the co-founder of Airbnb which began in his San Francisco living room and spread to nearly 7M listings in 191+ countries, changing how people trust each other. Joe now holds a strategic advisory position and serves on the Board of Directors at Airbnb. His latest venture, Samara, also cemented in economic empowerment, housing resources, and design, produces fully customized, factory-made homes designed to create rental income, house family, and form new types of housing communities.",
      "is_active": true,
      "linkedin_url": "https://www.linkedin.com/in/jgebbia/",
      "x_url": "https://x.com/jgebbia",
      "avatar_thumb_url": "https://bookface-images.s3.us-west-2.amazonaws.com/avatars/8edd4b693f91d2a5507247fbd23259dbe88d4dba.jpg",
      "email": null
    }
  ],
  "jobs": [],
  "news": [
    {
      "title": "Airbnb CEO Brian Chesky on taking it back to basics: ‘I can’t make products just for 41-year-old tech founders’ - The Verge",
      "url": "https://www.theverge.com/2023/5/9/23716903/airbnb-ceo-brian-chesky-rooms-ai-travel-future-of-work-summer-2023",
      "date": "May 09, 2023"
    },
    {
      "title": "Airbnb launches Airbnb Rooms listing category for budget travel",
      "url": "https://www.usatoday.com/story/travel/news/2023/05/03/airbnb-rooms-listing-category-budget-travel/70178696007/",
      "date": "May 03, 2023"
    },
    {
      "title": "Brian Chesky Isn't Running Airbnb--He's 'Designing' It",
      "url": "https://www.inc.com/magazine/202303/christine-lagorio-chafkin/brian-chesky-isnt-running-airbnb-hes-designing-it.html",
      "date": "Mar 16, 2023"
    },
    {
      "title": "Airbnb’s cofounder just donated $25M to get plastic out of the ocean",
      "url": "https://fortune.com/2023/02/02/airbnb-joe-gebbia-donation-25-million-ocean-cleanup-great-pacific-garbage-patch",
      "date": "Feb 02, 2023"
    },
    {
      "title": "'Hocus Pocus' fans can now stay in the Sanderson Sisters' cottage : NPR",
      "url": "https://www.npr.org/2022/10/04/1126605757/hocus-pocus-cottage-airbnb",
      "date": "Oct 06, 2022"
    }
  ],
  "launches": []
}
```
## 🤝 Contributing

Contributions are welcome! This project is open source under the [MIT License](LICENSE).

### Help wanted: Improve email discovery rate

The biggest open problem is **founder email discovery**. Currently only ~4% of founder emails can be verified via SMTP `RCPT TO`. The breakdown:

| Category | % of founders | Why |
|---|---|---|
| **Catch-all domains** | ~17% | Mostly Google Workspace. These domains accept mail for *any* address, so we can't distinguish real from fake. |
| **Not found (rejected)** | ~63% | The domain's mail server rejects all candidate patterns. Founders likely use custom aliases, personal email forwarding, or non-standard naming conventions. |
| **No MX records** | ~12% | Company website domain has no mail server (dead sites, redirect-only domains, etc.). |
| **Connection failures** | ~4% | Mail servers that refuse or timeout on our SMTP connections. |
| **Verified** | ~4% | SMTP returns 250 for a candidate pattern on a non-catch-all domain. |

#### What we currently try

- 6 name-based patterns: `first@`, `first.last@`, `first_last@`, `firstlast@`, `flast@`, `f.last@`
- 3-part name expansion (e.g. "Mary Jane Watson" → tries `mary.watson@`, `mary.jane@`, `maryjane.watson@`, etc.)
- Mononym support (single-word names → `{name}@domain`)
- LinkedIn/Twitter username as `{username}@domain`

## ⭐ Star History

<a href="https://star-history.com/#devasheeshG/yc-api&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=devasheeshG/yc-api&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=devasheeshG/yc-api&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=devasheeshG/yc-api&type=Date" />
 </picture>
</a>

## 📄 License

This project is licensed under the [MIT License](LICENSE).
