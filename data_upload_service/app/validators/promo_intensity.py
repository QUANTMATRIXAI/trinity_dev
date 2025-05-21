import pandas as pd
from typing import List

from .base import ValidationReport, clean_columns, check_missing

# Configuration constants for Promo Intensity validation
_PI_REQUIRED = ["Channel", "Brand", "PPG", "SalesValue", "Volume"]
_PI_AGG = ["Variant", "PackType", "PackSize"]

def validate_promo_intensity(
    df: pd.DataFrame,
    *,
    required: List[str] = _PI_REQUIRED,
    aggregators: List[str] = _PI_AGG,
) -> ValidationReport:
    """
    Validates data for Promotional Intensity analysis.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing promotional data
    required : List[str], optional
        List of required columns
    aggregators : List[str], optional
        List of potential aggregator columns
        
    Returns
    -------
    ValidationReport
        Validation results
    """
    rep = ValidationReport()
    
    # Clean column names (remove whitespace)
    clean_columns(df, rep)
    
    # Check for missing values in critical columns
    check_missing(df, rep, critical=required)

    # Check for required columns
    missing_columns = [c for c in required if c not in df.columns]
    if not missing_columns:
        rep.pass_("required_cols", "all required columns present")
    else:
        rep.fail("required_cols", f"missing columns: {missing_columns}")

    # Check time granularity
    has_date = "Date" in df.columns
    has_week = "Year" in df.columns and "Week" in df.columns
    
    if has_date or has_week:
        rep.pass_("granularity", "daily" if has_date else "weekly")
    else:
        rep.fail("granularity", "need 'Date' or both 'Year' & 'Week'")

    # Check for aggregator columns
    found_aggregators = [c for c in aggregators if c in df.columns]
    if found_aggregators:
        rep.pass_("aggregators", f"found columns: {found_aggregators}")
    else:
        rep.warn("aggregators", f"none of the recommended aggregator columns found: {aggregators}")

    # Check price columns
    for col in ("Price", "BasePrice"):
        if col in df.columns:
            is_numeric = pd.api.types.is_numeric_dtype(df[col])
            if is_numeric:
                rep.pass_(col, "numeric data type confirmed")
            else:
                rep.warn(col, f"column found but not numeric (type: {df[col].dtype})")
        else:
            rep.warn(col, "column missing; will need to be computed later")
    
    # Check for promotion flag or discount
    has_promo_flag = any(col for col in df.columns if "promo" in col.lower())
    has_discount = any(col for col in df.columns if "discount" in col.lower())
    
    if has_promo_flag or has_discount:
        rep.pass_("promotion_indicator", "found promotion flag or discount column")
    else:
        rep.warn("promotion_indicator", "no promotion indicator found; will need to be derived")
    
    # Check if dataframe is empty
    if df.empty:
        rep.fail("data_empty", "Dataset is empty")
    else:
        rep.pass_("records_count", f"{len(df)} records")
        
    # Check for date ranges if available
    if "Date" in df.columns:
        try:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            
            if not df["Date"].isna().all():
                min_date = df["Date"].min().date()
                max_date = df["Date"].max().date()
                date_range = (max_date - min_date).days + 1
                rep.pass_("date_range", f"from {min_date} to {max_date} ({date_range} days)")
        except Exception as e:
            rep.warn("date_range", f"error analyzing date range: {str(e)}")
    
    return rep