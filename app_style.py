import streamlit as st

def inject_css():
    st.markdown(
        """
<style>
/* =========================================================
   THEME VARIABLES (works for LIGHT + DARK automatically)
   ========================================================= */
:root {
  --bg: var(--background-color);
  --card: var(--secondary-background-color);
  --text: var(--text-color);
  --border: rgba(120,120,120,0.25);
  --input-bg: var(--secondary-background-color);
  --placeholder: rgba(120,120,120,0.9);
}

/* =========================================================
   PAGE LAYOUT
   ========================================================= */
.block-container {
  padding-top: 1.2rem;
  padding-bottom: 2rem;
  max-width: 1200px;
}

h1, h2, h3 {
  letter-spacing: -0.02em;
  color: var(--text);
}

/* =========================================================
   SIDEBAR
   ========================================================= */
section[data-testid="stSidebar"] {
  background-color: var(--card) !important;
  border-right: 1px solid var(--border) !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
  color: var(--text) !important;
}

/* =========================================================
   🔥 FIX: SEARCH INPUT / TEXT INPUT VISIBILITY
   ========================================================= */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
  background-color: var(--input-bg) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}

section[data-testid="stSidebar"] input::placeholder,
section[data-testid="stSidebar"] textarea::placeholder {
  color: var(--placeholder) !important;
}

/* =========================================================
   🔥 FIX: AUTOCOMPLETE / DROPDOWN (shows without click)
   ========================================================= */
div[role="listbox"],
div[data-baseweb="popover"] {
  background: var(--card) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
}

div[role="option"] {
  color: var(--text) !important;
}

/* =========================================================
   METRIC CARDS
   ========================================================= */
div[data-testid="stMetric"] {
  background: var(--card) !important;
  padding: 14px !important;
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
}

div[data-testid="stMetric"] * {
  color: var(--text) !important;
}

/* =========================================================
   DATAFRAME
   ========================================================= */
div[data-testid="stDataFrame"] {
  border-radius: 14px;
  border: 1px solid var(--border);
  overflow: hidden;
}

/* =========================================================
   JOB CARDS
   ========================================================= */
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
