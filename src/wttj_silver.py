import json
import re
from typing import Optional, Dict

from bs4 import BeautifulSoup

def _clean_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _parse_jsonld_jobposting(soup: BeautifulSoup) -> Optional[Dict]:
    """
    Try to extract JobPosting from JSON-LD scripts if present.
    """
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for sc in scripts:
        try:
            data = json.loads(sc.get_text(strip=True))
        except Exception:
            continue

        # JSON-LD can be dict or list
        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                return item

    return None

def parse_job_fields(html: str, url: str) -> dict:
    """
    Parse job page HTML -> structured fields (title/company/location/contract/description)
    Uses html.parser (no lxml dependency).
    """
    soup = BeautifulSoup(html, "html.parser")

    title = company = location = contract = description = ""

    jp = _parse_jsonld_jobposting(soup)
    if jp:
        title = jp.get("title") or ""
        org = jp.get("hiringOrganization") or {}
        if isinstance(org, dict):
            company = org.get("name") or ""
        loc = jp.get("jobLocation") or ""
        # jobLocation can be dict/list
        if isinstance(loc, list) and loc:
            loc = loc[0]
        if isinstance(loc, dict):
            addr = loc.get("address") or {}
            if isinstance(addr, dict):
                city = addr.get("addressLocality") or ""
                region = addr.get("addressRegion") or ""
                country = addr.get("addressCountry") or ""
                parts = [p for p in [city, region, country] if p]
                location = ", ".join(parts)

        contract = jp.get("employmentType") or ""
        description = soup.get_text(" ", strip=True)

    # fallback selectors
    if not title:
        h1 = soup.find("h1")
        title = _clean_text(h1.get_text()) if h1 else ""

    if not company:
        # WTTJ often includes company in meta or structured parts; keep best-effort:
        og = soup.find("meta", attrs={"property": "og:site_name"})
        company = _clean_text(og.get("content")) if og and og.get("content") else ""

    if not description:
        description = soup.get_text(" ", strip=True)

    return {
        "url": url,
        "source": "WTTJ",
        "title": _clean_text(title),
        "company": _clean_text(company),
        "location": _clean_text(location),
        "contract": _clean_text(contract),
        "description": _clean_text(description),
    }
