# Lead Generation Pipeline

AI-powered lead generation using [yc-api](https://github.com/devasheeshG/yc-api) data. Fetches active YC startups, scores them with Claude, and pushes qualified leads to Notion.

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
| `NOTION_API_KEY` | Notion integration token |
| `NOTION_DATABASE_ID` | Target Notion database ID |

## Usage

```bash
uv run python main.py
```
