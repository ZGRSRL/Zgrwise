"""Test embedding generation tasks."""

import pytest
import numpy as np
from unittest.mock import patch, Mock
from worker.tasks.embed import generate_embeddings, process_highlight_embeddings


def test_generate_embeddings_success(mock_redis, sample_article):
    """Test successful embedding generation."""
    with patch('worker.tasks.embed.SentenceTransformer') as mock_model:
        mock_instance = Mock()
        mock_instance.encode.return_value = np.array([0.1, 0.2, 0.3, 0.4])
        mock_model.return_value = mock_instance
        
        embeddings = generate_embeddings(sample_article["content"])
        assert embeddings is not None
        assert len(embeddings) == 4
        assert isinstance(embeddings, list)


def test_generate_embeddings_empty_content(mock_redis):
    """Test embedding generation with empty content."""
    embeddings = generate_embeddings("")
    assert embeddings is None


def test_generate_embeddings_none_content(mock_redis):
    """Test embedding generation with None content."""
    embeddings = generate_embeddings(None)
    assert embeddings is None


def test_process_highlight_embeddings_success(mock_redis, mock_gemini):
    """Test processing highlight embeddings."""
    highlight_data = {
        "id": 1,
        "text": "This is a test highlight",
        "source_id": 1
    }
    
    with patch('worker.tasks.embed.generate_embeddings') as mock_embeddings:
        mock_embeddings.return_value = [0.1, 0.2, 0.3, 0.4]
        
        result = process_highlight_embeddings(highlight_data)
        assert result is not None
        assert "highlight_id" in result
        assert "embeddings" in result


def test_process_highlight_embeddings_failure(mock_redis, mock_gemini):
    """Test processing highlight embeddings with failure."""
    highlight_data = {
        "id": 1,
        "text": "",
        "source_id": 1
    }
    
    with patch('worker.tasks.embed.generate_embeddings') as mock_embeddings:
        mock_embeddings.return_value = None
        
        result = process_highlight_embeddings(highlight_data)
        assert result is None
