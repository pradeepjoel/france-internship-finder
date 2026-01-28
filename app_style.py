import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    /* Page width & spacing */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Headings */
    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0B0F14;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: #111827;
        padding: 14px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        overflow: hidden;
    }

    /* Job cards */
    .job-card {
        padding: 14px 16px;
        border-radius: 16px;
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 12px;
    }

    .job-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .job-meta {
        opacity: 0.85;
        margin-bottom: 8px;
        font-size: 14px;
    }

    .badge {
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.15);
        font-size: 12px;
    }

    </style>
    """, unsafe_allow_html=True)
