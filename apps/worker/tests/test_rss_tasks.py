"""Test RSS processing tasks."""

import pytest
from unittest.mock import patch, Mock
from worker.tasks.rss import process_rss_feed, fetch_rss_articles


def test_process_rss_feed_success(mock_redis, mock_gemini, sample_rss_feed):
    """Test successful RSS feed processing."""
    with patch('worker.tasks.rss.feedparser.parse') as mock_parse:
        mock_parse.return_value = Mock(
            feed=Mock(title="Test Feed"),
            entries=[
                Mock(
                    title="Test Article",
                    link="https://example.com/article1",
                    summary="Test summary",
                    published="2024-01-01T00:00:00Z"
                )
            ]
        )
        
        result = process_rss_feed(sample_rss_feed["url"])
        assert result is not None
        assert "articles_processed" in result


def test_process_rss_feed_invalid_url(mock_redis, mock_gemini):
    """Test RSS feed processing with invalid URL."""
    result = process_rss_feed("invalid-url")
    assert result is None


def test_fetch_rss_articles_success(mock_redis, mock_gemini):
    """Test fetching RSS articles."""
    with patch('worker.tasks.rss.feedparser.parse') as mock_parse:
        mock_parse.return_value = Mock(
            feed=Mock(title="Test Feed"),
            entries=[
                Mock(
                    title="Test Article 1",
                    link="https://example.com/article1",
                    summary="Test summary 1",
                    published="2024-01-01T00:00:00Z"
                ),
                Mock(
                    title="Test Article 2",
                    link="https://example.com/article2",
                    summary="Test summary 2",
                    published="2024-01-02T00:00:00Z"
                )
            ]
        )
        
        articles = fetch_rss_articles("https://example.com/rss")
        assert len(articles) == 2
        assert articles[0]["title"] == "Test Article 1"
        assert articles[1]["title"] == "Test Article 2"


def test_fetch_rss_articles_empty_feed(mock_redis, mock_gemini):
    """Test fetching from empty RSS feed."""
    with patch('worker.tasks.rss.feedparser.parse') as mock_parse:
        mock_parse.return_value = Mock(
            feed=Mock(title="Empty Feed"),
            entries=[]
        )
        
        articles = fetch_rss_articles("https://example.com/empty-rss")
        assert len(articles) == 0
