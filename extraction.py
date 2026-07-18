import os
import json
import time
import hashlib
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.bbva.com.co/"
ALLOWED_DOMAIN = "www.bbva.com.co"
SEED_URLS = [
    "https://www.bbva.com.co/",
    "https://www.bbva.com.co/personas/sitemap.html",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RAGTestBot/1.0; +https://example.com/bot)"
}

RAW_DIR = "data/raw"
CLEAN_DIR = "data/clean"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return (
        parsed.scheme in {"http", "https"}
        and parsed.netloc == ALLOWED_DOMAIN
        and not url.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip"))
    )


def url_to_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def fetch(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        if "text/html" not in resp.headers.get("Content-Type", ""):
            return None
        return resp.text
    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None


def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        full = urljoin(base_url, a["href"])
        full = full.split("#")[0]
        if is_valid_url(full):
            links.add(full)
    return sorted(links)


def clean_content(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else ""
    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "li"])]
    clean_text = "\n".join([t for t in paragraphs if len(t) > 30])

    return {
        "title": title,
        "headings": headings,
        "clean_text": clean_text,
    }


def save_document(url: str, html: str, cleaned: dict):
    doc_id = url_to_id(url)

    with open(f"{RAW_DIR}/{doc_id}.json", "w", encoding="utf-8") as f:
        json.dump({"url": url, "raw_html": html}, f, ensure_ascii=False, indent=2)

    with open(f"{CLEAN_DIR}/{doc_id}.json", "w", encoding="utf-8") as f:
        json.dump({"url": url, **cleaned}, f, ensure_ascii=False, indent=2)


def crawl(max_pages: int = 30):
    visited = set()
    queue = list(SEED_URLS)

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue

        html = fetch(url)
        if not html:
            visited.add(url)
            continue

        cleaned = clean_content(html)
        save_document(url, html, cleaned)

        links = extract_links(html, url)
        for link in links:
            if link not in visited and link not in queue:
                queue.append(link)

        visited.add(url)
        time.sleep(1)

    print(f"Crawled {len(visited)} pages")


if __name__ == "__main__":
    crawl()