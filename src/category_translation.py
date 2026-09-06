"""
category_translation.py — Product Category Translation & Fallback Audit
Project: Gradient Learnings Data Analytics Hackathon 2026 (Olist)

Provides a robust, deterministic category translation layer mapping Portuguese
category names to English while strictly adhering to data governance rules:
- Known translations in product_category_name_translation.csv are mapped.
- Unmapped Portuguese categories are preserved with explicit format: [original_category_name].
- Missing/null categories are labeled as 'unknown'.
- No artificial/fictitious translations are invented.
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd


def load_category_mapping(
    translation_path: Path,
) -> Dict[str, str]:
    """Loads official Portuguese to English translations."""
    df_trans = pd.read_csv(translation_path)
    return dict(zip(df_trans["product_category_name"], df_trans["product_category_name_english"]))


def translate_category(
    category: str,
    cat_map: Dict[str, str],
) -> str:
    """Translates a single category using the official map and explicit fallback."""
    if pd.isna(category) or category is None or str(category).strip() == "":
        return "unknown"
    category_str = str(category).strip()
    if category_str in cat_map:
        return cat_map[category_str]
    # Explicit fallback policy: preserve original in brackets
    return f"[{category_str}]"


def audit_category_translations(
    products_path: Path,
    translation_path: Path,
    output_audit_path: Path = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Audits category coverage across all unique products.
    Returns:
        (products_enriched, audit_summary_df)
    """
    df_products = pd.read_csv(products_path)
    cat_map = load_category_mapping(translation_path)

    df_products["product_category_name_english"] = df_products["product_category_name"].apply(
        lambda c: translate_category(c, cat_map)
    )

    # Breakdown of mapping statuses
    def get_status(row):
        cat = row["product_category_name"]
        if pd.isna(cat):
            return "MISSING_ORIGINAL"
        if str(cat).strip() in cat_map:
            return "OFFICIALLY_TRANSLATED"
        return "UNMAPPED_PRESERVED_FALLBACK"

    df_products["translation_status"] = df_products.apply(get_status, axis=1)

    # Audit summary by category
    audit_rows = []
    unique_cats = df_products.groupby("product_category_name", dropna=False).agg(
        product_count=("product_id", "count"),
        translation_status=("translation_status", "first"),
        english_name=("product_category_name_english", "first"),
    ).reset_index()

    if output_audit_path is not None:
        output_audit_path.parent.mkdir(parents=True, exist_ok=True)
        unique_cats.to_csv(output_audit_path, index=False)

    return df_products, unique_cats


if __name__ == "__main__":
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    prod_path = base_dir / "data" / "raw" / "olist_products_dataset.csv"
    trans_path = base_dir / "data" / "raw" / "product_category_name_translation.csv"
    out_path = base_dir / "outputs" / "tables" / "category_translation_audit.csv"

    enriched_prods, audit = audit_category_translations(prod_path, trans_path, out_path)
    print("Category translation audit complete.")
    print(f"Total products: {len(enriched_prods)}")
    print(f"Translation status breakdown:\n{enriched_prods['translation_status'].value_counts()}")
    print(f"Audit table written to: {out_path}")
