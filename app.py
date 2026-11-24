import streamlit as st

from src.explore_page import render_explore_page
from src.predict_page import render_predict_page
from src.styles import apply_app_styles


st.set_page_config(page_title="Review Outlook", page_icon="⭐", layout="wide")
apply_app_styles()

with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
          <div class="brand-mark"><span></span><span></span><span></span></div>
          <div class="brand-name">Review Outlook</div>
        </div>
        <div class="nav-caption">Workspace</div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio("Navigation", ["Predict", "Explore"], label_visibility="collapsed")
    st.markdown("<br><p>Early review signals, historical peers, and category-level product discovery.</p>", unsafe_allow_html=True)

if page == "Predict":
    render_predict_page()
else:
    render_explore_page()
