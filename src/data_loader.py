"""Historical data access for the Explore screen."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_FEATURES_PATH = ROOT / "results" / "product_features.csv"


@st.cache_data(show_spinner="Loading historical products...")
def load_training_products() -> pd.DataFrame:
    """Load the historical training cohort used by the Explore tab."""
    columns = [
        "parent_asin",
        "cutoff_utc",
        "early_rating_mean",
        "days_to_20",
        "early_verified_share",
        "early_low_rating_share",
        "early_text",
        "later_review_count_365d",
        "later_rating_mean_365d",
        "is_successful",
        "split",
    ]
    products = pd.read_csv(PRODUCT_FEATURES_PATH, usecols=columns)
    products = products.loc[products["split"] == "train"].copy()
    products["early_text"] = products["early_text"].fillna("")
    products["review_profile"] = products.apply(review_profile, axis=1)
    return products


def review_profile(product: pd.Series) -> str:
    """Create a transparent grouping for browsing peers, not a model prediction."""
    if product["early_low_rating_share"] >= 0.20:
        return "Frequent low-star feedback"
    if product["early_rating_mean"] >= 4.50:
        return "Very positive early reviews"
    if product["early_rating_mean"] >= 3.50:
        return "Mixed early reviews"
    return "Mostly negative early reviews"
