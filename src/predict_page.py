"""Predict-tab UI. The trained model is intentionally added in Week 3."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_loader import CATEGORY_FILES, load_historical_peers, peer_path
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


def find_similar_products(reviews: pd.DataFrame, category: str, limit: int = 5) -> pd.DataFrame:
    """Rank category-matched historical products by first-20-review similarity."""
    comparison_path = peer_path(category)
    peers = load_historical_peers(category, comparison_path.stat().st_mtime_ns).copy()
    uploaded_stars = reviews["rating"].mean()
    uploaded_days = max((reviews["date"].max() - reviews["date"].min()).days, 0)
    uploaded_low_share = reviews["rating"].le(2).mean()

    rating_gap = ((peers["early_rating_mean"] - uploaded_stars).abs() / 0.50).clip(upper=1)
    time_gap = (
        (peers["days_to_20"].map(math.log1p) - math.log1p(uploaded_days)).abs() / math.log(2)
    ).clip(upper=1)
    low_star_gap = ((peers["early_low_rating_share"] - uploaded_low_share).abs() / 0.15).clip(upper=1)
    peers["similarity"] = 100 * (1 - 0.50 * rating_gap - 0.35 * time_gap - 0.15 * low_star_gap)
    return peers.sort_values(
        ["similarity", "later_review_count_365d"], ascending=[False, False]
    ).head(limit)


def render_similar_products(reviews: pd.DataFrame, category: str) -> None:
    """Show outcomes for the closest category-matched historical products."""
    if not peer_path(category).exists():
        st.info("Historical comparison data is not available for this category yet.")
        return
    peers = find_similar_products(reviews, category)
    if peers.empty:
        st.info("No historical products were available for comparison.")
        return

    st.subheader("Similar historical products")
    st.caption(
        "Matches use only the first 20 reviews: average stars, days to reach 20 reviews, and low-star share. "
        "Later outcomes are shown after matching, not used to select the products."
    )
    median_later_reviews = peers["later_review_count_365d"].median()
    median_later_stars = peers["later_rating_mean_365d"].median()
    first, second = st.columns(2)
    first.metric("Median later reviews", f"{median_later_reviews:.0f}")
    second.metric("Median later stars", f"{median_later_stars:.2f}" if pd.notna(median_later_stars) else "—")

    display = peers[
        [
            "product_name",
            "early_rating_mean",
            "days_to_20",
            "later_review_count_365d",
            "later_rating_mean_365d",
            "last_20_rating_mean",
        ]
    ].rename(
        columns={
            "product_name": "Similar product",
            "early_rating_mean": "First 20 stars",
            "days_to_20": "Days to 20",
            "later_review_count_365d": "Later reviews",
            "later_rating_mean_365d": "Later stars",
            "last_20_rating_mean": "Last 20 stars",
        }
    )
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "First 20 stars": st.column_config.NumberColumn(format="%.2f"),
            "Days to 20": st.column_config.NumberColumn(format="%.0f"),
            "Later reviews": st.column_config.NumberColumn(format="%d"),
            "Later stars": st.column_config.NumberColumn(format="%.2f"),
            "Last 20 stars": st.column_config.NumberColumn(format="%.2f"),
        },
    )


def render_predict_page() -> None:
    st.markdown('<div class="section-kicker">Review forecast</div>', unsafe_allow_html=True)
    st.header("Predict a product's review outlook")
    thumbnail_column, product_column = st.columns([1, 6], vertical_alignment="center")
    with thumbnail_column:
        st.image(str(EXAMPLE_THUMBNAIL), width=105)
    with product_column:
        st.subheader("Lavender Daily Moisturizer")
        st.caption("Example product - upload the complete first 20 reviews for one parent product.")

    category = st.selectbox(
        "Comparison category",
        list(CATEGORY_FILES),
        help="Your uploaded reviews will be compared only with products from this category.",
        key="predict_category",
    )

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

    render_similar_products(reviews, category)

    with st.expander("Preview uploaded reviews"):
        st.dataframe(reviews, use_container_width=True, hide_index=True)

