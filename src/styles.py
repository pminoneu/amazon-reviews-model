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
            --canvas: #ffffff;
            --ink: #17172a;
            --muted: #50586a;
            --border: #c8cfdb;
          }
          .stApp, [data-testid="stAppViewContainer"] { background: var(--canvas); color: var(--ink); }
          [data-testid="stHeader"] { background: transparent; }
          .block-container { max-width: 1400px; padding: 1.55rem 2.35rem 3rem; }
          [data-testid="stSidebar"], section[data-testid="stSidebar"] {
            background: var(--navy); min-width: 245px !important; max-width: 245px !important; width: 245px !important;
          }
          [data-testid="stSidebarResizeHandle"], [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"] { display:none !important; }
          [data-testid="stSidebar"] * { color: #f8f9ff; }
          [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #d0d4e8; }
          [data-testid="stSidebar"] .stButton > button {
            background: transparent !important; color: #f8f9ff !important; border: 0 !important; box-shadow: none !important;
            border-radius: 10px !important; font-weight: 650 !important; justify-content: flex-start !important; padding: .7rem .8rem !important;
          }
          [data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,.10) !important; }
          .sidebar-nav-active { background: #403a96; color: white; border-radius: 10px; font-weight: 700; padding: .7rem .8rem; margin: .2rem 0; }
          .brand-lockup { display:flex; align-items:center; gap:.75rem; margin:.55rem .15rem 3.1rem; }
          .brand-mark { display:flex; align-items:end; gap:3px; height:28px; }
          .brand-mark span { display:block; width:7px; border-radius:7px; background:#27c6e5; }
          .brand-mark span:nth-child(1) { height:11px; } .brand-mark span:nth-child(2) { height:20px; } .brand-mark span:nth-child(3) { height:28px; }
          .brand-name { color:white; font-size:1.22rem; font-weight:760; letter-spacing:-.03em; }
          .page-heading { border-left:7px solid var(--cyan); padding-left:1rem; margin:.1rem 0 1.65rem; }
          .page-title { color:var(--ink); font-size:2.18rem; line-height:1.12; font-weight:760; letter-spacing:-.045em; margin:0; }
          .page-subtitle { color:var(--muted); font-size:1rem; margin:.35rem 0 0; }
          .product-identity { display:flex; align-items:center; gap:1rem; padding:.2rem 0 1.1rem; }
          .product-identity h3 { margin:0; color:var(--ink); font-size:1.2rem; }
          .category-chip { display:inline-block; color:#007f9b; background:#dff8fc; border-radius:999px; font-size:.78rem; font-weight:700; padding:.28rem .7rem; margin-top:.32rem; }
          .review-summary-card, .outlook-card { height:100%; min-height:190px; box-sizing:border-box; border:1px solid var(--border); border-radius:14px; background:white; padding:1.1rem 1.2rem; }
          .review-summary-card h3, .outlook-title { color:var(--ink); font-size:1.22rem; font-weight:760; letter-spacing:-.025em; margin:0 0 1rem; }
          .summary-content { display:grid; grid-template-columns:1fr 1fr 1.35fr; gap:.85rem; align-items:stretch; }
          .summary-metric { background:#f2f5f9; border-radius:11px; padding:.85rem .9rem; display:flex; flex-direction:column; justify-content:space-between; min-height:90px; }
          .summary-metric span { color:var(--muted); font-size:.76rem; font-weight:650; }
          .summary-metric strong { color:var(--ink); font-size:2.2rem; line-height:1; letter-spacing:-.06em; }
          .rating-breakdown { border-left:1px solid var(--border); padding:.1rem 0 .1rem .9rem; }
          .rating-row { display:grid; grid-template-columns:28px 1fr 18px; align-items:center; gap:.42rem; color:var(--muted); font-size:.76rem; font-weight:650; margin:.34rem 0; }
          .rating-track { height:8px; border-radius:999px; background:#e2e8ef; overflow:hidden; }
          .rating-fill { display:block; height:100%; border-radius:999px; background:var(--cyan); }
          .outlook-card { text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; }
          .outlook-title { align-self:flex-start; margin-bottom:.7rem; }
          .outlook-result { display:flex; align-items:center; justify-content:center; gap:1rem; }
          .outlook-result span { display:grid; place-items:center; width:70px; height:70px; border-radius:18px; font-size:2.45rem; }
          .outlook-result strong { font-size:3.2rem; letter-spacing:-.06em; }
          .outlook-card p { color:var(--muted); font-size:.77rem; margin:.55rem 0 0; }
          .outlook-preview { color:var(--muted); font-size:.67rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; margin-top:.3rem; }
          .outlook-positive .outlook-result span { background:#e3f5e7; } .outlook-positive .outlook-result strong { color:#14833c; }
          .outlook-negative .outlook-result span { background:#fde7e8; } .outlook-negative .outlook-result strong { color:#bd3041; }
          h2, h3 { color:var(--ink); letter-spacing:-.025em; }
          h2 { font-size:1.28rem !important; margin-top:.3rem; }
          [data-testid="stMetric"] { background:white; border:1px solid var(--border); border-radius:13px; padding:.9rem 1rem; box-shadow:none; }
          [data-testid="stMetricLabel"] { color:var(--muted); font-size:.76rem; font-weight:650; }
          [data-testid="stMetricValue"] { color:var(--ink); font-weight:760; letter-spacing:-.03em; }
          [data-testid="stVerticalBlockBorderWrapper"] { border:1px solid var(--border) !important; border-radius:14px !important; background:white; box-shadow:none; }
          [data-testid="stFileUploader"] { background:#fbfdff; border:1.5px dashed #96c2d0; border-radius:14px; padding:1.4rem .6rem; }
          [data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:13px; overflow:hidden; background:white; }
          [data-testid="stExpander"] { border:1px solid var(--border); border-radius:12px; background:white; }
          [data-baseweb="tab-list"] { gap:1.45rem; border-bottom:1px solid var(--border); }
          [data-baseweb="tab"] { color:var(--muted); font-weight:650; padding:.6rem .05rem; }
          [data-baseweb="tab-highlight"] { background:var(--cyan) !important; height:3px !important; }
          .stButton > button, .stDownloadButton > button { background:var(--navy); color:white; border:0; border-radius:9px; font-weight:700; }
          .stButton > button:hover, .stDownloadButton > button:hover { background:var(--navy-2); color:white; border:0; }
          [data-testid="stSelectbox"] > div > div, [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input { border-color:#aeb8c9; border-radius:9px; background:white; }
          [data-testid="stAlert"] { border-radius:11px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_heading(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="page-heading"><div class="page-title">{title}</div><div class="page-subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )
