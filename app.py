import pandas as pd
import streamlit as st
import re

from src.db import init_db, conn
from app_style import inject_css

st.set_page_config(page_title="France Internship Finder", layout="wide")
inject_css()
init_db()

st.title("🇫🇷 Internship Finder (France)")
st.caption("Internships & Alternance • English-friendly • France")

@st.cache_data(ttl=120)
def load_df():
    with conn() as c:
        return pd.read_sql_query("""
            SELECT
                s.title, s.company, s.location, s.url,
                s.description,
                g.language, g.english_score, g.contract_type, g.is_target,
                s.parsed_at
            FROM silver_jobs s
            JOIN gold_jobs g ON g.url = s.url
            WHERE g.is_target = 1
            ORDER BY s.parsed_at DESC
        """, c)

df = load_df()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Filters")

    mode = st.radio(
        "Mode",
        ["All internships/alternance", "English-friendly only"],
        index=0
    )

    min_score = 0 if mode == "All internships/alternance" else 40
    min_score = st.slider("Min EnglishScore", 0, 100, min_score)

    role = st.radio(
        "Role",
        ["All", "Data & AI", "Software", "Business", "Marketing"]
    )

    search = st.text_input("Search keywords")

    work_mode = st.multiselect(
        "Work mode",
        ["Remote", "Hybrid", "On-site", "Unspecified"],
        default=["Remote", "Hybrid", "On-site", "Unspecified"]
    )

# ---------- FILTERING ----------
f = df.copy()
f = f[f["english_score"] >= min_score]

if role != "All":
    role_map = {
        "Data & AI": ["data", "ml", "machine", "ai", "sql", "python"],
        "Software": ["software", "frontend", "backend", "react", "java"],
        "Business": ["business", "analyst", "consultant"],
        "Marketing": ["marketing", "seo", "growth"]
    }
    blob = (f["title"] + " " + f["description"]).str.lower()
    mask = False
    for k in role_map[role]:
        mask = mask | blob.str.contains(k, na=False)
    f = f[mask]

if search.strip():
    blob = (f["title"] + " " + f["company"]).str.lower()
    f = f[blob.str.contains(search.lower(), na=False)]

# ---------- METRICS ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Results", len(f))
c2.metric("Remote", int((f["location"].str.contains("remote", case=False, na=False)).sum()))
c3.metric("Avg EnglishScore", int(f["english_score"].mean()) if len(f) else 0)
c4.metric("Internships", int((f["contract_type"]=="INTERNSHIP").sum()))

st.divider()

# ---------- JOB CARDS ----------
for _, r in f.head(30).iterrows():
    st.markdown(f"""
    <div class="job-card">
        <div class="job-title">{r['title']}</div>
        <div class="job-meta">{r['company']} • {r['location']} • {r['contract_type']}</div>
        <div style="display:flex;gap:8px;align-items:center;">
            <span class="badge">EnglishScore {r['english_score']}</span>
            <span class="badge">{r['language']}</span>
            <a href="{r['url']}" target="_blank" style="margin-left:auto;">Open ↗</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.dataframe(
    f[["english_score","contract_type","title","company","location","language","url"]],
    use_container_width=True,
    column_config={"url": st.column_config.LinkColumn("Job link")}
)
