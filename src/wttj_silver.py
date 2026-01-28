import json
import re
from typing import Optional, Dict
from bs4 import BeautifulSoup

def _strip_html(s: str) -> str:
    if not s:
        return ""
    soup = BeautifulSoup(s, "lxml")
    return soup.get_text("\n", strip=True)

def _first_text(node):
    return node.get_text(strip=True) if node else ""

def _parse_jsonld_jobposting(soup: BeautifulSoup) -> Optional[Dict]:
    scripts = soup.select("script[type='application/ld+json']")
    for sc in scripts:
        raw = sc.get_text(strip=True)
        if not raw:
            continue

        try:
            data = json.loads(raw)
        except Exception:
            raw2 = re.sub(r",\s*}", "}", raw)
            raw2 = re.sub(r",\s*]", "]", raw2)
            try:
                data = json.loads(raw2)
            except Exception:
                continue

        items = [data] if isinstance(data, dict) else data if isinstance(data, list) else []
        for obj in items:
            if not isinstance(obj, dict):
                continue
            if obj.get("@type") == "JobPosting":
                title = obj.get("title", "") or ""

                org = obj.get("hiringOrganization") or {}
                company = org.get("name", "") if isinstance(org, dict) else ""

                location_text = ""
                loc = obj.get("jobLocation")
                if isinstance(loc, list) and loc:
                    loc = loc[0]
                if isinstance(loc, dict):
                    addr = loc.get("address") or {}
                    if isinstance(addr, dict):
                        city = addr.get("addressLocality") or ""
                        region = addr.get("addressRegion") or ""
                        country = addr.get("addressCountry") or ""
                        location_text = ", ".join(x for x in [city, region, country] if x)

                contract = obj.get("employmentType") or ""
                if isinstance(contract, list):
                    contract = ", ".join(str(x) for x in contract if x)

                description = _strip_html(obj.get("description", "") or "")

                return {
                    "title": title,
                    "company": company,
                    "location": location_text,
                    "contract": str(contract),
                    "description": description
                }

    return None

def parse_job_fields(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    job = _parse_jsonld_jobposting(soup)
    if job:
        return job

    title = _first_text(soup.select_one("h1"))
    company = _first_text(soup.select_one("[data-testid='job-header-company-name']"))
    location = _first_text(soup.select_one("[data-testid='job-location']"))
    contract = _first_text(soup.select_one("[data-testid='job-contract-type']"))

    desc_node = soup.select_one("[data-testid='job-description']")
    description = desc_node.get_text("\n", strip=True) if desc_node else soup.get_text("\n", strip=True)

    return {
        "title": title,
        "company": company,
        "location": location,
        "contract": contract,
        "description": description
    }
