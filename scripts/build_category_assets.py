"""Build compact catalog and historical-peer files for each supported category.

Raw Amazon files remain in ``data/`` and are intentionally excluded from Git.
The resulting files in ``results/`` are small enough to deploy with Streamlit.
"""

from __future__ import annotations

import gzip
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DAY_MS = 86_400_000
CATEGORIES = {
    "Health & Personal Care": {
        "reviews": ROOT / "data" / "Health_and_Personal_Care.jsonl",
        "metadata": ROOT / "data" / "meta_Health_and_Personal_Care.jsonl.gz",
        "catalog": ROOT / "results" / "health_product_catalog.csv",
        "peers": ROOT / "results" / "health_peer_products.csv",
    },
    "All Beauty": {
        "reviews": ROOT / "data" / "All_Beauty.jsonl",
        "metadata": ROOT / "data" / "meta_All_Beauty.jsonl.gz",
        "catalog": ROOT / "results" / "beauty_product_catalog.csv",
        "peers": ROOT / "results" / "beauty_peer_products.csv",
    },
}


def load_product_names(metadata_path: Path) -> dict[str, str]:
    names: dict[str, str] = {}
    with gzip.open(metadata_path, "rt", encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            asin = item.get("parent_asin")
            title = (item.get("title") or "").strip()
            if asin and title:
                names[asin] = title
    return names


def load_reviews(review_path: Path) -> tuple[dict[str, dict[str, object]], int]:
    products: dict[str, dict[str, object]] = defaultdict(
        lambda: {"rating_sum": 0.0, "review_count": 0, "reviews": []}
    )
    latest_timestamp = 0
    with review_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            asin = item.get("parent_asin") or item.get("asin")
            rating = item.get("rating")
            timestamp = item.get("timestamp")
            if not asin or rating is None or timestamp is None:
                continue
            timestamp = int(timestamp)
            product = products[asin]
            product["rating_sum"] += float(rating)
            product["review_count"] += 1
            product["reviews"].append((timestamp, float(rating)))
            latest_timestamp = max(latest_timestamp, timestamp)
    return products, latest_timestamp


def build_category(category: str, paths: dict[str, Path]) -> None:
    products, latest_timestamp = load_reviews(paths["reviews"])
    names = load_product_names(paths["metadata"])
    catalog_rows: list[dict[str, object]] = []
    peer_rows: list[dict[str, object]] = []

    for asin, values in products.items():
        reviews = sorted(values["reviews"])
        review_count = int(values["review_count"])
        average_stars = float(values["rating_sum"]) / review_count
        title = names.get(asin, "Product name unavailable")
        catalog_row: dict[str, object] = {
            "parent_asin": asin,
            "product_name": title,
            "average_stars": average_stars,
            "review_count": review_count,
            "days_to_20": None,
            "early_review_pace": None,
            "early_average_stars": None,
            "recent_average_stars": None,
            "rating_change": None,
            "sustained_rating": None,
        }
        if len(reviews) >= 20:
            first_timestamp = reviews[0][0]
            twentieth_timestamp = reviews[19][0]
            days_to_20 = (twentieth_timestamp - first_timestamp) / DAY_MS
            catalog_row["days_to_20"] = days_to_20
            if days_to_20 > 0:
                catalog_row["early_review_pace"] = 20 / days_to_20 * 30
        if len(reviews) >= 40:
            early_average = sum(rating for _, rating in reviews[:20]) / 20
            recent_average = sum(rating for _, rating in reviews[-20:]) / 20
            catalog_row["early_average_stars"] = early_average
            catalog_row["recent_average_stars"] = recent_average
            catalog_row["rating_change"] = recent_average - early_average
            catalog_row["sustained_rating"] = (early_average + recent_average) / 2
        catalog_rows.append(catalog_row)

        if len(reviews) < 20 or reviews[19][0] + 365 * DAY_MS > latest_timestamp:
            continue
        cutoff = reviews[19][0]
        early_ratings = [rating for _, rating in reviews[:20]]
        later_ratings = [
            rating for timestamp, rating in reviews[20:]
            if cutoff < timestamp <= cutoff + 365 * DAY_MS
        ]
        peer_rows.append(
            {
                "parent_asin": asin,
                "product_name": title,
                "early_rating_mean": sum(early_ratings) / 20,
                "days_to_20": (cutoff - reviews[0][0]) / DAY_MS,
                "early_low_rating_share": sum(rating <= 2 for rating in early_ratings) / 20,
                "later_review_count_365d": len(later_ratings),
                "later_rating_mean_365d": (
                    sum(later_ratings) / len(later_ratings) if later_ratings else None
                ),
                "last_20_rating_mean": sum(rating for _, rating in reviews[-20:]) / 20,
            }
        )

    catalog = pd.DataFrame(catalog_rows)
    overall_average = catalog["average_stars"].mean()
    minimum_reviews = catalog["review_count"].quantile(0.75)
    catalog["weighted_rating"] = (
        catalog["review_count"] / (catalog["review_count"] + minimum_reviews) * catalog["average_stars"]
        + minimum_reviews / (catalog["review_count"] + minimum_reviews) * overall_average
    )
    catalog.sort_values(["weighted_rating", "review_count"], ascending=False).to_csv(paths["catalog"], index=False)

    peers = pd.DataFrame(peer_rows)
    review_threshold = peers["later_review_count_365d"].quantile(0.75)
    peers["is_successful"] = (
        peers["later_review_count_365d"].ge(review_threshold)
        & peers["later_rating_mean_365d"].ge(4.0)
    )
    peers["category"] = category
    peers.to_csv(paths["peers"], index=False)
    print(f"{category}: {len(catalog):,} catalog products; {len(peers):,} historical peers")


if __name__ == "__main__":
    for category_name, category_paths in CATEGORIES.items():
        build_category(category_name, category_paths)
