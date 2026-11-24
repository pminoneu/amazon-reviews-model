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
        lambda: {"sample_review_title": "No review title", "rating_sum": 0.0, "review_count": 0}
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

    catalog = pd.DataFrame(
        [
            {
            "parent_asin": asin,
            "sample_review_title": values["sample_review_title"],
            "average_stars": values["rating_sum"] / values["review_count"],
            "review_count": values["review_count"],
            }
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
