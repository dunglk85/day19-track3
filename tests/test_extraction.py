import pytest
from unittest.mock import MagicMock, patch
import os

# Set dummy API key
os.environ["OPENAI_API_KEY"] = "sk-dummy"

from app.services.indexing_service import IndexingService
from app.services.loader_service import Document
from app.models.schemas import ExtractionResult

@patch("app.services.indexing_service.OpenAI")
def test_extract_entities_graceful_validation(mock_openai):
    # Setup mock response with one valid and one invalid entity
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = """
    {
        "entities": [
            {"name": "OpenAI", "label": "Company"},
            {"name": "Bad", "label": "InvalidLabel"}
        ],
        "relationships": []
    }
    """
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 50
    mock_client.chat.completions.create.return_value = mock_response
    
    service = IndexingService()
    chunk = Document(page_content="Text", metadata={"source_file": "test.txt"})
    
    result = service.extract_entities(chunk)
    
    # Should contain only the valid entity
    assert len(result.entities) == 1
    assert result.entities[0].name == "OpenAI"
    assert result.entities[0].label == "Company"

@patch("app.services.indexing_service.OpenAI")
def test_extract_entities_retry_logic(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    # Fail twice, then succeed
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"entities": [], "relationships": []}'
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    
    mock_client.chat.completions.create.side_effect = [
        Exception("API Error"),
        Exception("API Error"),
        mock_response
    ]
    
    service = IndexingService()
    chunk = Document(page_content="Text", metadata={"source_file": "test.txt"})
    
    result = service.extract_entities(chunk)
    
    assert mock_client.chat.completions.create.call_count == 3
    assert isinstance(result, ExtractionResult)
