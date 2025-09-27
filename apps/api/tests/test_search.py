"""Test search endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_search_highlights(client: TestClient):
    """Test searching highlights."""
    search_data = {
        "q": "test query",
        "limit": 10
    }
    response = client.post(
        "/api/search",
        json=search_data,
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert isinstance(data["results"], list)


def test_search_highlights_unauthorized(client: TestClient):
    """Test searching without API key."""
    search_data = {"q": "test query"}
    response = client.post("/api/search", json=search_data)
    assert response.status_code == 401


def test_search_with_pagination(client: TestClient):
    """Test search with pagination parameters."""
    search_data = {
        "q": "test",
        "limit": 5,
        "offset": 0
    }
    response = client.post(
        "/api/search",
        json=search_data,
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 5


def test_search_empty_query(client: TestClient):
    """Test search with empty query."""
    search_data = {"q": ""}
    response = client.post(
        "/api/search",
        json=search_data,
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 400
