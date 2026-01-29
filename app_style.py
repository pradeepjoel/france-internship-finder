import streamlit as st

def inject_css():
    st.markdown(
        """
<style>
/* Use Streamlit theme variables so it works in LIGHT + DARK mode */
:root {
  --bg: var(--background-color);
  --card: var(--secondary-background-color);
  --text: var(--text-color);
  --border: rgba(120,120,120,0.25);
}

/* Page width & spacing */
.block-container {
  padding-top: 1.2rem;
  padding-bottom: 2rem;
  max-width: 1200px;
}
h1, h2, h3 { letter-spacing: -0.02em; color: var(--text); }

/* Sidebar */
section[data-testid="stSidebar"] {
  background-color: var(--card) !important;
  border-right: 1px solid var(--border) !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
  background: var(--card) !important;
  padding: 14px !important;
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
}
div[data-testid="stMetric"] * { color: var(--text) !important; }

/* Dataframe wrapper */
div[data-testid="stDataFrame"] {
  border-radius: 14px;
  border: 1px solid var(--border);
  overflow: hidden;
}

/* Job cards */
.job-card {
  padding: 14px 16px;
  border-radius: 16px;
  background: var(--card);
  border: 1px solid var(--border);
  margin-bottom: 12px;
  color: var(--text);
}
.job-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--text);
}
.job-meta {
  opacity: 0.85;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text);
}
.badge {
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  font-size: 12px;
  color: var(--text);
}
</style>
        """,
        unsafe_allow_html=True
    )
