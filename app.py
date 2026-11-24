import streamlit as st

from src.explore_page import render_explore_page
from src.predict_page import render_predict_page
from src.styles import apply_dashboard_styles


st.set_page_config(page_title="Review Outlook", page_icon="⭐", layout="wide")
apply_dashboard_styles()
st.markdown(
    """
    <section class="dashboard-hero">
        <div class="dashboard-hero__eyebrow">Amazon review intelligence</div>
        <h1>Review Outlook</h1>
        <p>Understand early product traction, compare historical peers, and make the next review signal easier to act on.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

predict, explore = st.tabs(["Predict", "Explore"])

with predict:
    render_predict_page()

with explore:
    render_explore_page()
