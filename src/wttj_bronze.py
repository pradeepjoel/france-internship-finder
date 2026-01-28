import time
from typing import List, Set
from playwright.sync_api import sync_playwright

BASE = "https://www.welcometothejungle.com"
LIST_URL = (
    "https://www.welcometothejungle.com/fr/jobs"
    "?refinementList%5Boffices.country_code%5D%5B%5D=FR"
)

def wttj_list_urls_france(
    limit: int = 400,
    max_scrolls: int = 25,
    sleep_s: float = 1.0,
) -> List[str]:
    urls: List[str] = []
    seen: Set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(LIST_URL, timeout=60000)

        time.sleep(3)

        for step in range(max_scrolls):
            links = page.eval_on_selector_all(
                "a[href*='/jobs/']",
                "els => els.map(e => e.href)"
            )

            new = 0
            for href in links:
                if "/companies/" in href and href not in seen:
                    seen.add(href)
                    urls.append(href)
                    new += 1
                    if len(urls) >= limit:
                        browser.close()
                        return urls

            print(f"[WTTJ] scroll {step+1}/{max_scrolls} | +{new} | total={len(urls)}")

            page.mouse.wheel(0, 5000)
            time.sleep(sleep_s)

            if new == 0:
                break

        browser.close()

    return urls
