"""Explore-tab UI for historical training-product comparisons."""

from __future__ import annotations

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


def render_explore_page() -> None:
    page_heading(
        "Category intelligence",
        "Explore products",
        "Browse category data, compare historical review outcomes, and rank products with more context than star ratings alone.",
    )
    category = st.selectbox("Product category", list(CATEGORY_FILES), key="explore_category")
    catalog_tab, peers_tab = st.tabs(["Product catalog", "Historical peers"])
    with catalog_tab:
        render_product_catalog(category)
    with peers_tab:
        render_historical_peers(category)


def render_product_catalog(category: str) -> None:
    st.header(f"{category} product catalog")
    st.write("Search products by product name or ASIN and rank them fairly by rating quality and review volume.")
    category_catalog_path = catalog_path(category)
    if not category_catalog_path.exists():
        st.info(f"The {category} product catalog has not been built yet.")
        st.code("python scripts/build_category_assets.py", language="bash")
        return

    catalog = load_product_catalog(category, category_catalog_path.stat().st_mtime_ns)
    search, minimum_reviews, sort_by = st.columns([3, 1, 2])
    query = search.text_input("Search product name or ASIN", placeholder="e.g., vitamins or B07TDSJZMR")
    review_floor = minimum_reviews.number_input("Minimum reviews", min_value=0, value=10, step=10)
    sort_option = sort_by.selectbox(
        "Sort by",
        ["Weighted rating", "Average stars", "Review count", "Fastest early traction", "Sustained high ratings"],
    )

    filtered = catalog.loc[catalog["review_count"] >= review_floor].copy()
    if query:
        matches = (
            filtered["product_name"].str.contains(query, case=False, na=False)
            | filtered["parent_asin"].str.contains(query, case=False, na=False)
        )
        filtered = filtered.loc[matches]

    sort_column = {
        "Weighted rating": "weighted_rating",
        "Average stars": "average_stars",
        "Review count": "review_count",
        "Fastest early traction": "days_to_20",
        "Sustained high ratings": "sustained_rating",
    }[sort_option]
    if sort_option == "Fastest early traction":
        filtered = filtered.dropna(subset=["days_to_20"]).sort_values([sort_column, "review_count"], ascending=[True, False])
    elif sort_option == "Sustained high ratings":
        filtered = filtered.loc[
            filtered["recent_average_stars"].ge(4.5) & filtered["rating_change"].ge(-0.25)
        ].sort_values([sort_column, "review_count"], ascending=False)
    else:
        filtered = filtered.sort_values([sort_column, "review_count"], ascending=False)
    first, second, third = st.columns(3)
    first.metric("Matching products", f"{len(filtered):,}")
    second.metric("Category average", f"{catalog['average_stars'].mean():.2f}")
    third.metric("Ranking", "Weighted rating" if sort_option == "Weighted rating" else sort_option)
    descriptions = {
        "Weighted rating": "Weighted rating combines a product's average stars with its review count, pulling low-volume products toward the category average.",
        "Fastest early traction": "Products are ranked by the fewest days from their first observed review to their 20th review.",
        "Sustained high ratings": "Requires at least 40 reviews, a recent 20-review average of 4.5+, and no decline greater than 0.25 stars from the first 20 reviews.",
    }
    st.caption(descriptions.get(sort_option, "Products are ranked by the selected metric."))
    display_columns = ["product_name", "average_stars", "review_count", "weighted_rating"]
    if sort_option == "Fastest early traction":
        display_columns += ["days_to_20", "early_review_pace"]
    elif sort_option == "Sustained high ratings":
        display_columns += ["early_average_stars", "recent_average_stars", "rating_change", "sustained_rating"]
    display = filtered[display_columns].rename(
        columns={
            "product_name": "Product name",
            "average_stars": "Average stars",
            "review_count": "Reviews",
            "weighted_rating": "Weighted rating",
            "days_to_20": "Days to 20",
            "early_review_pace": "Early reviews / month",
            "early_average_stars": "First 20 stars",
            "recent_average_stars": "Recent 20 stars",
            "rating_change": "Rating change",
            "sustained_rating": "Sustained rating",
        }
    )
    catalog_column, explanation_column = st.columns([4, 1], gap="large")
    with catalog_column:
        st.subheader("Product catalog")
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            height=500,
            column_config={
                "Average stars": st.column_config.NumberColumn(format="%.2f"),
                "Weighted rating": st.column_config.NumberColumn(format="%.2f"),
                "Reviews": st.column_config.NumberColumn(format="%d"),
                "Days to 20": st.column_config.NumberColumn(format="%.0f"),
                "Early reviews / month": st.column_config.NumberColumn(format="%.1f"),
                "First 20 stars": st.column_config.NumberColumn(format="%.2f"),
                "Recent 20 stars": st.column_config.NumberColumn(format="%.2f"),
                "Rating change": st.column_config.NumberColumn(format="%+.2f"),
                "Sustained rating": st.column_config.NumberColumn(format="%.2f"),
            },
        )
    with explanation_column.container(border=True):
        st.subheader("How ranking works")
        st.write(
            "Weighted rating balances average stars with review volume, so a product with one five-star review does not lead the catalog."
        )


