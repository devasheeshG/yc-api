import { describe, it, expect } from "vitest";
import { YCClient } from "../src/client.js";

describe("Parse all.json", () => {
    it("get_all should fetch and parse all companies", async () => {
        const client = new YCClient();
        const companies = await client.getAll();
        expect(companies.length).toBeGreaterThan(0);
    }, 60_000);
});
