/** Company operating status. */
export enum CompanyStatus {
    Active = 'Active',
    Inactive = 'Inactive',
    Acquired = 'Acquired',
    Public = 'Public',
}

/** YC group partner assigned to a company. */
export interface Partner {
    name: string | null;
    url: string | null;
}

/** Company founder. */
export interface Founder {
    user_id: number | null;
    full_name: string | null;
    title: string | null;
    founder_bio: string | null;
    is_active: boolean | null;
    linkedin_url: string | null;
    x_url: string | null;
    avatar_thumb_url: string | null;
    /** SMTP-verified email address, or null if not found. */
    email: string | null;
}

/** Open job posting. */
export interface Job {
    id: number | null;
    title: string | null;
    url: string | null;
    location: string | null;
    type: string | null;
    role: string | null;
    role_type: string | null;
    salary_range: string | null;
    equity_range: string | null;
    experience: string | null;
    visa: string | null;
    skills: string[];
}

/** Press/news item. */
export interface News {
    title: string | null;
    url: string | null;
    date: string | null;
}

/** A single application answer. */
export interface AppAnswer {
    question: string | null;
    answer: string | null;
}

/** A single free-response question answer. */
export interface QuestionAnswer {
    question: string | null;
    answer: string | null;
}

/** Launch YC post. */
export interface Launch {
    id: number | null;
    title: string | null;
    tagline: string | null;
    body: string | null;
    url: string | null;
    votes: number | null;
    created_at: string | null;
}

/** A Y Combinator company with all available data. */
export interface Company {
    // Core fields (from Algolia)
    id: number | null;
    name: string | null;
    slug: string | null;
    former_names: string[];
    small_logo_thumb_url: string | null;
    website: string | null;
    all_locations: string | null;
    long_description: string | null;
    one_liner: string | null;
    team_size: number | null;
    industry: string | null;
    subindustry: string | null;
    launched_at: number | null;
    tags: string[];
    tags_highlighted: string[];
    top_company: boolean | null;
    isHiring: boolean | null;
    nonprofit: boolean | null;
    batch: string | null;
    status: CompanyStatus | null;
    industries: string[];
    regions: string[];
    stage: string | null;
    app_video_public: boolean | null;
    demo_day_video_public: boolean | null;
    app_answers: AppAnswer[] | null;
    question_answers: QuestionAnswer[] | null;
    url: string | null;
    api: string | null;

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
