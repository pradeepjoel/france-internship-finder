import time
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Set, Optional, Dict, Any, Tuple

BASE = "https://www.welcometothejungle.com"

HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ✅ We only want these contract types
ALLOWED_CONTRACT_TOKENS = {
    "intern",         # internship / intern
    "stage",          # stage / stagiaire
    "stagiaire",
    "alternance",     # alternance
    "apprent",        # apprenticeship / apprentissage
    "apprentissage",
    "trainee",
}

def fetch(url: str) -> str:
    r = requests.get(url, headers=HTML_HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def _normalize_job_url(href: str) -> Optional[str]:
    if not href:
        return None

    if href.startswith("/"):
        href = BASE + href

    if "welcometothejungle.com" not in href:
        return None

    if "/companies/" in href and "/jobs/" in href:
        return href.split("?")[0]

    return None

# ---------------------------
# Extract window.env (Algolia creds)
# ---------------------------

def _extract_env_from_html(html: str, debug: bool = False) -> Dict[str, Any]:
    marker = "window.env"
    i = html.find(marker)
    if i == -1:
        return {}

    j = html.find("{", i)
    if j == -1:
        return {}

    depth = 0
    k = j
    in_str = False
    esc = False
    while k < len(html):
        ch = html[k]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    raw = html[j:k+1]
                    try:
                        return json.loads(raw)
                    except Exception:
                        return {}
        k += 1

    return {}

def _pick_algolia_config(env: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], List[str]]:
    app_id = env.get("ALGOLIA_APP_ID") or env.get("ALGOLIA_APPLICATION_ID")
    api_key = env.get("ALGOLIA_API_KEY_CLIENT") or env.get("ALGOLIA_SEARCH_API_KEY")

    prefix = env.get("ALGOLIA_JOBS_INDEX_PREFIX")
    candidates: List[str] = []

    if isinstance(prefix, str) and prefix:
        candidates += [f"{prefix}_fr", prefix, f"{prefix}_jobs_fr", f"{prefix}_jobs"]

    for k, v in env.items():
        if isinstance(k, str) and isinstance(v, str) and ("ALGOLIA" in k and "INDEX" in k):
            candidates.append(v)

    candidates += [
        "wttj_jobs_production_fr",
        "wttj_jobs_production",
        "wttj_jobs_fr",
        "wttj_jobs",
        "jobs_fr",
        "jobs",
    ]

    seen = set()
    out = []
    for x in candidates:
        if x and x not in seen:
            seen.add(x)
            out.append(x)

    return app_id, api_key, out

# ---------------------------
# Algolia
# ---------------------------

def _algolia_post(app_id: str, api_key: str, index: str, params: str, debug: bool) -> Tuple[int, Optional[Dict[str, Any]]]:
    url = f"https://{app_id}-dsn.algolia.net/1/indexes/{index}/query"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "X-Algolia-API-Key": api_key,
        "X-Algolia-Application-Id": app_id,
        "Origin": BASE,
        "Referer": f"{BASE}/fr/jobs",
        "Accept": "application/json",
    }

    r = requests.post(url, headers=headers, json={"params": params}, timeout=30)
    if debug:
        print(f"[WTTJ][algolia] POST index={index} -> {r.status_code}")
    if r.status_code != 200:
        return r.status_code, None

    try:
        return 200, r.json()
    except Exception:
        return 200, None

def _find_working_index(app_id: str, api_key: str, indexes: List[str], debug: bool) -> Optional[str]:
    test_params = "query=&page=0&hitsPerPage=1"
    for idx in indexes:
        code, data = _algolia_post(app_id, api_key, idx, test_params, debug=debug)
        if code != 200 or not isinstance(data, dict):
            continue
        hits = data.get("hits")
        if isinstance(hits, list) and len(hits) > 0:
            if debug:
                print(f"[WTTJ][algolia] ✅ working index: {idx}")
            return idx
    return None

