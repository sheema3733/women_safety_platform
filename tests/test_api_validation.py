"""
Tests for API Request and Response Validation & Geospatial Proximity Endpoints
Part of Member 2 Backend Development & Integration
"""

import pytest
from app.validators.forms import validate_coordinates
from app.repositories.resource_repo import ResourceRepository
from app.repositories.user_repo import UserRepository
from app.repositories.sos_repo import SOSRepository

def test_validate_coordinates_valid():
    lat, lng, err = validate_coordinates("12.9716", "77.5946")
    assert err is None
    assert lat == 12.9716
    assert lng == 77.5946

def test_validate_coordinates_empty_optional():
    lat, lng, err = validate_coordinates(None, None, required=False)
    assert err is None
    assert lat is None
    assert lng is None

def test_validate_coordinates_missing_required():
    lat, lng, err = validate_coordinates("", "", required=True)
    assert err is not None
    assert "required" in err.lower()

def test_validate_coordinates_out_of_bounds_latitude():
    lat, lng, err = validate_coordinates("95.5", "77.0")
    assert err is not None
    assert "-90.0 and 90.0" in err

def test_validate_coordinates_out_of_bounds_longitude():
    lat, lng, err = validate_coordinates("12.0", "195.0")
    assert err is not None
    assert "-180.0 and 180.0" in err

def test_validate_coordinates_non_numeric():
    lat, lng, err = validate_coordinates("invalid_lat", "77.0")
    assert err is not None
    assert "decimal number" in err

def test_validate_coordinates_partial_pair():
    lat, lng, err = validate_coordinates("12.0", None)
    assert err is not None
    assert "provided together" in err

def test_api_resources_endpoint(client):
    res = client.get("/api/resources?limit=5")
    assert res.status_code == 200
    data = res.get_json()
    assert "count" in data
    assert "results" in data
    assert data["limit"] == 5

def test_api_resources_nearby_missing_coords(client):
    res = client.get("/api/resources/nearby")
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data
    assert data["status_code"] == 400

def test_api_resources_nearby_invalid_coords(client):
    res = client.get("/api/resources/nearby?lat=999&lng=77.5")
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data

def test_api_resources_nearby_valid_coords(client):
    # Query around Bangalore center (12.97, 77.59)
    res = client.get("/api/resources/nearby?lat=12.9716&lng=77.5946&radius_km=50")
    assert res.status_code == 200
    data = res.get_json()
    assert "radius_km" in data
    assert "results" in data
    if data["results"]:
        first = data["results"][0]
        assert "distance_km" in first
        assert isinstance(first["distance_km"], (int, float))

def test_api_sos_active_unauthenticated(client):
    res = client.get("/api/sos/active")
    assert res.status_code == 401
    data = res.get_json()
    assert "error" in data

def test_api_sos_status_unauthenticated(client):
    res = client.get("/api/sos/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["has_active_sos"] is False
    assert data["authenticated"] is False
