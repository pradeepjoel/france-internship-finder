import streamlit as st

def inject_css():
    st.markdown(
        """
<style>
/* Page width & spacing */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
h1, h2, h3 { letter-spacing: -0.02em; }

/* ---------- DARK DEFAULT (works even if user doesn't set theme) ---------- */
section[data-testid="stSidebar"] {
    background-color: #0B0F14;
    border-right: 1px solid rgba(255,255,255,0.06);
}
div[data-testid="stMetric"] {
    background: #111827;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
}
div[data-testid="stDataFrame"] {
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    overflow: hidden;
}
.job-card {
    padding: 14px 16px;
    border-radius: 16px;
    background: #111827;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 12px;
}
.job-title { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.job-meta  { opacity: 0.85; margin-bottom: 8px; font-size: 14px; }
.badge {
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.15);
    font-size: 12px;
}

/* ---------- LIGHT MODE FIX (so light-mode users can read your UI) ---------- */
@media (prefers-color-scheme: light) {
  section[data-testid="stSidebar"] {
      background-color: #F8FAFC !important;
      border-right: 1px solid rgba(0,0,0,0.08) !important;
  }
  div[data-testid="stMetric"] {
      background: #FFFFFF !important;
      border: 1px solid rgba(0,0,0,0.10) !important;
  }
  div[data-testid="stDataFrame"] {
      border: 1px solid rgba(0,0,0,0.10) !important;
  }
  .job-card {
      background: #FFFFFF !important;
      border: 1px solid rgba(0,0,0,0.10) !important;
  }
  .job-meta { opacity: 0.9 !important; }
  .badge { border: 1px solid rgba(0,0,0,0.18) !important; }
}
</style>
        """,
        unsafe_allow_html=True
    )
