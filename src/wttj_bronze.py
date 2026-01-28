import time
import requests
from bs4 import BeautifulSoup
from typing import List, Set

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def wttj_list_urls_france(limit: int = 300, max_pages: int = 30, sleep_s: float = 0.8) -> List[str]:
    """
    Crawl WTTJ jobs listing pages for France and return job URLs.
    Uses built-in HTML parser (no lxml) so Streamlit Cloud can install deps easily.
    """
    base = "https://www.welcometothejungle.com"
    page = 1
    seen: Set[str] = set()
    urls: List[str] = []

    while page <= max_pages and len(urls) < limit:
        list_url = (
            "https://www.welcometothejungle.com/fr/jobs"
            "?refinementList%5Boffices.country_code%5D%5B%5D=FR"
            f"&page={page}"
        )
        html = fetch(list_url)
        soup = BeautifulSoup(html, "html.parser")

        page_urls = []
        for a in soup.select("a[href*='/jobs/']"):
            href = a.get("href")
            if not href:
                continue
            if href.startswith("/"):
                href = base + href
            if "welcometothejungle.com" in href and "/jobs/" in href:
                page_urls.append(href)

        # dedupe
        new = 0
        for u in page_urls:
            if u not in seen:
                seen.add(u)
                urls.append(u)
                new += 1
                if len(urls) >= limit:
                    break

        # stop if no new urls found
        if new == 0:
            break

        page += 1
        time.sleep(sleep_s)

    return urls[:limit]
