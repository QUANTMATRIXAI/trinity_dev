import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Dict, List, Optional
import json
import io

from .schemas import ValidationResponse, ValidationRequest, ValidationReportRow
from .validator_dispatcher import dispatch_validation

router = APIRouter()

@router.post("/validate", response_model=ValidationResponse)
async def validate_data(request: ValidationRequest):
    """
    Validate data for a specific pipeline.
    
    Accepts JSON data with pipeline type and data frames.
    """
    try:
        # Convert the dictionary data to pandas DataFrames
        dataframes = {}
        for key, data_list in request.data.items():
            if data_list:  # Only process non-empty lists
                dataframes[key] = pd.DataFrame(data_list)
        
        # Dispatch to the appropriate validator
        report = dispatch_validation(request.pipeline, dataframes)
        
        # Convert ValidationReport to response schema
        response = ValidationResponse(
            ok=report.ok,
            rows=[
                ValidationReportRow(
                    check=row["check"],
                    status=row["status"],
                    msg=row["msg"],
                    column=row["column"]
                )
                for row in report.rows()
            ]
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate/file", response_model=ValidationResponse)
async def validate_file(
    pipeline: str = Form(...),
    files: List[UploadFile] = File(...),
    file_keys: Optional[str] = Form(None)
):
    """
    Validate data from CSV file uploads.
    
    - pipeline: The validation pipeline to use
    - files: CSV files to validate
    - file_keys: Optional JSON string mapping file indices to keys (for MMM)
    """
    try:
        # Parse file_keys if provided
        keys = {}
        if file_keys:
            keys = json.loads(file_keys)
        
        # Process files into DataFrames
        dataframes = {}
        
        for i, file in enumerate(files):
            # Read file content
            content = await file.read()
            
            # Determine the key for this file
            if str(i) in keys:
                key = keys[str(i)]
            elif len(files) == 1:
                key = "data"
            elif i == 0:
                key = "media" if pipeline == "mmm" else "data"
            elif i == 1 and pipeline == "mmm":
                key = "sales"
            else:
                key = f"data_{i}"
                
            # Convert to DataFrame
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            dataframes[key] = df
        
        # Dispatch to the appropriate validator
        report = dispatch_validation(pipeline, dataframes)
        
        # Convert ValidationReport to response schema
        response = ValidationResponse(
            ok=report.ok,
            rows=[
                ValidationReportRow(
                    check=row["check"],
                    status=row["status"],
                    msg=row["msg"],
                    column=row["column"]
                )
                for row in report.rows()
            ]
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))