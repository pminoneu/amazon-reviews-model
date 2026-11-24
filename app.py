import streamlit as st

from src.explore_page import render_explore_page
from src.predict_page import render_predict_page


st.set_page_config(page_title="Review Outlook", page_icon="⭐", layout="wide")
st.title("⭐ Review Outlook")
st.caption("Early Product Success | Amazon All Beauty reviews")

predict, explore = st.tabs(["Predict", "Explore"])

with predict:
    render_predict_page()

with explore:
    render_explore_page()
