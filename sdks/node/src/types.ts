/** Company operating status. */
export enum CompanyStatus {
    Active = 'Active',
    Inactive = 'Inactive',
    Acquired = 'Acquired',
    Public = 'Public',
}

/** Company stage. */
export enum CompanyStage {
    Early = 'Early',
    Growth = 'Growth',
}

/** Primary industry. */
export enum CompanyIndustry {
    B2B = 'B2B',
    Consumer = 'Consumer',
    Education = 'Education',
    Fintech = 'Fintech',
    Government = 'Government',
    Healthcare = 'Healthcare',
    Industrials = 'Industrials',
    RealEstateAndConstruction = 'Real Estate and Construction',
    Unspecified = 'Unspecified',
}

/** Company sub-industry. */
export enum CompanySubindustry {
    B2B = 'B2B',
    B2B_Analytics = 'B2B -> Analytics',
    B2B_EngineeringProductAndDesign = 'B2B -> Engineering, Product and Design',
    B2B_FinanceAndAccounting = 'B2B -> Finance and Accounting',
    B2B_HumanResources = 'B2B -> Human Resources',
    B2B_Infrastructure = 'B2B -> Infrastructure',
    B2B_Legal = 'B2B -> Legal',
    B2B_Marketing = 'B2B -> Marketing',
    B2B_OfficeManagement = 'B2B -> Office Management',
    B2B_Operations = 'B2B -> Operations',
    B2B_Productivity = 'B2B -> Productivity',
    B2B_RecruitingAndTalent = 'B2B -> Recruiting and Talent',
    B2B_Retail = 'B2B -> Retail',
    B2B_Sales = 'B2B -> Sales',
    B2B_Security = 'B2B -> Security',
    B2B_SupplyChainAndLogistics = 'B2B -> Supply Chain and Logistics',
    Consumer = 'Consumer',
    Consumer_ApparelAndCosmetics = 'Consumer -> Apparel and Cosmetics',
    Consumer_ConsumerElectronics = 'Consumer -> Consumer Electronics',
    Consumer_Content = 'Consumer -> Content',
    Consumer_FoodAndBeverage = 'Consumer -> Food and Beverage',
    Consumer_Gaming = 'Consumer -> Gaming',
    Consumer_HomeAndPersonal = 'Consumer -> Home and Personal',
    Consumer_JobAndCareerServices = 'Consumer -> Job and Career Services',
    Consumer_Social = 'Consumer -> Social',
    Consumer_TransportationServices = 'Consumer -> Transportation Services',
    Consumer_TravelLeisureAndTourism = 'Consumer -> Travel, Leisure and Tourism',
    Consumer_VirtualAndAugmentedReality = 'Consumer -> Virtual and Augmented Reality',
    Education = 'Education',
    Fintech = 'Fintech',
    Fintech_AssetManagement = 'Fintech -> Asset Management',
    Fintech_BankingAndExchange = 'Fintech -> Banking and Exchange',
    Fintech_ConsumerFinance = 'Fintech -> Consumer Finance',
    Fintech_CreditAndLending = 'Fintech -> Credit and Lending',
    Fintech_Insurance = 'Fintech -> Insurance',
    Fintech_Payments = 'Fintech -> Payments',
    Government = 'Government',
    Healthcare = 'Healthcare',
    Healthcare_ConsumerHealthAndWellness = 'Healthcare -> Consumer Health and Wellness',
    Healthcare_Diagnostics = 'Healthcare -> Diagnostics',
    Healthcare_DrugDiscoveryAndDelivery = 'Healthcare -> Drug Discovery and Delivery',
    Healthcare_HealthcareIT = 'Healthcare -> Healthcare IT',
    Healthcare_HealthcareServices = 'Healthcare -> Healthcare Services',
    Healthcare_IndustrialBio = 'Healthcare -> Industrial Bio',
    Healthcare_MedicalDevices = 'Healthcare -> Medical Devices',
    Healthcare_Therapeutics = 'Healthcare -> Therapeutics',
    Industrials = 'Industrials',
    Industrials_Agriculture = 'Industrials -> Agriculture',
    Industrials_Automotive = 'Industrials -> Automotive',
    Industrials_AviationAndSpace = 'Industrials -> Aviation and Space',
    Industrials_Climate = 'Industrials -> Climate',
    Industrials_Defense = 'Industrials -> Defense',
    Industrials_Drones = 'Industrials -> Drones',
    Industrials_Energy = 'Industrials -> Energy',
    Industrials_ManufacturingAndRobotics = 'Industrials -> Manufacturing and Robotics',
    RealEstateAndConstruction = 'Real Estate and Construction',
    RealEstateAndConstruction_Construction = 'Real Estate and Construction -> Construction',
    RealEstateAndConstruction_HousingAndRealEstate = 'Real Estate and Construction -> Housing and Real Estate',
    Unspecified = 'Unspecified',
}

