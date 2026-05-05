import pytest
from unittest.mock import MagicMock, patch
from app.services.search_service import SearchService
from app.models.schemas import QueryRequest

@pytest.mark.asyncio
@patch("app.services.search_service.OpenAI")
@patch("app.services.search_service.neo4j_repo")
@patch("app.services.search_service.embedding_service")
@patch("app.services.search_service.VectorCypherRetriever")
@patch("app.services.search_service.OpenAIEmbeddings")
async def test_perform_graph_search_success(mock_embeddings_class, mock_retriever_class, mock_embedding_svc, mock_repo, mock_openai_class):
    # Setup mocks
    mock_retriever_instance = MagicMock()
    mock_retriever_class.return_value = mock_retriever_instance
    
    mock_search_result = MagicMock()
    mock_item = MagicMock()
    mock_item.content = "Google - DEVELOPED - Gemini"
    mock_search_result.items = [mock_item]
    mock_retriever_instance.search.return_value = mock_search_result
    
    mock_openai_instance = MagicMock()
    mock_openai_class.return_value = mock_openai_instance
    mock_chat = MagicMock()
    mock_chat.choices = [MagicMock(message=MagicMock(content="Google phát triển Gemini."))]
    mock_chat.usage = MagicMock(prompt_tokens=30, completion_tokens=10)
    mock_openai_instance.chat.completions.create.return_value = mock_chat
    
    service = SearchService()
    service.client = mock_openai_instance
    # Inject mocked retriever
    service._graph_retriever = mock_retriever_instance
    
    request = QueryRequest(query="Google phát triển cái gì?", method="hybrid", top_k=1)
    
    response = await service.perform_graph_search(request)
    
    assert response.status == "success"
    assert "Gemini" in response.answer
    assert "Google - DEVELOPED - Gemini" in response.context
    assert mock_retriever_instance.search.called
