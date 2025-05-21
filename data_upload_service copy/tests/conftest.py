# data_upload_service/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
import pandas as pd
import io

from data_upload_service.app.main import app
from data_upload_service.app.validators.base import ValidationReport

@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def sample_cf_data():
    """Sample data for category forecasting"""
    return pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02"],
        "Market": ["US", "US"],
        "Channel": ["Retail", "Retail"],
        "Category": ["Electronics", "Electronics"],
        "Brand": ["TechBrand", "TechBrand"],
        "Sales": [1000, 1200]
    })

@pytest.fixture
def sample_pi_data():
    """Sample data for promo intensity"""
    return pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02"],
        "Channel": ["Retail", "Retail"],
        "Brand": ["TechBrand", "TechBrand"],
        "PPG": ["Product1", "Product1"],
        "SalesValue": [1000, 1200],
        "Volume": [100, 120],
        "Price": [10, 10]
    })

@pytest.fixture
def sample_mmm_media_data():
    """Sample media data for MMM"""
    return pd.DataFrame({
        "Year": ["2023", "2023"],
        "Month": [1, 1],
        "Week": [1, 2],
        "Market": ["US", "US"],
        "Region": ["West", "West"],
        "Category": ["Electronics", "Electronics"],
        "SubCategory": ["Phones", "Phones"],
        "Brand": ["TechBrand", "TechBrand"],
        "Media Category": ["TV", "TV"],
        "Media Subcategory": ["Prime Time", "Prime Time"],
        "Amount_Spent": [10000, 12000]
    })

@pytest.fixture
def sample_mmm_sales_data():
    """Sample sales data for MMM"""
    return pd.DataFrame({
        "Year": ["2023", "2023"],
        "Month": [1, 1],
        "Week": [1, 2],
        "Market": ["US", "US"],
        "Region": ["West", "West"],
        "Category": ["Electronics", "Electronics"],
        "SubCategory": ["Phones", "Phones"],
        "Brand": ["TechBrand", "TechBrand"],
        "D1": [1000, 1200],
        "Price": [10, 10],
        "Volume": [100, 120],
        "Sales": [1000, 1200]
    })

@pytest.fixture
def sample_cf_csv():
    """Sample CSV for category forecasting"""
    csv_data = """Date,Market,Channel,Category,Brand,Sales
2023-01-01,US,Retail,Electronics,TechBrand,1000
2023-01-02,US,Retail,Electronics,TechBrand,1200"""
    return io.BytesIO(csv_data.encode())

@pytest.fixture
def sample_mmm_media_csv():
    """Sample CSV for MMM media"""
    csv_data = """Year,Month,Week,Market,Region,Category,SubCategory,Brand,Media Category,Media Subcategory,Amount_Spent
2023,1,1,US,West,Electronics,Phones,TechBrand,TV,Prime Time,10000
2023,1,2,US,West,Electronics,Phones,TechBrand,TV,Prime Time,12000"""
    return io.BytesIO(csv_data.encode())

@pytest.fixture
def sample_mmm_sales_csv():
    """Sample CSV for MMM sales"""
    csv_data = """Year,Month,Week,Market,Region,Category,SubCategory,Brand,D1,Price,Volume,Sales
2023,1,1,US,West,Electronics,Phones,TechBrand,1000,10,100,1000
2023,1,2,US,West,Electronics,Phones,TechBrand,1200,10,120,1200"""
    return io.BytesIO(csv_data.encode())