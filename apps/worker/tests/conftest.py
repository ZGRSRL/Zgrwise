"""Test configuration and fixtures for ZgrWise Worker tests."""

import pytest
import asyncio
from typing import Generator
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from worker.utils.models import Base
from worker.utils.db import get_db_session

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_worker.db"

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


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    with patch('worker.utils.db.redis.Redis') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.ping.return_value = True
        yield mock_instance


@pytest.fixture
def mock_gemini():
    """Mock Gemini API for testing."""
    with patch('worker.utils.ai.generate_content') as mock:
        mock.return_value = {
            "summary": "Test summary",
            "tags": ["test", "sample"],
            "confidence": 0.95
        }
        yield mock


@pytest.fixture
def sample_rss_feed():
    """Sample RSS feed data for testing."""
    return {
        "url": "https://example.com/rss",
        "title": "Test RSS Feed",
        "last_updated": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_article():
    """Sample article data for testing."""
    return {
        "url": "https://example.com/article",
        "title": "Test Article",
        "content": "This is test content for the article.",
        "published_date": "2024-01-01T00:00:00Z"
    }
