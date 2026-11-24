"""Predict-tab UI. The trained model is intentionally added in Week 3."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_loader import (
    CATEGORY_FILES,
    catalog_path,
    load_historical_peers,
    load_product_catalog,
    peer_path,
)
from src.styles import page_heading
from src.validation import validate_reviews


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_THUMBNAIL = ROOT / "assets" / "example_product_thumbnail.png"


def render_decision_card(predicted_success: bool, preview: bool = False) -> None:
    """Show the model's Boolean prediction as a clear Yes/No result."""
    label = "Yes" if predicted_success else "No"
    icon = "👍" if predicted_success else "👎"
    status_class = "outlook-positive" if predicted_success else "outlook-negative"
    preview_label = '<div class="outlook-preview">Model preview</div>' if preview else ""
    st.markdown(
        f"""
        <section class="outlook-card {status_class}">
            <div class="outlook-title">Outlook</div>
            <div class="outlook-result"><span>{icon}</span><strong>{label}</strong></div>
            {preview_label}
            <p>Expected to meet the review-success proxy</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_review_summary(reviews: pd.DataFrame) -> None:
    """Render the mockup-style summary panel after a valid upload."""
    average_stars = reviews["rating"].mean()
    days_to_20 = (reviews["date"].max() - reviews["date"].min()).days
    star_counts = reviews["rating"].value_counts().reindex([5, 4, 3, 2, 1], fill_value=0)
    breakdown = "".join(
        f'''
        <div class="rating-row">
          <span>{star} ★</span>
          <span class="rating-track"><span class="rating-fill" style="width: {count / len(reviews) * 100:.0f}%"></span></span>
          <span>{count}</span>
        </div>
        '''
        for star, count in star_counts.items()
    )
    st.markdown(
        f"""
        <section class="review-summary-card">
          <h3>Early review summary</h3>
          <div class="summary-content">
            <div class="summary-metric"><span>Average stars</span><strong>{average_stars:.2f}</strong></div>
            <div class="summary-metric"><span>Days to 20 reviews</span><strong>{days_to_20}</strong></div>
            <div class="rating-breakdown">{breakdown}</div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def csv_template() -> bytes:
    """Create a small template that documents the required upload format."""
    example = pd.DataFrame(
        {
            "parent_asin": ["B00YQ6X8EO"] * 20,
            "rating": [5] * 20,
            "text": [f"Example review {number}" for number in range(1, 21)],
            "date": pd.date_range("2025-01-01", periods=20, freq="7D").strftime("%Y-%m-%d"),
            "verified_purchase": ["True"] * 20,
        }
    )
    return example.to_csv(index=False).encode("utf-8")


def resolve_uploaded_product(reviews: pd.DataFrame) -> tuple[str, str]:
    """Find the uploaded product's name and category from its parent ASIN."""
    parent_asin = reviews["parent_asin"].iloc[0]
    matches: list[tuple[str, str]] = []
    for category in CATEGORY_FILES:
        source_path = catalog_path(category)
        catalog = load_product_catalog(category, source_path.stat().st_mtime_ns)
        product = catalog.loc[catalog["parent_asin"] == parent_asin, "product_name"]
        if not product.empty:
            matches.append((category, product.iloc[0]))
    if not matches:
        raise ValueError(
            f"{parent_asin} was not found in the supported Health & Personal Care or All Beauty catalogs."
        )
    category, product_name = matches[0]
    return category, product_name


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
    closest_candidates = peers.sort_values(
        ["similarity", "later_review_count_365d"], ascending=[False, False]
    ).head(25)
    return closest_candidates.sort_values(
        ["last_20_rating_mean", "later_review_count_365d"], ascending=[False, False]
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
        "The five closest matches are then ordered by their current star rating."
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
            "last_20_rating_mean": "Current stars",
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
            "Current stars": st.column_config.NumberColumn(format="%.2f"),
        },
    )


def render_predict_page() -> None:
    page_heading(
        "Review forecast",
        "Predict review outlook",
        "Upload the first 20 reviews for one product to see its early signals and comparable historical outcomes.",
    )
    uploaded_product = st.session_state.get(
        "uploaded_product",
        {"name": "Product identified from upload", "category": "Category detected automatically"},
    )
    thumbnail_column, product_column = st.columns([1, 6], vertical_alignment="center")
    with thumbnail_column:
        st.image(str(EXAMPLE_THUMBNAIL), width=105)
    with product_column:
        st.markdown(
            f'<div class="product-identity"><div><h3>{uploaded_product["name"]}</h3><span class="category-chip">{uploaded_product["category"]}</span></div></div>',
            unsafe_allow_html=True,
        )

    uploaded_file = st.file_uploader(
        "Upload first_20_reviews.csv",
        type=["csv"],
        help="Required columns: parent_asin (or asin), rating, text, date, verified_purchase.",
    )
    _, template_column, _ = st.columns([2, 1.2, 2])
    with template_column:
        st.download_button(
            "Download template",
            data=csv_template(),
            file_name="first_20_reviews_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if uploaded_file is None:
        st.info("Required fields: parent_asin (or asin), rating, text, date, verified_purchase. Upload exactly 20 reviews.")
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

    try:
        category, product_name = resolve_uploaded_product(reviews)
    except ValueError as error:
        st.error(str(error))
        return
    resolved_product = {"name": product_name, "category": category}
    if st.session_state.get("uploaded_product") != resolved_product:
        st.session_state.uploaded_product = resolved_product
        st.rerun()

    st.success("20 / 20 valid reviews received.")
    summary_column, result_column = st.columns([3, 2], gap="large")

    with summary_column:
        render_review_summary(reviews)

    with result_column:
        # Week 3: replace False with the model's Boolean class prediction.
        render_decision_card(predicted_success=False, preview=True)

    render_similar_products(reviews, category)

    with st.expander("Preview uploaded reviews"):
        st.dataframe(reviews, use_container_width=True, hide_index=True)

