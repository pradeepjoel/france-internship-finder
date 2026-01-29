import time
import requests
from bs4 import BeautifulSoup
from typing import List, Set, Optional, Dict, Any

BASE = "https://www.welcometothejungle.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(url: str) -> str:
    """Fetch a job page HTML."""
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def _normalize_job_url(href: str) -> Optional[str]:
    if not href:
        return None

    if href.startswith("/"):
        href = BASE + href

    if "welcometothejungle.com" not in href:
        return None

    if "/fr/companies/" in href and "/jobs/" in href:
        return href.split("?")[0]

    return None

def _extract_urls_from_api_json(data: Dict[str, Any]) -> List[str]:
    """
    WTTJ API responses can vary. Try common shapes.
    """
    candidates = []
    if isinstance(data.get("jobs"), list):
        candidates = data["jobs"]
    elif isinstance(data.get("results"), list):
        candidates = data["results"]
    elif isinstance(data.get("data"), dict) and isinstance(data["data"].get("jobs"), list):
        candidates = data["data"]["jobs"]

    urls: List[str] = []
    for j in candidates:
        if not isinstance(j, dict):
            continue

        u = j.get("public_url") or j.get("url") or j.get("website_url") or j.get("href") or j.get("path")
        if not u or not isinstance(u, str):
            continue

        if u.startswith("/"):
            u = BASE + u

        norm = _normalize_job_url(u)
        if norm:
            urls.append(norm)

    return urls

def _wttj_api_fetch_page(page: int, per_page: int, debug: bool = False) -> List[str]:
    endpoints = [
        f"{BASE}/api/v1/jobs",
        f"{BASE}/api/v1/search/jobs",
    ]

    params_variants = [
        {"page": page, "per_page": per_page, "country_code": "FR"},
        {"page": page, "per_page": per_page, "offices.country_code": "FR"},
        {"page": page, "per_page": per_page, "query": "", "country_code": "FR"},
    ]

    last_err = None
    for ep in endpoints:
        for params in params_variants:
            try:
                r = requests.get(ep, headers=HEADERS, params=params, timeout=30)
                if debug:
                    print(f"[WTTJ][api] GET {r.url} -> {r.status_code}")
                if r.status_code >= 400:
                    last_err = f"{ep} -> {r.status_code}"
                    continue

                # Some endpoints return HTML when blocked → protect json()
                try:
                    data = r.json()
                except Exception as e:
                    last_err = f"json parse failed: {e}"
                    continue

                urls = _extract_urls_from_api_json(data)
                if urls:
                    return urls

            except Exception as e:
                last_err = str(e)
                continue

    if debug:
        print(f"[WTTJ][api] failed to parse jobs (last_err={last_err})")
    return []

def wttj_list_urls_france(
    limit: int = 400,
    max_pages: int = 40,
    per_page: int = 50,
    sleep_s: float = 0.2,
    debug: bool = False,
) -> List[str]:
    """
    Primary: WTTJ API pagination (aim 300-400 URLs)
    Fallback: HTML paging (usually ~30)
    """
    seen: Set[str] = set()
    urls: List[str] = []

    # --- API mode ---
    for page in range(1, max_pages + 1):
        page_urls = _wttj_api_fetch_page(page=page, per_page=per_page, debug=debug)
        if debug:
            print(f"[WTTJ][api] page={page} got={len(page_urls)}")

        if not page_urls:
            break

        added = 0
        for u in page_urls:
            if u not in seen:
                seen.add(u)
                urls.append(u)
                added += 1
                if len(urls) >= limit:
                    return urls[:limit]

        if debug:
            print(f"[WTTJ][api] page={page} added={added} total={len(urls)}")

        time.sleep(sleep_s)

    if len(urls) >= 60:
        return urls[:limit]

    # --- HTML fallback ---
    if debug:
        print("[WTTJ] API gave too few URLs, falling back to HTML paging...")

    page = 1
    while page <= max_pages and len(urls) < limit:
        list_url = (
            f"{BASE}/fr/jobs"
            "?refinementList%5Boffices.country_code%5D%5B%5D=FR"
            f"&page={page}"
        )
        html = fetch(list_url)
        soup = BeautifulSoup(html, "html.parser")

        page_urls = []
        for a in soup.select("a[href*='/jobs/']"):
            href = a.get("href") or ""
            norm = _normalize_job_url(href)
            if norm:
                page_urls.append(norm)

        new = 0
        for u in page_urls:
            if u not in seen:
                seen.add(u)
                urls.append(u)
                new += 1
                if len(urls) >= limit:
                    break

        if debug:
            print(f"[WTTJ][html] page={page} new={new} total={len(urls)}")

        if new == 0:
            break

        page += 1
        time.sleep(sleep_s)

    return urls[:limit]
