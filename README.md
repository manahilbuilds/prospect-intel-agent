# Prospect Intelligence Agent

An autonomous Python CLI agent that scrapes any B2B company website, extracts structured business intelligence using Google Gemini + Pydantic, identifies operational bottlenecks, and generates a grounded cold outreach hook.

## Why This Exists
Sales teams and agencies waste hours manually reading prospect websites before outreach or discovery calls. Dumping raw HTML into ChatGPT produces hallucinated, generic fluff.

This tool enforces a deterministic pipeline:
1. **Clean Extraction (`scraper.py`)**: Strips scripts, navigation, and boilerplate noise using `BeautifulSoup`.
2. **Strict Schema Enforcement (`schemas.py`)**: Uses `Pydantic` models to guarantee predictable JSON output.
3. **Grounded Synthesis (`agent.py`)**: Uses Gemini structured outputs (`response_schema`) to tie every pain point directly to evidence found on the site.

## Architecture
```text
Target URL ──▶ BeautifulSoup Scraper ──▶ Gemini (Structured JSON) ──▶ Terminal Brief + JSON Export
```

## Quickstart

### 1. Clone & Install
```bash
git clone https://github.com/manahilbuilds/prospect-intel-agent.git
cd prospect-intel-agent
python -m venv .venv
.venv\Scripts\activate  # On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Key
Copy `.env.example` to `.env` and add your free Google AI Studio key:
```env
GEMINI_API_KEY=your_key_here
```

### 3. Run
```bash
python -m src.main https://example.com
```

Output is rendered cleanly in your terminal and saved to `outputs/<domain>.json`.
