from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field

class ValidationReportRow(BaseModel):
    check: str
    status: str
    msg: Optional[str] = ""
    column: Optional[str] = None

class ValidationResponse(BaseModel):
    ok: bool
    rows: List[ValidationReportRow]

class ValidationRequest(BaseModel):
    pipeline: str = Field(
        ..., 
        description="Validation pipeline to use",
        examples=["category_forecasting", "mmm", "promo_intensity"]
    )
    data: Dict[str, List[Dict[str, Any]]] = Field(
        ...,
        description="Data to validate as a dictionary of DataFrames",
        examples=[
            {
                "data": [
                    {"Market": "US", "Date": "2023-01-01", "Sales": 100}
                ]
            }
        ]
    )

class HealthResponse(BaseModel):
    status: str = "ok"