from src.db import init_db, conn
from src.wttj_bronze import wttj_list_urls_france, fetch
from src.wttj_silver import parse_job_fields
from src.gold_features import compute_gold

def bronze_ingest():
    # Playwright-based discovery
    urls = wttj_list_urls_france(limit=400, max_scrolls=30)
    print(f"[BRONZE] discovered urls: {len(urls)}")

    new = 0
    with conn() as c:
        for url in urls:
            try:
                html = fetch(url)
                c.execute(
                    "INSERT OR IGNORE INTO bronze_raw(url, source, html) VALUES (?, ?, ?)",
                    (url, "wttj", html),
                )
                if c.total_changes > 0:
                    new += 1
            except Exception:
                continue
    print(f"[BRONZE] new pages: {new}")

def silver_transform():
    new = 0
    with conn() as c:
        rows = c.execute("""
            SELECT b.url, b.source, b.html
            FROM bronze_raw b
            LEFT JOIN silver_jobs s ON s.url = b.url
            WHERE s.url IS NULL
        """).fetchall()

        for url, source, html in rows:
            try:
                f = parse_job_fields(html)
                c.execute("""
                    INSERT OR REPLACE INTO silver_jobs(url, source, title, company, location, contract, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (url, source, f["title"], f["company"], f["location"], f["contract"], f["description"]))
                new += 1
            except Exception:
                continue
    print(f"[SILVER] parsed: {new}")

def gold_compute():
    new = 0
    with conn() as c:
        rows = c.execute("""
            SELECT s.url, s.title, s.contract, s.description
            FROM silver_jobs s
            LEFT JOIN gold_jobs g ON g.url = s.url
            WHERE g.url IS NULL
        """).fetchall()

        for url, title, contract, description in rows:
            try:
                g = compute_gold(title, contract, description)
                c.execute("""
                    INSERT OR REPLACE INTO gold_jobs(url, language, english_score, contract_type, is_target)
                    VALUES (?, ?, ?, ?, ?)
                """, (url, g["language"], g["english_score"], g["contract_type"], g["is_target"]))
                new += 1
            except Exception:
                continue
    print(f"[GOLD] computed: {new}")

def main():
    init_db()
    bronze_ingest()
    silver_transform()
    gold_compute()
    print("✅ Pipeline completed.")

if __name__ == "__main__":
    main()
