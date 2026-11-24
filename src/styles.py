"""Shared visual treatment for the Streamlit dashboard."""

from __future__ import annotations

import streamlit as st


def apply_dashboard_styles() -> None:
    """Apply the indigo-and-cyan dashboard design used throughout the app."""
    st.markdown(
        """
        <style>
            :root {
                --ink: #28205d;
                --ink-soft: #463d82;
                --cyan: #42b9e8;
                --magenta: #e15ac6;
                --canvas: #f5f6fb;
                --line: #e5e7f2;
            }
            .stApp, [data-testid="stAppViewContainer"] { background: var(--canvas); }
            [data-testid="stHeader"] { background: transparent; }
            .block-container { max-width: 1360px; padding-top: 1.75rem; padding-bottom: 3rem; }
            h1, h2, h3 { color: var(--ink); letter-spacing: -0.025em; }
            h2 { font-size: 1.55rem !important; }
            .dashboard-hero {
                background: linear-gradient(118deg, #28205d 0%, #3d347d 70%, #42b9e8 155%);
                border-radius: 22px;
                color: white;
                padding: 1.65rem 2rem;
                margin: 0 0 1.35rem 0;
                box-shadow: 0 16px 32px rgba(40, 32, 93, 0.16);
            }
            .dashboard-hero__eyebrow { color: #87dcfa; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.11em; text-transform: uppercase; }
            .dashboard-hero h1 { color: white; font-size: 2.2rem !important; margin: 0.25rem 0 0.35rem; }
            .dashboard-hero p { color: #e4e8ff; font-size: 1rem; margin: 0; }
            .section-kicker { color: var(--cyan); font-size: 0.75rem; font-weight: 750; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .25rem; }
            [data-baseweb="tab-list"] { gap: 1.6rem; border-bottom: 1px solid var(--line); }
            [data-baseweb="tab"] { color: #74768d; font-size: .94rem; font-weight: 650; padding: .75rem .15rem; }
            [data-baseweb="tab"]:hover { color: var(--ink); }
            [data-baseweb="tab-highlight"] { background-color: var(--cyan) !important; height: 3px !important; }
            [data-testid="stMetric"] {
                background: white;
                border: 1px solid var(--line);
                border-radius: 15px;
                padding: .85rem 1rem;
                box-shadow: 0 5px 14px rgba(33, 29, 78, .055);
            }
            [data-testid="stMetricLabel"] { color: #74768d; font-size: .76rem; font-weight: 650; }
            [data-testid="stMetricValue"] { color: var(--ink); font-weight: 750; }
            [data-testid="stFileUploader"] {
                background: white;
                border: 1.5px dashed #8ed9f2;
                border-radius: 15px;
                padding: .4rem;
            }
            [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 15px; overflow: hidden; background: white; }
            [data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 14px; background: white; }
            [data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--line) !important; border-radius: 15px !important; background: white; box-shadow: 0 5px 14px rgba(33, 29, 78, .045); }
            .stButton > button, .stDownloadButton > button {
                border-radius: 10px; border: 0; background: var(--ink); color: white; font-weight: 650;
            }
            .stButton > button:hover, .stDownloadButton > button:hover { background: var(--ink-soft); color: white; border: 0; }
            [data-testid="stSelectbox"] > div > div, [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
                background: white; border-color: var(--line); border-radius: 10px;
            }
            div[data-testid="stAlert"] { border-radius: 12px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
