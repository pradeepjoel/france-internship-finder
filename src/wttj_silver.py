import json
import re
from typing import Optional, Dict

from bs4 import BeautifulSoup


def _clean_text(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def _parse_jsonld_jobposting(soup: BeautifulSoup) -> Optional[Dict]:
    """Try to extract JobPosting from JSON-LD scripts if present."""
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for sc in scripts:
        try:
            raw = sc.get_text(strip=True)
            if not raw:
                continue
            data = json.loads(raw)
        except Exception:
            continue

        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                return item
    return None


def parse_job_fields(html: str, url: str = "") -> dict:
    """
    Parse job page HTML -> structured fields (title/company/location/contract/description)
    url is optional so the pipeline won't crash if it calls parse_job_fields(html).
    """
    soup = BeautifulSoup(html or "", "html.parser")

    title = company = location = contract = ""
    description = ""

    jp = _parse_jsonld_jobposting(soup)
    if jp:
        title = jp.get("title") or ""

        org = jp.get("hiringOrganization") or {}
        if isinstance(org, dict):
            company = org.get("name") or ""

        loc = jp.get("jobLocation") or ""
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

        emp = jp.get("employmentType") or ""
        contract = emp if isinstance(emp, str) else str(emp)

    # fallback: title
    if not title:
        h1 = soup.find("h1")
        title = h1.get_text(" ", strip=True) if h1 else ""

    # fallback: company
    if not company:
        # og:site_name is NOT always company, but keep as best-effort fallback
        og = soup.find("meta", attrs={"property": "og:site_name"})
        company = (og.get("content") or "") if og else ""

    # description: prefer readable text; avoid returning entire site garbage if possible
    # (Still best-effort without site-specific selectors)
    description = soup.get_text(" ", strip=True)

    return {
        "url": url,
        "source": "wttj",
        "title": _clean_text(title),
        "company": _clean_text(company),
        "location": _clean_text(location),
        "contract": _clean_text(contract),
        "description": _clean_text(description),
    }