def render_historical_peers(category: str) -> None:
    st.header("Explore historical reviews")
    st.write(f"Find {category} products with early reviews like yours and compare their later review outcomes.")
    st.caption("This view uses historical training products. Comparisons are associations, not proof of cause and effect.")

    category_peer_path = peer_path(category)
    if not category_peer_path.exists():
        st.error(f"Historical data is missing: {category_peer_path.name}")
        return

    products = load_historical_peers(category, category_peer_path.stat().st_mtime_ns)
    filter_column, details_column = st.columns([2, 3], gap="large")
    with filter_column.container(border=True):
        st.subheader("Filter peer products")
        max_days = int(min(products["days_to_20"].max(), 2000))
        rating_range = st.slider("Early average stars", 1.0, 5.0, (3.5, 5.0), 0.1)
        days_range = st.slider("Days to reach 20 reviews", 0, max_days, (0, min(900, max_days)))
        profile_options = ["All review profiles"] + sorted(products["review_profile"].unique())
        profile = st.selectbox("Review profile", profile_options)

    peers = products[
        products["early_rating_mean"].between(*rating_range)
        & products["days_to_20"].between(*days_range)
    ]
    if profile != "All review profiles":
        peers = peers.loc[peers["review_profile"] == profile]

    count = len(peers)
    share = peers["is_successful"].mean() if count else None
    with details_column.container(border=True):
        st.subheader("Matching peer group")
        first, second = st.columns(2)
        first.metric("Products", f"{count:,}")
        second.metric("Observed success", f"{share:.1%}" if share is not None else "—")
        st.caption("Observed success uses the category's later-review volume threshold plus a 4.0+ later rating.")

    if not count:
        st.warning("No products match these filters. Broaden a range to view historical peers.")
        return

    st.subheader("Early reviews and later outcomes")
    chart = peers.rename(columns={"early_rating_mean": "Early stars", "days_to_20": "Days to 20"}).copy()
    chart["Later outcome"] = chart["is_successful"].map({1: "Met proxy", 0: "Did not meet proxy"})
    st.scatter_chart(chart, x="Days to 20", y="Early stars", color="Later outcome")

    st.subheader("Inspect a peer product")
    peer_labels = {
        row.parent_asin: f"{row.product_name} — {row.parent_asin}"
        for row in peers[["parent_asin", "product_name"]].itertuples(index=False)
    }
    selected_id = st.selectbox(
        "Select a product",
        peers["parent_asin"].sort_values().tolist(),
        format_func=peer_labels.get,
    )
    selected = peers.loc[peers["parent_asin"] == selected_id].iloc[0]
    product_column, outcome_column = st.columns(2)
    with product_column.container(border=True):
        st.markdown("**Early review signals**")
        st.write(f"Product: **{selected.product_name}**")
        st.write(f"Average stars: **{selected.early_rating_mean:.2f}**")
        st.write(f"Days to reach 20 reviews: **{selected.days_to_20:.0f}**")
        st.write(f"Low-star share: **{selected.early_low_rating_share:.0%}**")
        st.write(f"Review profile: **{selected.review_profile}**")
    with outcome_column.container(border=True):
        st.markdown("**Later observed outcome**")
        result = "Yes" if selected.is_successful else "No"
        st.write(f"Met review-success proxy: **{result}**")
        st.write(f"Later reviews in 365 days: **{selected.later_review_count_365d:.0f}**")
        later_rating = "No later reviews" if pd.isna(selected.later_rating_mean_365d) else f"{selected.later_rating_mean_365d:.2f}"
        st.write(f"Later average stars: **{later_rating}**")
        st.write(f"Last 20-review average: **{selected.last_20_rating_mean:.2f}**")

    st.subheader("Matching products")
    table = peers[
        ["product_name", "parent_asin", "early_rating_mean", "days_to_20", "later_review_count_365d", "last_20_rating_mean", "is_successful"]
    ].rename(
        columns={
            "product_name": "Product name",
            "parent_asin": "ASIN",
            "early_rating_mean": "Early rating",
            "days_to_20": "Days to 20",
            "later_review_count_365d": "Later reviews",
            "last_20_rating_mean": "Last 20 stars",
            "is_successful": "Observed success",
        }
    )
    st.dataframe(table, use_container_width=True, hide_index=True, height=350)
