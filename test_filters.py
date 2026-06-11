# pyrefly: ignore [missing-import]
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

endpoints = [
    "/api/v1/admin/analytics/users",
    "/api/v1/admin/analytics/conversions",
    "/api/v1/admin/analytics/economics",
    "/api/v1/admin/analytics/referrals",
    "/api/v1/admin/analytics/operations"
]

@pytest.mark.parametrize("endpoint", endpoints)
def test_endpoints_without_filters(endpoint):
    response = client.get(endpoint)
    assert response.status_code == 200, f"Failed on {endpoint} without filters. Response: {response.text}"

@pytest.mark.parametrize("endpoint", endpoints)
def test_endpoints_with_filters(endpoint):
    params = {
        "start_date": "2026-01-01T00:00:00",
        "end_date": "2026-12-31T23:59:59"
    }
    response = client.get(endpoint, params=params)
    assert response.status_code == 200, f"Failed on {endpoint} with filters. Response: {response.text}"
