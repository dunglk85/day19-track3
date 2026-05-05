import pytest
from unittest.mock import MagicMock, patch
from app.services.search_service import SearchService
from app.models.schemas import QueryRequest

@pytest.mark.asyncio
@patch("app.services.search_service.OpenAI")
@patch("app.services.search_service.neo4j_repo")
@patch("app.services.search_service.embedding_service")
async def test_perform_vector_search_success(mock_embedding, mock_repo, mock_openai_class):
    # Setup mocks
    mock_embedding.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
    mock_repo.vector_search.return_value = [
        {"text": "Google was founded by Larry Page and Sergey Brin.", "score": 0.9, "source": "google.txt"},
        {"text": "OpenAI is an AI research laboratory.", "score": 0.85, "source": "openai.txt"}
    ]
    
    mock_openai_instance = MagicMock()
    mock_openai_class.return_value = mock_openai_instance
    
    mock_chat = MagicMock()
    mock_chat.choices = [MagicMock(message=MagicMock(content="Google được thành lập bởi Larry Page và Sergey Brin."))]
    mock_chat.usage = MagicMock(prompt_tokens=50, completion_tokens=20)
    mock_openai_instance.chat.completions.create.return_value = mock_chat
    
    # We need to re-initialize the service to use the mocked OpenAI client
    # but SearchService creates it in __init__. 
    # Alternatively, we can patch the instance's client.
    service = SearchService()
    service.client = mock_openai_instance
    
    request = QueryRequest(query="Ai sáng lập Google?", method="vector", top_k=2)
    
    response = await service.perform_vector_search(request)
    
    assert response.status == "success"
    assert "Larry Page" in response.answer
    assert len(response.context) == 2
    assert response.meta.tokens["prompt"] == 50
    assert response.meta.tokens["completion"] == 20
    assert response.meta.latency_ms >= 0

@pytest.mark.asyncio
@patch("app.services.search_service.search_service.perform_vector_search")
async def test_api_endpoint_vector(mock_search):
    # This would typically use TestClient, but for now we just test the logic
    from app.api.v1.search import query_rag
    from app.models.schemas import QueryResponse, SearchMeta
    
    mock_search.return_value = QueryResponse(
        answer="Test Answer",
        context=["C1"],
        meta=SearchMeta(tokens={"total": 10}, latency_ms=100.0)
    )
    
    request = QueryRequest(query="Test?", method="vector")
    response = await query_rag(request)
    
    assert response.answer == "Test Answer"
    mock_search.assert_called_once_with(request)
