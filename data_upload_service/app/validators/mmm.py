import pandas as pd
from typing import Dict, Any, List

from .base import ValidationReport, clean_columns, check_missing, check_dtypes

# Configuration constants for MMM validation
_MMM_MEDIA = {
    "required": ["Market", "Channel", "Region", "Category", "SubCategory", "Brand",
                 "Variant", "PackType", "PPG", "PackSize", "Year", "Month", "Week",
                 "Media Category", "Media Subcategory"],
    "non_null": ["Market", "Region", "Category", "SubCategory", "Brand", "Year",
                 "Month", "Media Category", "Media Subcategory"],
    "dtypes": {"Amount_Spent": "float64", "Year": "object"},
}

_MMM_SALES = {
    "required": ["Market", "Channel", "Region", "Category", "SubCategory", "Brand",
                 "Variant", "PackType", "PPG", "PackSize", "Year", "Month", "Week",
                 "D1", "Price"],
    "non_null": ["Market", "Region", "Category", "SubCategory", "Brand", "Year", "Month"],
    "dtypes": {"D1": "float64", "Volume": "float64", "Sales": "float64",
               "Price": "float64", "Year": "object"},
}

def validate_mmm(
    media_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    *,
    media_rules: Dict[str, Any] = _MMM_MEDIA,
    sales_rules: Dict[str, Any] = _MMM_SALES,
) -> ValidationReport:
    """
    Validates data for Marketing Mix Modeling.
    
    Parameters
    ----------
    media_df : pd.DataFrame
        DataFrame containing media spend data
    sales_df : pd.DataFrame
        DataFrame containing sales data
    media_rules : Dict[str, Any], optional
        Validation rules for media data
    sales_rules : Dict[str, Any], optional
        Validation rules for sales data
        
    Returns
    -------
    ValidationReport
        Validation results with checks for both datasets
    """
    rep = ValidationReport()

    def _validate_dataset(df: pd.DataFrame, tag: str, rules: Dict[str, Any]) -> None:
        """Helper function to validate a single dataset with specified rules"""
        rep.pass_("section", tag)  # marker for section in report
        
        # Clean column names (remove whitespace)
        clean_columns(df, rep)
        
        # Check for missing values in critical columns
        check_missing(df, rep, critical=rules["non_null"])
        
        # Validate data types
        check_dtypes(df, rep, rules["dtypes"])
        
        # Check for required columns
        missing_columns = [c for c in rules["required"] if c not in df.columns]
        if not missing_columns:
            rep.pass_(f"required_{tag}", "all required columns present")
        else:
            rep.fail(f"required_{tag}", f"missing columns: {missing_columns}")
        
        # Check if DataFrame is empty
        if df.empty:
            rep.fail(f"data_empty_{tag}", "Dataset is empty")
        else:
            rep.pass_(f"records_count_{tag}", f"{len(df)} records")
            
        # Check for time period coverage
        if all(col in df.columns for col in ["Year", "Month"]):
            try:
                years = df["Year"].astype(str).unique()
                months = df["Month"].astype(int).unique()
                rep.pass_(f"time_coverage_{tag}", f"Years: {sorted(years)}, Months: {sorted(months)}")
            except Exception as e:
                rep.warn(f"time_coverage_{tag}", f"Error analyzing time coverage: {str(e)}")

    # Validate media dataset
    _validate_dataset(media_df, "media", media_rules)
    
    # Validate sales dataset
    _validate_dataset(sales_df, "sales", sales_rules)
    
    # Check for consistency between datasets
    if not media_df.empty and not sales_df.empty:
        # Check if time periods match
        try:
            media_periods = set(zip(media_df["Year"], media_df["Month"]))
            sales_periods = set(zip(sales_df["Year"], sales_df["Month"]))
            
            if media_periods == sales_periods:
                rep.pass_("time_alignment", "Time periods match between datasets")
            else:
                media_only = media_periods - sales_periods
                sales_only = sales_periods - media_periods
                
                msg = []
                if media_only:
                    msg.append(f"Periods in media but not in sales: {sorted(media_only)[:5]}...")
                if sales_only:
                    msg.append(f"Periods in sales but not in media: {sorted(sales_only)[:5]}...")
                
                rep.warn("time_alignment", "; ".join(msg))
        except Exception as e:
            rep.warn("time_alignment", f"Error checking time alignment: {str(e)}")
    
    return rep