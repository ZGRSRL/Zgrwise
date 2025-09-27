"""Test sources endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_create_source(client: TestClient, sample_source_data):
    """Test creating a new source."""
    response = client.post(
        "/api/sources",
        json=sample_source_data,
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_source_data["title"]
    assert data["url"] == sample_source_data["url"]
    assert "id" in data


def test_create_source_unauthorized(client: TestClient, sample_source_data):
    """Test creating source without API key."""
    response = client.post("/api/sources", json=sample_source_data)
    assert response.status_code == 401


def test_get_sources(client: TestClient):
    """Test getting sources list."""
    response = client.get(
        "/api/sources",
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_source_by_id(client: TestClient, sample_source_data):
    """Test getting a specific source by ID."""
    # First create a source
    create_response = client.post(
        "/api/sources",
        json=sample_source_data,
        headers={"X-API-Key": "test-key"}
    )
    assert create_response.status_code == 201
    source_id = create_response.json()["id"]
    
    # Then get it by ID
    response = client.get(
        f"/api/sources/{source_id}",
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == source_id
    assert data["title"] == sample_source_data["title"]


def test_get_nonexistent_source(client: TestClient):
    """Test getting a source that doesn't exist."""
    response = client.get(
        "/api/sources/99999",
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 404
