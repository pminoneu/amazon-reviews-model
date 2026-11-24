"""Category-specific historical data access for the Streamlit app."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
CATEGORY_FILES = {
    "Health & Personal Care": {
        "catalog": ROOT / "results" / "health_product_catalog.csv",
        "peers": ROOT / "results" / "health_peer_products.csv",
    },
    "All Beauty": {
        "catalog": ROOT / "results" / "beauty_product_catalog.csv",
        "peers": ROOT / "results" / "beauty_peer_products.csv",
    },
}


def catalog_path(category: str) -> Path:
    return CATEGORY_FILES[category]["catalog"]


def peer_path(category: str) -> Path:
    return CATEGORY_FILES[category]["peers"]


@st.cache_data(show_spinner="Loading product catalog...")
def load_product_catalog(category: str, catalog_version: int) -> pd.DataFrame:
    """Load a category catalog; the version invalidates the cache after a rebuild."""
    del catalog_version
    return pd.read_csv(catalog_path(category))


@st.cache_data(show_spinner="Loading historical comparison products...")
def load_historical_peers(category: str, peer_version: int) -> pd.DataFrame:
    """Load category-matched outcomes used for peer comparison and upload matches."""
    del peer_version
    products = pd.read_csv(peer_path(category))
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
