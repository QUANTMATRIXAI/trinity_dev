# data_upload_service/tests/test_routes.py
import json
import pytest
from fastapi import status

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}

def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

# Category forecasting tests
def test_validate_category_forecasting_json(client, sample_cf_data):
    """Test category forecasting validation with JSON data"""
    data = {
        "pipeline": "category_forecasting",
        "data": {
            "data": sample_cf_data.to_dict(orient="records")
        }
    }
    
    response = client.post("/api/v1/validate", json=data)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    
    # Basic response structure checks
    assert "ok" in result
    assert "rows" in result
    assert isinstance(result["rows"], list)
    
    # Check for expected validation results
    check_names = [row["check"] for row in result["rows"]]
    assert "date_column" in check_names
    assert "dimension_check" in check_names

def test_validate_category_forecasting_file(client, sample_cf_csv):
    """Test category forecasting validation with file upload"""
    response = client.post(
        "/api/v1/validate/file",
        files={"files": ("sample.csv", sample_cf_csv, "text/csv")},
        data={"pipeline": "category_forecasting"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    
    # Basic response structure checks
    assert "ok" in result
    assert "rows" in result
    assert isinstance(result["rows"], list)

# Promo Intensity tests
def test_validate_promo_intensity_json(client, sample_pi_data):
    """Test promo intensity validation with JSON data"""
    data = {
        "pipeline": "promo_intensity",
        "data": {
            "data": sample_pi_data.to_dict(orient="records")
        }
    }
    
    response = client.post("/api/v1/validate", json=data)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    
    # Check for expected validation results
    check_names = [row["check"] for row in result["rows"]]
    assert "required_cols" in check_names
    assert "granularity" in check_names

# MMM tests
def test_validate_mmm_json(client, sample_mmm_media_data, sample_mmm_sales_data):
    """Test MMM validation with JSON data"""
    data = {
        "pipeline": "mmm",
        "data": {
            "media": sample_mmm_media_data.to_dict(orient="records"),
            "sales": sample_mmm_sales_data.to_dict(orient="records")
        }
    }
    
    response = client.post("/api/v1/validate", json=data)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    
    # Check for expected validation results
    check_names = [row["check"] for row in result["rows"]]
    assert "section" in check_names  # Should have section markers
    
    # Check that we have both media and sales validations
    required_media = [c for c in check_names if c == "required_media"]
    required_sales = [c for c in check_names if c == "required_sales"]
    assert required_media  # Should be non-empty
    assert required_sales  # Should be non-empty

def test_validate_mmm_files(client, sample_mmm_media_csv, sample_mmm_sales_csv):
    """Test MMM validation with file uploads"""
    files = [
        ("files", ("media.csv", sample_mmm_media_csv, "text/csv")),
        ("files", ("sales.csv", sample_mmm_sales_csv, "text/csv"))
    ]
    
    file_keys = json.dumps({"0": "media", "1": "sales"})
    
    response = client.post(
        "/api/v1/validate/file",
        files=files,
        data={"pipeline": "mmm", "file_keys": file_keys}
    )
    
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    
    # Check for expected validation results
    check_names = [row["check"] for row in result["rows"]]
    assert "section" in check_names  # Should have section markers

# Error handling tests
def test_invalid_pipeline(client, sample_cf_data):
    """Test error handling for invalid pipeline"""
    data = {
        "pipeline": "invalid_pipeline",
        "data": {
            "data": sample_cf_data.to_dict(orient="records")
        }
    }
    
    response = client.post("/api/v1/validate", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_missing_required_data(client):
    """Test error handling for missing required data"""
    data = {
        "pipeline": "category_forecasting",
        "data": {}  # Missing the 'data' key
    }
    
    response = client.post("/api/v1/validate", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST