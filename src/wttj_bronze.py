from typing import List
from urllib.parse import quote_plus
import time

from playwright.sync_api import sync_playwright

BASE = "https://www.welcometothejungle.com"
LIST_URL = BASE + "/fr/jobs"

def _collect_links_from_page(page) -> List[str]:
    # grab all job links currently visible
    hrefs = page.eval_on_selector_all(
        "a[href*='/jobs/']",
        "els => els.map(e => e.href)"
    )
    # de-dup while preserving order
    seen, out = set(), []
    for h in hrefs:
        if "/jobs/" in h and "welcometothejungle.com" in h and h not in seen:
            seen.add(h)
            out.append(h)
    return out

def wttj_list_urls_france(limit: int = 400, max_scrolls: int = 25) -> List[str]:
    """
    Uses a real browser (Playwright) to load WTTJ listings like Chrome,
    scroll to load more, and extract job URLs.
    """
    keywords = [
        "data engineer", "data analyst", "data scientist",
        "front end developer", "business analyst", "digital marketing",
        "python", "sql", "spark", "databricks", "machine learning"
    ]

    collected: List[str] = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="fr-FR")
        page = context.new_page()

        for kw in keywords:
            q = quote_plus(kw)
            url = f"{LIST_URL}?refinementList%5Boffices.country_code%5D%5B%5D=FR&query={q}"
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # small wait for content to render
            page.wait_for_timeout(1500)

            # scroll multiple times to load more cards
            last_count = 0
            for _ in range(max_scrolls):
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(1000)
                urls = _collect_links_from_page(page)
                if len(urls) == last_count:
                    # no new links after scroll => stop scrolling
                    break
                last_count = len(urls)

            urls = _collect_links_from_page(page)
            for u in urls:
                if u not in seen:
                    seen.add(u)
                    collected.append(u)
                if len(collected) >= limit:
                    browser.close()
                    return collected[:limit]

            # tiny pause between keyword queries
            time.sleep(0.4)

        browser.close()

    return collected[:limit]

# Keep requests-style fetch for the job page itself (your pipeline uses this)
import requests
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}
def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text
