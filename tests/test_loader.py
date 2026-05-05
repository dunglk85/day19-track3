import pytest
import os
from app.services.loader_service import LoaderService
from langchain_core.documents import Document

def test_loader_service_loading(tmp_path):
    # Setup temporary data directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "test1.txt").write_text("Hello World", encoding="utf-8")
    
    loader = LoaderService(data_dir=str(data_dir))
    docs = loader.load_documents()
    
    assert len(docs) == 1
    assert docs[0].metadata["source_file"] == "test1.txt"
    assert "file_path" in docs[0].metadata
    assert os.path.isabs(docs[0].metadata["file_path"])

def test_loader_service_chunking():
    loader = LoaderService()
    # Use a text that is guaranteed to split based on settings
    long_text = "Word " * 1000 
    doc = Document(page_content=long_text, metadata={"source_file": "long.txt"})
    
    chunks = loader.chunk_documents([doc])
    
    assert len(chunks) > 1
    assert chunks[0].metadata["source_file"] == "long.txt"
    assert "chunk_id" in chunks[0].metadata
    
    # Verify standard Document class
    assert isinstance(chunks[0], Document)
