"""
geolocation.py — Geolocation Pre-Aggregation & Centroid Reference Table
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Provides a clean, deduplicated zip-to-centroid reference table:
1. Filters coordinate anomalies using explicit, configurable Brazilian territorial bounds.
2. Default coordinates cover all Brazilian territory including oceanic archipelagos:
   - BRAZIL_LAT_MIN = -33.75 (Chuí, RS)
   - BRAZIL_LAT_MAX = 5.27   (Monte Caburaí, RR)
   - BRAZIL_LNG_MIN = -73.99 (Serra do Divisor, AC)
   - BRAZIL_LNG_MAX = -32.00 (Fernando de Noronha, PE at ~-32.4°W)
3. Computes arithmetic centroid (mean latitude/longitude) on valid coordinates.
4. Determines canonical city and state per zip prefix via statistical mode.
5. Emits exactly 1 row per unique zip_code_prefix (19,015 prefixes).
6. Outputs an audit summary to outputs/tables/geolocation_aggregation_audit.csv.
"""

from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

# Configurable Territorial Bounding Box (Brazil)
BRAZIL_LAT_MIN: float = -33.75
BRAZIL_LAT_MAX: float = 5.27
BRAZIL_LNG_MIN: float = -73.99
BRAZIL_LNG_MAX: float = -32.00  # Default accommodates Fernando de Noronha (-32.4°W)

# Alternative mainland-only boundary for comparative auditing
BRAZIL_MAINLAND_LNG_MAX: float = -34.79


def build_zip_centroids(
    geolocation_path: Path,
    output_audit_path: Path = None,
    lat_min: float = BRAZIL_LAT_MIN,
    lat_max: float = BRAZIL_LAT_MAX,
    lng_min: float = BRAZIL_LNG_MIN,
    lng_max: float = BRAZIL_LNG_MAX,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Constructs a deduplicated zip_to_centroid reference table.
    Returns:
        (zip_to_centroid_df, audit_summary_df)
    """
    df_geo = pd.read_csv(geolocation_path)
    total_raw_rows = len(df_geo)
    unique_zip_prefixes = df_geo["geolocation_zip_code_prefix"].nunique()

    # Identify coordinates within configured territorial bounds
    is_valid_coord = (
        (df_geo["geolocation_lat"] >= lat_min) &
        (df_geo["geolocation_lat"] <= lat_max) &
        (df_geo["geolocation_lng"] >= lng_min) &
        (df_geo["geolocation_lng"] <= lng_max)
    )

    df_geo["is_valid_coord"] = is_valid_coord
    valid_coord_count = int(is_valid_coord.sum())
    invalid_coord_count = int((~is_valid_coord).sum())

    # Mainland comparison
    is_valid_mainland = (
        (df_geo["geolocation_lat"] >= lat_min) &
        (df_geo["geolocation_lat"] <= lat_max) &
        (df_geo["geolocation_lng"] >= lng_min) &
        (df_geo["geolocation_lng"] <= BRAZIL_MAINLAND_LNG_MAX)
    )
    mainland_valid_count = int(is_valid_mainland.sum())
    mainland_invalid_count = int((~is_valid_mainland).sum())

    # Build per-zip stats
    # 1. Total, valid, invalid rows per zip
    zip_counts = df_geo.groupby("geolocation_zip_code_prefix").agg(
        raw_row_count=("is_valid_coord", "count"),
        valid_coord_count=("is_valid_coord", "sum"),
    )
    zip_counts["invalid_coord_count"] = zip_counts["raw_row_count"] - zip_counts["valid_coord_count"]

    # 2. Centroid coordinates from valid records
    df_valid = df_geo[is_valid_coord]
    valid_centroids = df_valid.groupby("geolocation_zip_code_prefix").agg(
        centroid_lat=("geolocation_lat", "mean"),
        centroid_lng=("geolocation_lng", "mean"),
    )

    # 3. Canonical city and state (mode per zip)
    # Using df_valid when available, else fallback to df_geo
    canonical_loc = df_valid.groupby("geolocation_zip_code_prefix").agg(
        canonical_city=("geolocation_city", lambda s: s.mode().iloc[0] if not s.empty else "unknown"),
        canonical_state=("geolocation_state", lambda s: s.mode().iloc[0] if not s.empty else "unknown"),
    )

    # Combine into canonical table
    zip_reference = zip_counts.join(valid_centroids, how="left").join(canonical_loc, how="left")

    # Handle zip prefixes where 100% of coordinates were invalid (e.g. 4 zip prefixes with erroneous overseas entries)
    # In these cases, centroid_lat/lng will be null, and canonical_city/state will be filled from raw mode
    null_centroid_mask = zip_reference["centroid_lat"].isnull()
    prefixes_all_invalid = int(null_centroid_mask.sum())

    if prefixes_all_invalid > 0:
        raw_fallback = df_geo[df_geo["geolocation_zip_code_prefix"].isin(zip_reference[null_centroid_mask].index)].groupby(
            "geolocation_zip_code_prefix"
        ).agg(
            fallback_city=("geolocation_city", lambda s: s.mode().iloc[0] if not s.empty else "unknown"),
            fallback_state=("geolocation_state", lambda s: s.mode().iloc[0] if not s.empty else "unknown"),
        )
        zip_reference.loc[null_centroid_mask, "canonical_city"] = raw_fallback["fallback_city"]
        zip_reference.loc[null_centroid_mask, "canonical_state"] = raw_fallback["fallback_state"]

    zip_reference = zip_reference.reset_index().rename(
        columns={"geolocation_zip_code_prefix": "zip_code_prefix"}
    )

    # Audit summary
    audit_rows = [
        {"metric": "total_raw_rows", "value": total_raw_rows},
        {"metric": "unique_zip_prefixes", "value": unique_zip_prefixes},
        {"metric": "configured_lat_min", "value": lat_min},
        {"metric": "configured_lat_max", "value": lat_max},
        {"metric": "configured_lng_min", "value": lng_min},
        {"metric": "configured_lng_max", "value": lng_max},
        {"metric": "valid_coordinates_count", "value": valid_coord_count},
        {"metric": "invalid_coordinates_count", "value": invalid_coord_count},
        {"metric": "mainland_valid_coordinates_count", "value": mainland_valid_count},
        {"metric": "mainland_invalid_coordinates_count", "value": mainland_invalid_count},
        {"metric": "unique_zips_with_valid_centroids", "value": unique_zip_prefixes - prefixes_all_invalid},
        {"metric": "unique_zips_with_all_invalid_coords", "value": prefixes_all_invalid},
        {"metric": "mean_raw_rows_per_zip", "value": round(total_raw_rows / unique_zip_prefixes, 2)},
        {"metric": "min_rows_per_zip", "value": int(zip_counts["raw_row_count"].min())},
        {"metric": "max_rows_per_zip", "value": int(zip_counts["raw_row_count"].max())},
    ]
    audit_df = pd.DataFrame(audit_rows)

    if output_audit_path is not None:
        output_audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_df.to_csv(output_audit_path, index=False)

    return zip_reference, audit_df


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    geo_p = base_dir / "data" / "raw" / "olist_geolocation_dataset.csv"
    audit_p = base_dir / "outputs" / "tables" / "geolocation_aggregation_audit.csv"

    centroids, audit = build_zip_centroids(geo_p, audit_p)
    print("Geolocation aggregation complete.")
    print(f"Centroids table: {len(centroids)} rows (1 per zip prefix).")
    print(f"Unique zip prefixes: {centroids['zip_code_prefix'].nunique()}")
    print(f"Audit written to: {audit_p}")
