import pandas as pd
from typing import Optional

from .base import ValidationReport, clean_columns, check_missing

_CF_ANY = [
    "Market", "Channel", "Region", "Category", "SubCategory",
    "Brand", "PPG", "Variant", "PackType", "PackSize",
]

def validate_category_forecasting(
    df: pd.DataFrame,
    *,
    date_col: str = "Date",
    fiscal_start_month: int = 4,
) -> ValidationReport:
    rep = ValidationReport()
    
    # 1. Clean column names (remove leading/trailing spaces and standardize case)
    # First strip whitespace
    renamed_cols = {c: c.strip() for c in df.columns if c != c.strip()}
    if renamed_cols:
        df.rename(columns=renamed_cols, inplace=True)
        rep.pass_("cleanup","pass", f"renamed columns {list(renamed_cols.keys())}")
     
    # Then standardize case variations
    standard_names = {
        "market": "Market", "channel": "Channel", "region": "Region", 
        "category": "Category", "subcategory": "SubCategory", "sub-category": "SubCategory",
        "brand": "Brand", "ppg": "PPG", "variant": "Variant", 
        "packtype": "PackType", "pack type": "PackType", "pack-type": "PackType",
        "packsize": "PackSize", "pack size": "PackSize", "pack-size": "PackSize",
        "fiscal year": "Fiscal Year", "fiscalyear": "Fiscal Year", "fiscal-year": "Fiscal Year",
        "date": "Date"
    }
    
    case_standardized = {}
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in standard_names and col != standard_names[col_lower]:
            case_standardized[col] = standard_names[col_lower]
    
    if case_standardized:
        df.rename(columns=case_standardized, inplace=True)
        rep.pass_("case_standardization", f"standardized column names: {list(case_standardized.keys())}")
    
    # 2. Date column validation and conversion
    if date_col not in df.columns:
        rep.fail("date_column", f"'{date_col}' not found")
    else:
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            try:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                if df[date_col].isna().all():
                    rep.fail("date_column", "all values NaT after conversion")
                else:
                    rep.pass_("date_column", "valid datetime")
            except Exception as e:
                rep.fail("date_column", f"error converting: {str(e)}")
        else:
            rep.pass_("date_column","valid datetime")
        
        # Check for duplicate dates
        if date_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[date_col]):
            dup = df[date_col].duplicated().sum()
            if dup:
                rep.fail("duplicate_dates", f"{dup} duplicates")
            else:
                rep.pass_("duplicate_dates")
            
            # Add date range information
            if not df[date_col].isna().all():
                min_date = df[date_col].min().date()
                max_date = df[date_col].max().date()
                rep.pass_("date_range", f"from {min_date} to {max_date}")
    
    # 3. Check for required columns (case-insensitive)
    found = []
    for required in _CF_ANY:
        # Check for exact match first
        if required in df.columns:
            found.append(required)
        # If not found, try case-insensitive match
        elif required.lower() in [col.lower() for col in df.columns]:
            # Find the actual column name that matched
            for col in df.columns:
                if col.lower() == required.lower():
                    found.append(col)
                    break
    
    if found:
        rep.pass_("dimension_check", f"found {', '.join(found)}")
    else:
        rep.fail("dimension_check", f"need at least one of {', '.join(_CF_ANY)}")
    
    # 4. Check for Fiscal Year column
    if "Fiscal Year" in df.columns:
        rep.pass_("fiscal_year")
    else:
        # Create Fiscal Year column based on date column if date column is valid
        if date_col in df.columns and not df[date_col].isna().all() and pd.api.types.is_datetime64_any_dtype(df[date_col]):
            rep.warn("fiscal_year", "success_with_warning",f"will compute at runtime (start={fiscal_start_month})")
    
    # 5. Missing values summary
    check_missing(df, rep)
    
    # 6. Check if dataframe is empty
    if df.empty:
        rep.fail("data_empty", "Data is empty after validations")
    else:
        rep.pass_("records_count", f"{len(df)} records")
    
    return rep