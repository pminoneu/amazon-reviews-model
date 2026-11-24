import streamlit as st

from src.explore_page import render_explore_page
from src.predict_page import render_predict_page
from src.styles import apply_app_styles


st.set_page_config(page_title="Review Outlook", page_icon="⭐", layout="wide")
apply_app_styles()

if "active_page" not in st.session_state:
    st.session_state.active_page = "Predict"

with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
          <div class="brand-mark"><span></span><span></span><span></span></div>
          <div class="brand-name">Review Outlook</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.active_page == "Predict":
        st.markdown('<div class="sidebar-nav-active">✦&nbsp;&nbsp; Predict</div>', unsafe_allow_html=True)
        if st.button("⌕  Explore", key="go_to_explore", use_container_width=True):
            st.session_state.active_page = "Explore"
            st.rerun()
    else:
        if st.button("✦  Predict", key="go_to_predict", use_container_width=True):
            st.session_state.active_page = "Predict"
            st.rerun()
        st.markdown('<div class="sidebar-nav-active">⌕&nbsp;&nbsp; Explore</div>', unsafe_allow_html=True)
if st.session_state.active_page == "Predict":
    render_predict_page()
else:
    render_explore_page()
