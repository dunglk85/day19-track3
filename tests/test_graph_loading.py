import pytest
from unittest.mock import MagicMock, patch
import os

# Set dummy API key
os.environ["OPENAI_API_KEY"] = "sk-dummy"

from app.services.graph_service import GraphService
from app.services.loader_service import Document
from app.models.schemas import ExtractionResult, Entity

@patch("app.services.graph_service.neo4j_repo")
@patch("app.services.graph_service.embedding_service")
@patch("app.services.graph_service.indexing_service")
def test_process_chunk(mock_indexing, mock_embedding, mock_repo):
    # Setup mocks
    mock_indexing.extract_entities.return_value = ExtractionResult(
        entities=[Entity(name="OpenAI", label="Company")],
        relationships=[]
    )
    mock_embedding.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
    
    # Mock repo methods
    mock_repo.merge_entities_batch = MagicMock()
    mock_repo.merge_relationships_batch = MagicMock()
    mock_repo.save_chunk_tx = MagicMock()
    
    service = GraphService()
    chunk = Document(page_content="Test content", metadata={"chunk_id": 0, "source_file": "test.txt"})
    
    res = service.process_chunk(chunk)
    
    assert res["entities"] == 1
    assert res["relationships"] == 0
    assert mock_repo.merge_entities_batch.called
    assert mock_repo.save_chunk_tx.called

@patch("app.services.graph_service.neo4j_repo")
@patch("app.services.graph_service.embedding_service")
@patch("app.services.graph_service.indexing_service")
def test_ingest_documents_summary(mock_indexing, mock_embedding, mock_repo):
    mock_indexing.extract_entities.return_value = ExtractionResult(entities=[], relationships=[])
    mock_embedding.get_embeddings.return_value = [[0.1]]
    
    service = GraphService()
    chunks = [
        Document(page_content="C1", metadata={"chunk_id": 0}),
        Document(page_content="C2", metadata={"chunk_id": 1})
    ]
    
    summary = service.ingest_documents(chunks)
    
    assert summary["total_chunks"] == 2
    assert summary["processed_chunks"] == 2
    assert summary["failed_chunks"] == 0
