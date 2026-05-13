# ekantipur-scraper

Small [Playwright](https://playwright.dev/python/) (Python **sync** API) script that reads public pages on [ekantipur.com](https://ekantipur.com) and saves JSON locally.

## What it collects

| Source | Data |
|--------|------|
| `/entertainment` | Top **5** story cards: title, image URL, category, author |
| `/cartoon` | Today’s cartoon: title, image URL, author (when the layout matches) |

Output file: **`output.json`** (UTF-8, Nepali text not escaped).

## Setup

Requires **Python 3.12+** and [uv](https://docs.astral.sh/uv/).

```bash
cd ekantipur-scraper
uv sync
uv run playwright install chromium
```

## Run

```bash
uv run python scraper.py
```

(Or activate `.venv` after `uv sync` and run `python scraper.py`.)

A Chromium window opens (`headless=False` in code). Change that in `scraper.py` if you prefer no UI.

## Project layout

- `scraper.py` — scraping logic and `main()`
- `pyproject.toml` — dependency: `playwright` (install with `uv sync`)

Use this responsibly: check the site’s terms, avoid hammering their servers, and expect selectors to break if the site redesigns.
