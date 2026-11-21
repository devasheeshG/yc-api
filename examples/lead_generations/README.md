# Lead Generation Pipeline

AI-powered lead generation using [yc-api](https://github.com/devasheeshG/yc-api) data. Fetches active YC startups, qualifies them with Claude (web research + Brave Search), and pushes results to Notion.

## Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.template .env
# Fill in your API keys
```

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `ANTHROPIC_BASE_URL` | Anthropic API base URL (default: `https://api.anthropic.com`) |
| `BRAVE_SEARCH_API_KEY` | Brave Search API key |
| `NOTION_API_KEY` | Notion integration token |
| `NOTION_DATABASE_ID` | Target Notion database ID |

## Notion Database Schema

Create a Notion database with these columns:

| Column | Type | Notes |
|---|---|---|
| Company Name | Title | Company name (used for dedup) |
| Batch | Rich Text | YC batch, e.g. "Winter 2024" |
| Website URL | URL | Company website |
| YC URL | URL | Link to YC startup directory page |
| Qualified | Checkbox | Whether the lead is qualified |
| Fit Score | Select | `HIGH` / `MEDIUM` / `LOW` (qualified only) |
| Reason | Rich Text | Qualification rationale if qualified, disqualification reason if not |
| Status | Select | `New` / `Contacted` / `Replied` / `Meeting` / `Skipped` / `Closed` (qualified only) |

## Usage

```bash
uv run python main.py
```
