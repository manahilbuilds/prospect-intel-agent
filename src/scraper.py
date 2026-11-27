"""Web scraper module to fetch and clean readable business text from a URL."""

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def normalize_url(url: str) -> str:
    """Ensure the URL has an HTTP/HTTPS scheme."""
    cleaned = url.strip()
    if not cleaned.startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"
    return cleaned


def extract_domain(url: str) -> str:
    """Return a filesystem-safe domain name from a URL."""
    parsed = urlparse(normalize_url(url))
    return parsed.netloc.replace("www.", "").replace(":", "_")


def scrape_website(url: str, max_chars: int = 12000) -> dict[str, str]:
    """Fetch a webpage and return cleaned title, meta description, and body text."""
    target_url = normalize_url(url)
    response = requests.get(target_url, headers=DEFAULT_HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else "N/A"

    meta_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = (
        meta_tag["content"].strip()
        if meta_tag and meta_tag.get("content")
        else "N/A"
    )

    # Remove non-content elements so the LLM only sees meaningful copy
    for tag in soup(["script", "style", "noscript", "svg", "iframe", "nav", "footer"]):
        tag.decompose()

    raw_text = soup.get_text(separator="\n")
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)[:max_chars]

    return {
        "url": target_url,
        "title": title,
        "meta_description": meta_desc,
        "content": clean_text,
    }
