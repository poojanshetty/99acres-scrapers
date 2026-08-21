"""Cleaning and feature-engineering functions for raw 99acres listings."""

from __future__ import annotations

import numpy as np
import pandas as pd


FINAL_COLUMNS = [
    "name",
    "ratings",
    "location",
    "price_lakhs",
    "price_crores",
    "area_sqft",
    "bhk",
]


def price_to_lakhs(price: pd.Series) -> pd.Series:
    """Convert price strings such as '₹2.4 Cr' and '₹75 Lac' to lakhs."""
    cleaned = price.astype("string").str.replace("₹", "", regex=False).str.replace(",", "", regex=False)
    values = pd.to_numeric(cleaned.str.extract(r"([\d.]+)")[0], errors="coerce")
    return values.where(~cleaned.str.contains(r"\bCr\b", case=False, na=False), values * 100)


def clean_raw_properties(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Create the final analytical dataset from the raw Kaggle Excel export."""
    required_columns = {"name", "location", "price", "area", "bhk"}
    missing_columns = required_columns.difference(raw_data.columns)
    if missing_columns:
        raise ValueError(f"Raw data is missing required columns: {sorted(missing_columns)}")

    # Remove only exact raw duplicates. Doing this after lower-casing and location
    # parsing would incorrectly collapse distinct listings that become similar.
    data = raw_data.drop_duplicates().copy()
    raw_name = data["name"].astype("string")
    raw_location = data["location"].astype("string")

    data["ratings"] = pd.to_numeric(
        raw_name.str.extract(r"\n\s*([0-5](?:\.\d+)?)\s*$")[0], errors="coerce"
    )
    data["name"] = (
        raw_name.str.replace(r"\n\s*[0-5](?:\.\d+)?\s*$", "", regex=True)
        .str.strip()
        .str.lower()
    )
    data["location"] = (
        raw_location.str.extract(r"\bin\s+(.+)$")[0]
        .str.replace(r",\s*bangalore(?:\s+\w+)?$", "", regex=True, case=False)
        .str.strip()
        .str.lower()
    )
    data["price_lakhs"] = price_to_lakhs(data["price"])
    data["price_crores"] = data["price_lakhs"] / 100
    data["area_sqft"] = pd.to_numeric(
        data["area"].astype("string").str.replace(",", "", regex=False).str.extract(r"([\d.]+)")[0],
        errors="coerce",
    )
    data["bhk"] = pd.to_numeric(data["bhk"].astype("string").str.extract(r"(\d+)")[0], errors="coerce")

    data = data[FINAL_COLUMNS].dropna(subset=["name", "location", "price_lakhs", "area_sqft", "bhk"])
    return data.reset_index(drop=True)


def add_value_features(data: pd.DataFrame) -> pd.DataFrame:
    """Add a price-per-sqft feature used by the dashboard and value analysis."""
    result = data.copy()
    result["price_per_sqft"] = np.round(result["price_lakhs"] * 100_000 / result["area_sqft"])
    return result
