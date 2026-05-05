import pytest
from unittest.mock import MagicMock, patch
from app.services.search_service import SearchService
from app.models.schemas import QueryRequest

@pytest.mark.asyncio
@patch("app.services.search_service.OpenAI")
@patch("app.services.search_service.neo4j_repo")
@patch("app.services.search_service.embedding_service")
@patch("app.services.search_service.VectorCypherRetriever")
async def test_perform_hybrid_search_success(mock_retriever_class, mock_embedding_svc, mock_repo, mock_openai_class):
    # Setup mocks
    mock_retriever_instance = MagicMock()
    mock_retriever_class.return_value = mock_retriever_instance
    
    # Mock Vector results (via _get_vector_context)
    mock_embedding_svc.get_embeddings.return_value = [[0.1, 0.2]]
    mock_repo.vector_search.return_value = [{"text": "Vector context content"}]
    
    # Mock Graph results (via _get_graph_context)
    mock_search_result = MagicMock()
    mock_item = MagicMock()
    mock_item.content = "Graph context fact"
    mock_search_result.items = [mock_item]
    mock_retriever_instance.search.return_value = mock_search_result
    
    # Mock LLM
    mock_openai_instance = MagicMock()
    mock_openai_class.return_value = mock_openai_instance
    mock_chat = MagicMock()
    mock_chat.choices = [MagicMock(message=MagicMock(content="Hybrid Answer"))]
    mock_chat.usage = MagicMock(prompt_tokens=100, completion_tokens=50)
    mock_openai_instance.chat.completions.create.return_value = mock_chat
    
    service = SearchService()
    service.client = mock_openai_instance
    service._graph_retriever = mock_retriever_instance
    
    request = QueryRequest(query="Hybrid Query?", method="hybrid", top_k=1)
    
    response = await service.perform_hybrid_search(request)
    
    assert response.status == "success"
    assert response.answer == "Hybrid Answer"
    assert "Vector context content" in response.context
    assert "Graph context fact" in response.context
    assert response.meta.latency_ms > 0
    
    # Check if both contexts were used in prompt
    args, kwargs = mock_openai_instance.chat.completions.create.call_args
    prompt = kwargs["messages"][1]["content"]
    assert "Vector context content" in prompt
    assert "Graph context fact" in prompt
