import os
import logging
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.services.metrics_service import metrics_tracker
from app.core.config import settings

logger = logging.getLogger(__name__)

class LoaderService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        )

    def load_documents(self) -> List[Document]:
        """Loads all text files from the data directory with robust encoding and metadata."""
        documents = []
        if not os.path.exists(self.data_dir):
            logger.warning(f"Data directory {self.data_dir} does not exist.")
            return documents

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    # Using utf-8-sig to handle BOM and common encoding issues
                    with open(file_path, "r", encoding="utf-8-sig") as f:
                        content = f.read()
                        
                        # Enhanced metadata for traceability
                        metadata = {
                            "source_file": filename,
                            "file_path": os.path.abspath(file_path),
                            "file_size": os.path.getsize(file_path)
                        }
                        
                        documents.append(Document(
                            page_content=content,
                            metadata=metadata
                        ))
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {str(e)}")
        
        logger.info(f"Loaded {len(documents)} documents from {self.data_dir}")
        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Splits documents into semantic chunks using standardized Document class."""
        chunks = []
        with metrics_tracker.track("document_chunking"):
            for doc in documents:
                texts = self.splitter.split_text(doc.page_content)
                for i, text in enumerate(texts):
                    chunk_metadata = doc.metadata.copy()
                    chunk_metadata["chunk_id"] = i
                    chunks.append(Document(
                        page_content=text,
                        metadata=chunk_metadata
                    ))
        
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks

# Singleton instance
loader_service = LoaderService()