/** Employment type. */
export enum JobType {
    FullTime = 'Full-time',
    Internship = 'Internship',
    Contract = 'Contract',
    CoFounder = 'Co-founder',
}

/** Role category. */
export enum JobRole {
    Design = 'Design',
    Engineering = 'Engineering',
    Finance = 'Finance',
    Legal = 'Legal',
    Marketing = 'Marketing',
    Operations = 'Operations',
    Product = 'Product',
    RecruitingHR = 'Recruiting & HR',
    Sales = 'Sales',
    Science = 'Science',
    Support = 'Support',
}

/** Visa sponsorship status. */
export enum JobVisa {
    USOnly = 'US citizen/visa only',
    NotRequired = 'US citizenship/visa not required',
    WillSponsor = 'Will sponsor',
}

/** Required experience level. */
export enum JobExperience {
    OnePlus = '1+ years',
    ThreePlus = '3+ years',
    SixPlus = '6+ years',
    ElevenPlus = '11+ years',
    Any = 'Any (new grads ok)',
}

/** YC group partner assigned to a company. */
export interface Partner {
    name: string;
    url: string;
}

/** Company founder. */
export interface Founder {
    user_id: number;
    full_name: string;
    title: string;
    founder_bio: string | null;
    is_active: boolean;
    linkedin_url: string | null;
    x_url: string | null;
    avatar_thumb_url: string;
    /** SMTP-verified email address, or null if not found. */
    email?: string | null;
}

/** Open job posting. */
export interface Job {
    id: number;
    title: string;
    url: string;
    location: string;
    type: JobType;
    role: JobRole;
    role_type: string | null;
    salary_range: string;
    equity_range: string;
    experience: JobExperience | null;
    visa: JobVisa;
    skills: string[];
}

/** Press/news item. */
export interface News {
    title: string;
    url: string;
    date: string;
}

/** A single application answer. */
export interface AppAnswer {
    question: string;
    answer: string | null;
}

/** A single free-response question answer. */
export interface QuestionAnswer {
    question: string;
    answer: string;
}

/** Launch YC post. */
export interface Launch {
    id: number;
    title: string;
    tagline: string;
    body: string;
    url: string;
    votes: number;
    created_at: string;
}

/** A Y Combinator company with all available data. */
export interface Company {
    // Core fields (from Algolia)
    id: number;
    name: string;
    slug: string;
    former_names: string[];
    small_logo_thumb_url: string;
    website: string | null;
    all_locations: string;
    long_description: string | null;
    one_liner: string;
    team_size: number | null;
    industry: CompanyIndustry;
    subindustry: CompanySubindustry;
    launched_at: number;
    tags: string[];
    tags_highlighted: string[];
    top_company: boolean | null;
    isHiring: boolean;
    nonprofit: boolean;
    batch: string;
    status: CompanyStatus;
    industries: string[];
    regions: string[];
    stage: CompanyStage;
    app_video_public: boolean;
    demo_day_video_public: boolean;
    app_answers: AppAnswer[] | null;
    question_answers: QuestionAnswer[] | null;
    url: string;
    api: string;

    // Enriched fields (from detail page scraping)
    year_founded: number | null;
    city: string | null;
    country: string | null;
    linkedin_url: string | null;
    x_url: string | null;
    fb_url: string | null;
    cb_url: string | null;
    github_url: string | null;
    logo_url: string | null;
    app_video_url: string | null;
    dday_video_url: string | null;
    primary_partner: Partner | null;
    company_photos: string[];
    founders: Founder[];
    jobs: Job[];
    news: News[];
    launches: Launch[];

    [key: string]: unknown;
}

/** A single entry in the meta.json index. */
export interface MetaEntry {
    name: string;
    count: number;
    api: string;
}

/** Top-level meta.json response. */
export interface Meta {
    last_updated: string | null;
    readme: string | null;
    companies: Record<string, MetaEntry>;
    tags: Record<string, MetaEntry>;
    industries: Record<string, MetaEntry>;
    batches: Record<string, MetaEntry>;
}
