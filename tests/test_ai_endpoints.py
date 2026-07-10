import pytest
from fastapi.testclient import TestClient

# Pastikan import dari root ai-engine bisa berjalan
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_health_check():
    """Test Happy Path: Healthcheck endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_forecasting_empty_data():
    """Test Edge Case: Forecasting dengan data kosong"""
    response = client.get("/api/v1/ai/forecasting/stockouts")
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert isinstance(data["predictions"], list)
    assert len(data["predictions"]) == 0  # Tidak ada produk yang di-forecast

from unittest.mock import patch, AsyncMock

@patch('routers.ai_router.ClusteringService.segment_customers', new_callable=AsyncMock)
def test_clustering_insufficient_data(mock_segment):
    """Test Edge Case: Clustering dengan data < 3 (K-Means constraint)"""
    # Mock return value to prevent DB error (returns clusters list, score)
    mock_segment.return_value = ([], 0.0)
    
    response = client.get("/api/v1/ai/clustering/customers")
    assert response.status_code == 200
    data = response.json()
    
    assert "clusters" in data
    assert "silhouette_score" in data
    # Karena data < 3, sil_score default harus 0.0
    assert data["silhouette_score"] == 0.0
