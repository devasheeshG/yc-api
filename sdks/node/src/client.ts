import type { Company, Meta } from './types.js';

const DEFAULT_BASE = 'https://devasheeshg.github.io/yc-api';

export interface YCClientOptions {
    /** API base URL. Defaults to the GitHub Pages endpoint. */
    baseUrl?: string;
    /** Request timeout in milliseconds. Defaults to 30 000. */
    timeout?: number;
}

export interface SearchOptions {
    batch?: string;
    industry?: string;
    tag?: string;
    hiring?: boolean;
    top?: boolean;
    nonprofit?: boolean;
}

/**
 * Typed client for the YC Companies API.
 *
 * @example
 * ```ts
 * import { YCClient } from "@devasheeshg/yc-api";
 *
 * const client = new YCClient();
 * const companies = await client.getAll();
 * ```
 */
export class YCClient {
    private base: string;
    private timeout: number;

    constructor(options: YCClientOptions = {}) {
        this.base = (options.baseUrl ?? DEFAULT_BASE).replace(/\/+$/, '');
        this.timeout = options.timeout ?? 30_000;
    }

    private async fetchJSON<T>(path: string): Promise<T> {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), this.timeout);
        try {
            const resp = await fetch(`${this.base}/${path}`, {
                signal: controller.signal,
            });
            if (!resp.ok) {
                throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
            }
            return (await resp.json()) as T;
        } finally {
            clearTimeout(timer);
        }
    }

    // ---- Meta ----

    /** Fetch the API index (meta.json). */
    async getMeta(): Promise<Meta> {
        return this.fetchJSON<Meta>('meta.json');
    }

    // ---- Company lists ----

    /** Fetch every company. */
    async getAll(): Promise<Company[]> {
        return this.fetchJSON<Company[]>('companies/all.json');
    }

    /** Fetch top YC companies. */
    async getTop(): Promise<Company[]> {
        return this.fetchJSON<Company[]>('companies/top.json');
    }

    /** Fetch companies that are currently hiring. */
    async getHiring(): Promise<Company[]> {
        return this.fetchJSON<Company[]>('companies/hiring.json');
    }

    /** Fetch nonprofit companies. */
    async getNonprofit(): Promise<Company[]> {
        return this.fetchJSON<Company[]>('companies/nonprofit.json');
    }

    // ---- Individual lookups ----

    /** Fetch a single company by its batch and company slug. */
    async getCompany(batchSlug: string, companySlug: string): Promise<Company> {
        return this.fetchJSON<Company>(`batches/${batchSlug}/${companySlug}.json`);
    }

    /** Fetch all companies in a batch (e.g. `'winter-2026'`). */
    async getBatch(batchSlug: string): Promise<Company[]> {
        return this.fetchJSON<Company[]>(`batches/${batchSlug}.json`);
    }

    /** Fetch all companies in an industry. */
    async getIndustry(industrySlug: string): Promise<Company[]> {
        return this.fetchJSON<Company[]>(`industries/${industrySlug}.json`);
    }

    /** Fetch all companies with a given tag. */
    async getTag(tagSlug: string): Promise<Company[]> {
        return this.fetchJSON<Company[]>(`tags/${tagSlug}.json`);
    }

    // ---- Search ----

    /**
     * Client-side filter over all companies.
     *
     * Fetches the full list once and filters in memory.
     * For large-scale use, prefer the specific `get*` methods.
     */
    async search(options: SearchOptions = {}): Promise<Company[]> {
        let companies = await this.getAll();

        if (options.batch !== undefined) {
            companies = companies.filter((c) => c.batch === options.batch);
        }
        if (options.industry !== undefined) {
            companies = companies.filter((c) => (c.industries ?? []).includes(options.industry!));
        }
        if (options.tag !== undefined) {
            companies = companies.filter((c) => (c.tags ?? []).includes(options.tag!));
        }
        if (options.hiring !== undefined) {
            companies = companies.filter((c) => c.isHiring === options.hiring);
        }
        if (options.top !== undefined) {
            companies = companies.filter((c) => c.top_company === options.top);
        }
        if (options.nonprofit !== undefined) {
            companies = companies.filter((c) => c.nonprofit === options.nonprofit);
        }

        return companies;
    }
}
