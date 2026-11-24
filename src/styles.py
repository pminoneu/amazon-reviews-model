"""Shared presentation helpers for the Review Outlook dashboard."""

from __future__ import annotations

import streamlit as st


def apply_app_styles() -> None:
    """Apply a restrained analytics-dashboard visual system."""
    st.markdown(
        """
        <style>
          :root {
            --navy: #1d1a56;
            --navy-2: #302b7c;
            --cyan: #18bfdc;
            --canvas: #f8f9fc;
            --ink: #17172a;
            --muted: #6e7185;
            --border: #e3e6ef;
          }
          .stApp, [data-testid="stAppViewContainer"] { background: var(--canvas); color: var(--ink); }
          [data-testid="stHeader"] { background: transparent; }
          .block-container { max-width: 1400px; padding: 2.1rem 2.35rem 3rem; }
          [data-testid="stSidebar"] { background: var(--navy); min-width: 235px; }
          [data-testid="stSidebar"] * { color: #f8f9ff; }
          [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #c8c8e5; }
          [data-testid="stSidebar"] [data-testid="stRadio"] label {
            border-radius: 10px; padding: .52rem .7rem; margin: .2rem 0; transition: background .15s ease;
          }
          [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: rgba(255,255,255,.09); }
          [data-testid="stSidebar"] [data-testid="stRadio"] input { accent-color: var(--cyan); }
          .brand-lockup { display:flex; align-items:center; gap:.75rem; margin:.4rem 0 2.4rem; }
          .brand-mark { display:flex; align-items:end; gap:3px; height:28px; }
          .brand-mark span { display:block; width:7px; border-radius:7px; background:#27c6e5; }
          .brand-mark span:nth-child(1) { height:11px; } .brand-mark span:nth-child(2) { height:20px; } .brand-mark span:nth-child(3) { height:28px; }
          .brand-name { color:white; font-size:1.22rem; font-weight:760; letter-spacing:-.03em; }
          .nav-caption { color:#9e9bc9 !important; text-transform:uppercase; letter-spacing:.1em; font-size:.68rem; font-weight:700; margin-bottom:.35rem; }
          .page-eyebrow { color:#00a9ca; font-size:.72rem; font-weight:750; letter-spacing:.1em; text-transform:uppercase; margin-bottom:.3rem; }
          .page-title { color:var(--ink); font-size:2.1rem; line-height:1.12; font-weight:760; letter-spacing:-.045em; margin:0; }
          .page-subtitle { color:var(--muted); font-size:1rem; margin:.45rem 0 1.65rem; }
          .product-identity { display:flex; align-items:center; gap:1rem; padding:.75rem 0 1.1rem; }
          .product-identity h3 { margin:0; color:var(--ink); font-size:1.2rem; }
          .category-chip { display:inline-block; color:#007f9b; background:#dff8fc; border-radius:999px; font-size:.78rem; font-weight:700; padding:.28rem .7rem; margin-top:.32rem; }
          h2, h3 { color:var(--ink); letter-spacing:-.025em; }
          h2 { font-size:1.28rem !important; margin-top:.3rem; }
          [data-testid="stMetric"] { background:white; border:1px solid var(--border); border-radius:13px; padding:.9rem 1rem; box-shadow:0 4px 12px rgba(27, 25, 73, .035); }
          [data-testid="stMetricLabel"] { color:var(--muted); font-size:.76rem; font-weight:650; }
          [data-testid="stMetricValue"] { color:var(--ink); font-weight:760; letter-spacing:-.03em; }
          [data-testid="stVerticalBlockBorderWrapper"] { border:1px solid var(--border) !important; border-radius:14px !important; background:white; box-shadow:0 4px 12px rgba(27, 25, 73, .025); }
          [data-testid="stFileUploader"] { background:white; border:1.5px dashed #9adfed; border-radius:14px; padding:1.05rem .6rem; }
          [data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:13px; overflow:hidden; background:white; }
          [data-testid="stExpander"] { border:1px solid var(--border); border-radius:12px; background:white; }
          [data-baseweb="tab-list"] { gap:1.45rem; border-bottom:1px solid var(--border); }
          [data-baseweb="tab"] { color:var(--muted); font-weight:650; padding:.6rem .05rem; }
          [data-baseweb="tab-highlight"] { background:var(--cyan) !important; height:3px !important; }
          .stButton > button, .stDownloadButton > button { background:var(--navy); color:white; border:0; border-radius:9px; font-weight:700; }
          .stButton > button:hover, .stDownloadButton > button:hover { background:var(--navy-2); color:white; border:0; }
          [data-testid="stSelectbox"] > div > div, [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input { border-color:var(--border); border-radius:9px; background:white; }
          [data-testid="stAlert"] { border-radius:11px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_heading(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="page-eyebrow">{eyebrow}</div><div class="page-title">{title}</div><div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )
