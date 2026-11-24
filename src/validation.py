"""Validation for the fixed first-20-review prediction input."""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {"parent_asin", "rating", "text", "date", "verified_purchase"}


def normalize_columns(reviews: pd.DataFrame) -> pd.DataFrame:
    """Accept a few common header variations and return consistent names."""
    normalized = {
        column: column.strip().lower().replace(" ", "_")
        for column in reviews.columns
    }
    aliases = {
        "stars": "rating",
        "review_text": "text",
        "review_date": "date",
        "timestamp": "date",
        "verified": "verified_purchase",
        "is_verified_purchase": "verified_purchase",
        "asin": "parent_asin",
        "product_asin": "parent_asin",
        "product_id": "parent_asin",
    }
    return reviews.rename(columns=normalized).rename(columns=aliases)


def validate_reviews(reviews: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Return standardized reviews and user-facing validation errors."""
    reviews = normalize_columns(reviews.copy())
    errors: list[str] = []

    missing = REQUIRED_COLUMNS - set(reviews.columns)
    if missing:
        errors.append("Missing required column(s): " + ", ".join(sorted(missing)) + ".")
        return reviews, errors

    if len(reviews) != 20:
        errors.append(f"Upload exactly 20 reviews; this file contains {len(reviews)}.")

    asins = reviews["parent_asin"].fillna("").astype(str).str.strip()
    if asins.eq("").any():
        errors.append("Each review needs a parent_asin (or asin) value.")
    elif asins.nunique() != 1:
        errors.append("All 20 reviews must have the same parent_asin.")
    reviews["parent_asin"] = asins

    reviews["rating"] = pd.to_numeric(reviews["rating"], errors="coerce")
    if reviews["rating"].isna().any() or not reviews["rating"].between(1, 5).all():
        errors.append("Each rating must be a number from 1 to 5.")

    reviews["date"] = pd.to_datetime(reviews["date"], errors="coerce", utc=True)
    if reviews["date"].isna().any():
        errors.append("Each date must be a valid date or timestamp.")

    if reviews["text"].fillna("").astype(str).str.strip().eq("").any():
        errors.append("Each review needs non-empty text.")

    accepted_flags = {"true", "false", "yes", "no", "1", "0"}
    flags = reviews["verified_purchase"].astype(str).str.strip().str.lower()
    if not flags.isin(accepted_flags).all():
        errors.append("verified_purchase must use True/False, Yes/No, or 1/0.")

    return reviews, errors
