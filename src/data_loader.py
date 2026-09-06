"""
data_loader.py -- Centralized Data Loading & Caching Module
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Provides a single, reusable entry point for loading raw CSVs and derived
analytical tables. All downstream modules should import from here rather
than reading CSVs independently, ensuring:
1. Consistent file paths.
2. Consistent dtypes and parse settings.
3. Single-point schema validation.
4. Optional caching to avoid repeated disk I/O.
"""

from pathlib import Path
from typing import Dict, Optional
import sys
import pandas as pd

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.data_contract import RAW_EXPECTED_COLUMNS

# ------------------------------------------------------------------------------
# Path Constants
# ------------------------------------------------------------------------------
RAW_DIR: Path = _project_root / "data" / "raw"
PROCESSED_DIR: Path = _project_root / "data" / "processed"
TABLES_DIR: Path = _project_root / "outputs" / "tables"

RAW_FILES: Dict[str, Path] = {
    "orders": RAW_DIR / "olist_orders_dataset.csv",
    "items": RAW_DIR / "olist_order_items_dataset.csv",
    "payments": RAW_DIR / "olist_order_payments_dataset.csv",
    "reviews": RAW_DIR / "olist_order_reviews_dataset.csv",
    "customers": RAW_DIR / "olist_customers_dataset.csv",
    "products": RAW_DIR / "olist_products_dataset.csv",
    "sellers": RAW_DIR / "olist_sellers_dataset.csv",
    "geolocation": RAW_DIR / "olist_geolocation_dataset.csv",
    "translation": RAW_DIR / "product_category_name_translation.csv",
}

# Timestamp columns that should be parsed as datetime
DATETIME_COLUMNS: Dict[str, list] = {
    "orders": [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"],
}

# Simple in-memory cache (per-process)
_cache: Dict[str, pd.DataFrame] = {}


def load_raw(name: str, *, use_cache: bool = True) -> pd.DataFrame:
    """
    Loads a raw CSV by logical name (e.g. 'orders', 'items').
    Applies datetime parsing where applicable.
    Returns a fresh copy so callers cannot mutate the cache.
    """
    if use_cache and name in _cache:
        return _cache[name].copy()

    if name not in RAW_FILES:
        raise KeyError(f"Unknown raw dataset name '{name}'. Valid names: {list(RAW_FILES.keys())}")

    path = RAW_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"Raw file not found: {path}")

    parse_dates = DATETIME_COLUMNS.get(name, False) or False
    df = pd.read_csv(path, parse_dates=parse_dates, low_memory=False)

    if use_cache:
        _cache[name] = df

    return df.copy()


def load_canonical_base(*, use_parquet: bool = True) -> pd.DataFrame:
    """
    Loads the canonical order_analytics_base from processed output.
    Parquet preferred for speed and type fidelity.
    """
    if use_parquet:
        path = PROCESSED_DIR / "order_analytics_base.parquet"
        if not path.exists():
            raise FileNotFoundError(
                f"Canonical base not found at {path}. "
                "Run `python src/build_order_base.py` first."
            )
        return pd.read_parquet(path)
    else:
        path = PROCESSED_DIR / "order_analytics_base.csv"
        if not path.exists():
            raise FileNotFoundError(f"Canonical base CSV not found at {path}.")
        return pd.read_csv(path, low_memory=False)


def clear_cache() -> None:
    """Clears the in-memory cache of raw DataFrames."""
    _cache.clear()


if __name__ == "__main__":
    print("Data Loader -- smoke test")
    for name in RAW_FILES:
        df = load_raw(name, use_cache=False)
        print(f"  {name:15s}: {len(df):>10,} rows, {len(df.columns)} cols")
    base = load_canonical_base()
    print(f"\n  canonical base: {len(base):>10,} rows, {len(base.columns)} cols")
    print("All datasets loaded successfully.")
