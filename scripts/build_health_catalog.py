"""Build a deployable Health & Personal Care product catalog from review JSONL.

The source review file stays local. The resulting compact CSV is safe to include
with the Streamlit app and powers the searchable Explore catalog.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "Health_and_Personal_Care.jsonl"
METADATA_PATH = ROOT / "data" / "meta_Health_and_Personal_Care.jsonl.gz"
OUTPUT_PATH = ROOT / "results" / "health_product_catalog.csv"


def build_catalog() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing source file: {INPUT_PATH}")
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Missing metadata file: {METADATA_PATH}")

    products: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "sample_review_title": "No review title",
            "rating_sum": 0.0,
            "review_count": 0,
            "reviews": [],
        }
    )
    with INPUT_PATH.open("r", encoding="utf-8") as stream:
        for line in stream:
            review = json.loads(line)
            parent_asin = review.get("parent_asin") or review.get("asin")
            rating = review.get("rating")
            if not parent_asin or rating is None:
                continue
            product = products[parent_asin]
            title = (review.get("title") or "").strip()
            if title and product["sample_review_title"] == "No review title":
                product["sample_review_title"] = title
            product["rating_sum"] += float(rating)
            product["review_count"] += 1
            if review.get("timestamp") is not None:
                product["reviews"].append((int(review["timestamp"]), float(rating)))

    catalog = pd.DataFrame(
        [
            product_row(asin, values)
            for asin, values in products.items()
        ]
    )
    product_names = load_product_names()
    catalog["product_name"] = catalog["parent_asin"].map(product_names).fillna("Product name unavailable")
    overall_average = catalog["average_stars"].mean()
    minimum_reviews = catalog["review_count"].quantile(0.75)
    catalog["weighted_rating"] = (
        catalog["review_count"] / (catalog["review_count"] + minimum_reviews) * catalog["average_stars"]
        + minimum_reviews / (catalog["review_count"] + minimum_reviews) * overall_average
    )
    return catalog.sort_values(["weighted_rating", "review_count"], ascending=False)


def product_row(parent_asin: str, values: dict[str, object]) -> dict[str, object]:
    """Calculate review-volume, pace, and sustained-rating fields for one product."""
    ordered_reviews = sorted(values["reviews"])
    review_count = values["review_count"]
    row: dict[str, object] = {
        "parent_asin": parent_asin,
        "sample_review_title": values["sample_review_title"],
        "average_stars": values["rating_sum"] / review_count,
        "review_count": review_count,
        "days_to_20": None,
        "early_review_pace": None,
        "early_average_stars": None,
        "recent_average_stars": None,
        "rating_change": None,
        "sustained_rating": None,
    }
    if len(ordered_reviews) >= 20:
        first_timestamp = ordered_reviews[0][0]
        twentieth_timestamp = ordered_reviews[19][0]
        days_to_20 = (twentieth_timestamp - first_timestamp) / 86_400_000
        row["days_to_20"] = days_to_20
        if days_to_20 > 0:
            row["early_review_pace"] = 20 / days_to_20 * 30
    if len(ordered_reviews) >= 40:
        early_average = sum(rating for _, rating in ordered_reviews[:20]) / 20
        recent_average = sum(rating for _, rating in ordered_reviews[-20:]) / 20
        row["early_average_stars"] = early_average
        row["recent_average_stars"] = recent_average
        row["rating_change"] = recent_average - early_average
        row["sustained_rating"] = (early_average + recent_average) / 2
    return row


def load_product_names() -> dict[str, str]:
    """Read only the metadata needed for the product-name join."""
    product_names: dict[str, str] = {}
    import gzip

    with gzip.open(METADATA_PATH, "rt", encoding="utf-8") as stream:
        for line in stream:
            product = json.loads(line)
            parent_asin = product.get("parent_asin")
            title = (product.get("title") or "").strip()
            if parent_asin and title:
                product_names[parent_asin] = title
    return product_names


if __name__ == "__main__":
    output = build_catalog()
    output.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(output):,} products to {OUTPUT_PATH}")