def _is_target_contract(hit: Dict[str, Any]) -> bool:
    """
    Filter Algolia hits to internships/alternance only.
    Your TOP_KEYS show `contract_type` exists.
    """
    ct = hit.get("contract_type")

    # Sometimes it's a string, sometimes list, sometimes None
    vals: List[str] = []
    if isinstance(ct, str):
        vals = [ct]
    elif isinstance(ct, list):
        vals = [str(x) for x in ct if x is not None]

    # Fallback: sometimes in profile/summary/name
    if not vals:
        for k in ("name", "summary"):
            v = hit.get(k)
            if isinstance(v, str) and v.strip():
                vals.append(v)

    blob = " ".join(vals).lower()
    return any(tok in blob for tok in ALLOWED_CONTRACT_TOKENS)

def _build_url_from_hit(hit: Dict[str, Any]) -> Optional[str]:
    job_slug = hit.get("slug")
    org = hit.get("organization")

    if not isinstance(job_slug, str) or not job_slug.strip():
        return None
    if not isinstance(org, dict):
        return None

    org_slug = org.get("slug") or org.get("company_slug")
    if not isinstance(org_slug, str) or not org_slug.strip():
        return None

    return f"{BASE}/fr/companies/{org_slug}/jobs/{job_slug}"

def _extract_urls_from_hits(hits: List[Any], only_internships: bool = True) -> List[str]:
    out: List[str] = []
    seen = set()

    for h in hits:
        if not isinstance(h, dict):
            continue

        # ✅ filter BEFORE building URL
        if only_internships and not _is_target_contract(h):
            continue

        built = _build_url_from_hit(h)
        if built:
            norm = _normalize_job_url(built)
            if norm and norm not in seen:
                seen.add(norm)
                out.append(norm)

        # Also accept any direct url-ish fields if present
        for k in ["public_url", "url", "website_url", "href", "path"]:
            v = h.get(k)
            if isinstance(v, str):
                norm = _normalize_job_url(v)
                if norm and norm not in seen:
                    seen.add(norm)
                    out.append(norm)

    return out

def _list_urls_algolia(limit: int, max_pages: int, per_page: int, sleep_s: float, debug: bool, only_internships: bool) -> List[str]:
    shell = fetch(f"{BASE}/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR")
    env = _extract_env_from_html(shell, debug=debug)
    app_id, api_key, indexes = _pick_algolia_config(env)

    if debug:
        print(f"[WTTJ][algolia] app_id={app_id} api_key={'YES' if api_key else 'NO'} candidates={indexes[:8]}...")

    if not app_id or not api_key:
        return []

    idx = _find_working_index(app_id, api_key, indexes, debug=debug)
    if not idx:
        if debug:
            print("[WTTJ][algolia] ❌ no working index found")
        return []

    seen: Set[str] = set()
    urls: List[str] = []

    for page in range(0, max_pages):
        params = f"query=&page={page}&hitsPerPage={per_page}"
        code, data = _algolia_post(app_id, api_key, idx, params, debug=debug)
        if code != 200 or not isinstance(data, dict):
            break

        hits = data.get("hits")
        if not isinstance(hits, list) or len(hits) == 0:
            break

        page_urls = _extract_urls_from_hits(hits, only_internships=only_internships)

        added = 0
        for u in page_urls:
            if u not in seen:
                seen.add(u)
                urls.append(u)
                added += 1
                if len(urls) >= limit:
                    return urls[:limit]

        if debug:
            print(f"[WTTJ][algolia] page={page} hits={len(hits)} urls_found={len(page_urls)} added={added} total={len(urls)}")

        time.sleep(sleep_s)

    return urls[:limit]

# ---------------------------
# HTML fallback (~30)
# ---------------------------

def _list_urls_html(limit: int, max_pages: int, sleep_s: float, debug: bool) -> List[str]:
    seen: Set[str] = set()
    urls: List[str] = []
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

def wttj_list_urls_france(
    limit: int = 400,
    max_pages: int = 40,
    per_page: int = 50,
    sleep_s: float = 0.2,
    debug: bool = False,
    only_internships: bool = True,   # ✅ default ON
) -> List[str]:
    urls = _list_urls_algolia(
        limit=limit,
        max_pages=max_pages,
        per_page=per_page,
        sleep_s=sleep_s,
        debug=debug,
        only_internships=only_internships,
    )
    if len(urls) >= 60:
        return urls[:limit]

    if debug:
        print("[WTTJ] Algolia gave too few URLs, falling back to HTML paging...")

    return _list_urls_html(limit=limit, max_pages=max_pages, sleep_s=sleep_s, debug=debug)
