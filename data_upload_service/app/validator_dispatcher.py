import pandas as pd
from typing import Dict, List, Union, Any

from .validators.category_forecasting import validate_category_forecasting
from .validators.promo_intensity import validate_promo_intensity
from .validators.mmm import validate_mmm

def dispatch_validation(
    pipeline: str,
    dfs: Dict[str, pd.DataFrame]
) -> Any:
    """
    Dispatches validation to the appropriate validator based on the pipeline name.
    
    Parameters
    ----------
    pipeline : str
        One of 'category_forecasting', 'mmm', 'promo_intensity'
    dfs : Dict[str, pd.DataFrame]
        Dictionary of DataFrames to validate
        • category_forecasting → expects 'data' key
        • promo_intensity → expects 'data' key
        • mmm → expects 'media' and 'sales' keys
    
    Returns
    -------
    ValidationReport
        The validation report
    """
    if pipeline == "category_forecasting":
        # For category forecasting, we expect a single DataFrame
        if "data" not in dfs:
            raise ValueError("Category forecasting expects a DataFrame with key 'data'")
        return validate_category_forecasting(dfs["data"])
    
    elif pipeline == "promo_intensity":
        # For promo intensity, we expect a single DataFrame
        if "data" not in dfs:
            raise ValueError("Promo intensity expects a DataFrame with key 'data'")
        return validate_promo_intensity(dfs["data"])
    
    elif pipeline == "mmm":
        # For MMM, we expect two DataFrames: media and sales
        if "media" not in dfs or "sales" not in dfs:
            raise ValueError("MMM expects DataFrames with keys 'media' and 'sales'")
        return validate_mmm(dfs["media"], dfs["sales"])
    
    else:
        raise ValueError(f"Unknown pipeline: {pipeline}")