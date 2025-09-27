"""Test configuration and fixtures for ZgrWise API tests."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_db, Base
from app.config import get_settings

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_settings():
    """Test settings with overrides."""
    settings = get_settings()
    settings.database_url = TEST_DATABASE_URL
    settings.api_key = "test-key"
    settings.gemini_api_key = "test-gemini-key"
    return settings


@pytest.fixture
def sample_highlight_data():
    """Sample highlight data for testing."""
    return {
        "source_id": 1,
        "text": "This is a test highlight",
        "context": "Test context",
        "tags": ["test", "sample"]
    }


@pytest.fixture
def sample_source_data():
    """Sample source data for testing."""
    return {
        "url": "https://example.com/test-article",
        "title": "Test Article",
        "source_type": "web",
        "content": "This is test content for the article."
    }
