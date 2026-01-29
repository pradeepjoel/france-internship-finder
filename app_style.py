import streamlit as st

def inject_css():
    st.markdown("""
    <style>

    /* ===============================
       Base layout
    =============================== */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    /* ===============================
       LIGHT MODE
    =============================== */
    [data-theme="light"] section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    [data-theme="light"] div[data-testid="stMetric"] {
        background: #ffffff;
        color: #111827;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 14px;
    }

    [data-theme="light"] .job-card {
        background: #ffffff;
        color: #111827;
        border: 1px solid #e5e7eb;
       
