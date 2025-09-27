"""Test highlights endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_create_highlight(client: TestClient, sample_highlight_data):
    """Test creating a new highlight."""
    response = client.post(
        "/api/highlights",
        json=sample_highlight_data,
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == sample_highlight_data["text"]
    assert "id" in data


def test_create_highlight_unauthorized(client: TestClient, sample_highlight_data):
    """Test creating highlight without API key."""
    response = client.post("/api/highlights", json=sample_highlight_data)
    assert response.status_code == 401


def test_get_highlights(client: TestClient):
    """Test getting highlights list."""
    response = client.get(
        "/api/highlights",
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_highlights_unauthorized(client: TestClient):
    """Test getting highlights without API key."""
    response = client.get("/api/highlights")
    assert response.status_code == 401


def test_get_highlight_by_id(client: TestClient, sample_highlight_data):
    """Test getting a specific highlight by ID."""
    # First create a highlight
    create_response = client.post(
        "/api/highlights",
        json=sample_highlight_data,
        headers={"X-API-Key": "test-key"}
    )
    assert create_response.status_code == 201
    highlight_id = create_response.json()["id"]
    
    # Then get it by ID
    response = client.get(
        f"/api/highlights/{highlight_id}",
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == highlight_id
    assert data["text"] == sample_highlight_data["text"]


def test_get_nonexistent_highlight(client: TestClient):
    """Test getting a highlight that doesn't exist."""
    response = client.get(
        "/api/highlights/99999",
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 404
