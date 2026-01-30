import pandas as pd
import streamlit as st

from src.db import init_db, conn
from app_style import inject_css

# ---- Page setup ----
st.set_page_config(page_title="France Internship Finder", layout="wide")
inject_css()
init_db()

st.title("🇫🇷 Internship Finder (France)")
st.caption("Internships & Alternance • English-friendly • France")

# Contract types we allow in the UI (extra safety)
ALLOWED_CONTRACT_TYPES = {"INTERNSHIP", "ALTERNANCE", "APPRENTICESHIP"}

@st.cache_data(ttl=120)
def load_df():
    with conn() as c:
        return pd.read_sql_query(
            """
            SELECT
                s.title,
                s.company,
                s.location,
                s.url,
                s.description,
                g.language,
                g.english_score,
                g.contract_type,
                g.is_target
            FROM silver_jobs s
            JOIN gold_jobs g ON g.url = s.url
            WHERE g.is_target = 1
              AND g.contract_type IN ('INTERNSHIP','ALTERNANCE','APPRENTICESHIP')
            """,
            c,
        )

df = load_df()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Filters")

    mode = st.radio(
        "Mode",
        ["All internships/alternance", "English-friendly only"],
        index=0,
    )

    min_score_default = 0 if mode == "All internships/alternance" else 40
    min_score = st.slider("Min EnglishScore", 0, 100, min_score_default)

    role = st.radio(
        "Role",
        ["All", "Data & AI", "Software", "Business", "Marketing"],
    )

    search = st.text_input("Search keywords")

    work_mode = st.multiselect(
        "Work mode",
        ["Remote", "Hybrid", "On-site", "Unspecified"],
        default=["Remote", "Hybrid", "On-site", "Unspecified"],
    )

# ---------- FILTERING ----------
f = df.copy()

# (extra safety) remove any non-target contracts just in case
f = f[f["contract_type"].isin(ALLOWED_CONTRACT_TYPES)]

# English score filter
f = f[f["english_score"] >= min_score]

# Role filter (keyword-based)
if role != "All":
    role_map = {
        "Data & AI": ["data", "ml", "machine learning", "ai", "sql", "python", "spark"],
        "Software": ["software", "frontend", "backend", "react", "java", "node", "golang"],
        "Business": ["business", "analyst", "consultant", "product"],
        "Marketing": ["marketing", "seo", "growth", "communication"],
    }
    blob = (f["title"].fillna("") + " " + f["description"].fillna("")).str.lower()
    mask = False
    for k in role_map[role]:
        mask = mask | blob.str.contains(k, na=False)
    f = f[mask]

# Free-text search
if search.strip():
    blob = (f["title"].fillna("") + " " + f["company"].fillna("")).str.lower()
    f = f[blob.str.contains(search.lower(), na=False)]

# Work mode filter (best-effort from location text)
if work_mode and set(work_mode) != {"Remote", "Hybrid", "On-site", "Unspecified"}:
    loc = f["location"].fillna("").str.lower()
    wm_mask = False
    if "Remote" in work_mode:
        wm_mask = wm_mask | loc.str.contains("remote")
    if "Hybrid" in work_mode:
        wm_mask = wm_mask | loc.str.contains("hybrid")
    if "On-site" in work_mode:
        wm_mask = wm_mask | (~loc.str.contains("remote") & ~loc.str.contains("hybrid") & (loc.str.len() > 0))
    if "Unspecified" in work_mode:
        wm_mask = wm_mask | (loc.str.len() == 0)
    f = f[wm_mask]

# ---------- METRICS ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Results", len(f))
c2.metric("Remote", int((f["location"].fillna("").str.contains("remote", case=False, na=False)).sum()))
c3.metric("Avg EnglishScore", int(f["english_score"].mean()) if len(f) else 0)
c4.metric("Internships", int((f["contract_type"] == "INTERNSHIP").sum()))

st.divider()

# Sort best-effort: newest-ish first using URL stability (no parsed_at column in DB)
# We'll just sort by english_score desc as a proxy; you can improve later by adding timestamps.
f_sorted = f.sort_values(["english_score"], ascending=False)

# ---------- JOB CARDS ----------
for _, r in f_sorted.head(30).iterrows():
    st.markdown(
        f"""
        <div class="job-card">
            <div class="job-title">{r['title']}</div>
            <div class="job-meta">{r['company']} • {r['location']} • {r['contract_type']}</div>
            <div style="display:flex;gap:8px;align-items:center;">
                <span class="badge">EnglishScore {int(r['english_score'])}</span>
                <span class="badge">{r['language']}</span>
                <a href="{r['url']}" target="_blank" style="margin-left:auto;">Open ↗</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

st.dataframe(
    f_sorted[["english_score", "contract_type", "title", "company", "location", "language", "url"]],
    use_container_width=True,
    column_config={"url": st.column_config.LinkColumn("Job link")},
)
