import time
import requests
from typing import List, Set, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def _normalize_job_url(href: str, base: str) -> Optional[str]:
    if not href:
        return None
    if href.startswith("/"):
        href = base + href
    if "welcometothejungle.com" not in href:
        return None
    if "/fr/jobs/" not in href:
        return None
    # remove tracking params
    href = href.split("?")[0]
    return href

def wttj_list_urls_france(
    limit: int = 400,
    max_scrolls: int = 30,
    sleep_s: float = 1.0,
) -> List[str]:
    """
    Discover WTTJ France job URLs (JS-rendered) using Playwright.
    Returns a de-duped list of job URLs.

    NOTE:
    - Streamlit Cloud app does NOT need Playwright (it reads SQLite).
    - GitHub Actions refresh workflow installs Playwright and runs this.
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError(
            "Playwright is required for URL discovery. "
            "Install it in GitHub Actions (pip install playwright) or locally."
        ) from e

    start_url = (
        "https://www.welcometothejungle.com/fr/jobs"
        "?refinementList%5Boffices.country_code%5D%5B%5D=FR"
    )
    base = "https://www.welcometothejungle.com"
    seen: Set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(start_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1500)

        for _ in range(max_scrolls):
            # collect links from current DOM
            anchors = page.query_selector_all("a[href*='/fr/jobs/']")
            for a in anchors:
                href = a.get_attribute("href")
                u = _normalize_job_url(href, base)
                if u:
                    seen.add(u)

            if len(seen) >= limit:
                break

            # scroll + wait for more jobs to load
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(int(sleep_s * 1000))

        browser.close()

    return list(seen)[:limit]
