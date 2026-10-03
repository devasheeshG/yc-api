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

#### `CompanyStatus`

- `Active`
- `Inactive`
- `Acquired`
- `Public`

#### `CompanyStage`

- `Early`
- `Growth`

#### `CompanyIndustry`

- `B2B`
- `Consumer`
- `Education`
- `Fintech`
- `Government`
- `Healthcare`
- `Industrials`
- `RealEstateAndConstruction`
- `Unspecified`

#### `CompanySubindustry`

- `B2B`
- `B2B_Analytics`
- `B2B_EngineeringProductAndDesign`
- `B2B_FinanceAndAccounting`
- `B2B_HumanResources`
- `B2B_Infrastructure`
- `B2B_Legal`
- `B2B_Marketing`
- `B2B_OfficeManagement`
- `B2B_Operations`
- `B2B_Productivity`
- `B2B_RecruitingAndTalent`
- `B2B_Retail`
- `B2B_Sales`
- `B2B_Security`
- `B2B_SupplyChainAndLogistics`
- `Consumer`
- `Consumer_ApparelAndCosmetics`
- `Consumer_ConsumerElectronics`
- `Consumer_Content`
- `Consumer_FoodAndBeverage`
- `Consumer_Gaming`
- `Consumer_HomeAndPersonal`
- `Consumer_JobAndCareerServices`
- `Consumer_Social`
- `Consumer_TransportationServices`
- `Consumer_TravelLeisureAndTourism`
- `Consumer_VirtualAndAugmentedReality`
- `Education`
- `Fintech`
- `Fintech_AssetManagement`
- `Fintech_BankingAndExchange`
- `Fintech_ConsumerFinance`
- `Fintech_CreditAndLending`
- `Fintech_Insurance`
- `Fintech_Payments`
- `Government`
- `Healthcare`
- `Healthcare_ConsumerHealthAndWellness`
- `Healthcare_Diagnostics`
- `Healthcare_DrugDiscoveryAndDelivery`
- `Healthcare_HealthcareIT`
- `Healthcare_HealthcareServices`
- `Healthcare_IndustrialBio`
- `Healthcare_MedicalDevices`
- `Healthcare_Therapeutics`
- `Industrials`
- `Industrials_Agriculture`
- `Industrials_Automotive`
- `Industrials_AviationAndSpace`
- `Industrials_Climate`
- `Industrials_Defense`
- `Industrials_Drones`
- `Industrials_Energy`
- `Industrials_ManufacturingAndRobotics`
- `RealEstateAndConstruction`
- `RealEstateAndConstruction_Construction`
- `RealEstateAndConstruction_HousingAndRealEstate`
- `Unspecified`

#### `JobType`

- `FullTime`
- `Internship`
- `Contract`
- `CoFounder`

#### `JobRole`

- `Design`
- `Engineering`
- `Finance`
- `Legal`
- `Marketing`
- `Operations`
- `Product`
- `RecruitingHR`
- `Sales`
- `Science`
- `Support`

#### `JobVisa`

- `USOnly`
- `NotRequired`
- `WillSponsor`

#### `JobExperience`

- `OnePlus`
- `ThreePlus`
- `SixPlus`
- `ElevenPlus`
- `Any`

## License

MIT
