"""Predict-tab UI. The trained model is intentionally added in Week 3."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.validation import validate_reviews


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_THUMBNAIL = ROOT / "assets" / "example_product_thumbnail.png"


def render_decision_card(predicted_success: bool, preview: bool = False) -> None:
    """Show the model's Boolean prediction as a clear Yes/No result."""
    label = "Yes" if predicted_success else "No"
    icon = "👍" if predicted_success else "👎"
    background = "#e8f5e9" if predicted_success else "#ffebee"
    text_color = "#1b5e20" if predicted_success else "#8b1e1e"
    st.markdown(
        f"""
        <div style="
            background: {background};
            border: 1px solid {text_color};
            border-radius: 12px;
            color: {text_color};
            padding: 24px;
            text-align: center;">
            <div style="font-size: 16px;">Expected to meet the review-success proxy?</div>
            <div style="font-size: 48px; margin: 10px 0;">{icon}</div>
            <div style="font-size: 42px; font-weight: 700;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if preview:
        st.warning(
            "Interface preview: this No result is illustrative until the trained model is connected."
        )
    st.caption(
        "The proxy is 24+ later reviews with an average later rating of at least 4.0, within 365 days."
    )


def csv_template() -> bytes:
    """Create a small template that documents the required upload format."""
    example = pd.DataFrame(
        {
            "rating": [5] * 20,
            "text": [f"Example review {number}" for number in range(1, 21)],
            "date": pd.date_range("2025-01-01", periods=20, freq="7D").strftime("%Y-%m-%d"),
            "verified_purchase": ["True"] * 20,
        }
    )
    return example.to_csv(index=False).encode("utf-8")


def render_predict_page() -> None:
    st.header("Predict a product's review outlook")
    thumbnail_column, product_column = st.columns([1, 6], vertical_alignment="center")
    with thumbnail_column:
        st.image(str(EXAMPLE_THUMBNAIL), width=105)
    with product_column:
        st.subheader("Lavender Daily Moisturizer")
        st.caption("Example product - upload the complete first 20 reviews for one parent product.")

    st.download_button(
        "Download CSV template",
        data=csv_template(),
        file_name="first_20_reviews_template.csv",
        mime="text/csv",
    )
    uploaded_file = st.file_uploader(
        "Drag and drop the first_20_reviews.csv here, or click Browse files",
        type=["csv"],
        help="Required columns: rating, text, date, verified_purchase.",
    )

    if uploaded_file is None:
        st.info("Required fields: rating, text, date, verified_purchase. Upload exactly 20 reviews.")
        return

    try:
        reviews = pd.read_csv(uploaded_file)
    except (UnicodeDecodeError, pd.errors.ParserError) as error:
        st.error(f"This CSV could not be read: {error}")
        return

    reviews, errors = validate_reviews(reviews)
    if errors:
        for error in errors:
            st.error(error)
        return

    st.success("20 / 20 valid reviews received. The file is ready for the model pipeline.")
    summary_column, result_column = st.columns([3, 2], gap="large")
    star_counts = reviews["rating"].value_counts().reindex([5, 4, 3, 2, 1], fill_value=0)

    with summary_column.container(border=True):
        st.subheader("Early review summary")
        first, second = st.columns(2)
        first.metric("Average stars", f"{reviews['rating'].mean():.2f}")
        second.metric("Days to review 20", f"{(reviews['date'].max() - reviews['date'].min()).days} days")
        st.markdown("**Star-rating breakdown**")
        stars = st.columns(5)
        for column, star in zip(stars, [5, 4, 3, 2, 1]):
            column.metric(f"{'★' * star}", star_counts[star])

    with result_column.container(border=True):
        st.subheader("Model result")
        # Week 3: replace False with the model's Boolean class prediction.
        render_decision_card(predicted_success=False, preview=True)

    with st.expander("Preview uploaded reviews"):
        st.dataframe(reviews, use_container_width=True, hide_index=True)

