import logging
from typing import List, Dict
from app.repositories.neo4j_repo import neo4j_repo
from app.services.embedding_service import embedding_service
from app.services.indexing_service import indexing_service
from app.services.loader_service import Document
from app.models.schemas import ExtractionResult

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self):
        self.repo = neo4j_repo

    def initialize_db(self):
        """Prepares the database (constraints and indexes)."""
        self.repo.create_constraints()
        # text-embedding-3-large is 3072 dims
        self.repo.create_vector_index(
            index_name="chunk_vector_index",
            label="Chunk",
            property="embedding",
            dimensions=3072
        )

    def process_chunk(self, chunk: Document) -> Dict[str, int]:
        """Fully processes a single chunk: Extract -> Embed -> Load."""
        # 1. Extract Entities & Relations
        extraction: ExtractionResult = indexing_service.extract_entities(chunk)
        
        # 2. Merge Entities & Relations in batches
        if extraction.entities:
            self.repo.merge_entities_batch(extraction.entities)
        if extraction.relationships:
            self.repo.merge_relationships_batch(extraction.relationships)
            
        # 3. Generate Embedding for the chunk text
        embedding = embedding_service.get_embeddings([chunk.page_content])[0]
        
        # 4. Save Chunk and link to entities
        self.repo.save_chunk_tx(
            text=chunk.page_content,
            embedding=embedding,
            metadata=chunk.metadata,
            entities=extraction.entities
        )
        
        return {
            "entities": len(extraction.entities),
            "relationships": len(extraction.relationships)
        }

    def ingest_documents(self, chunks: List[Document]) -> Dict[str, int]:
        """Ingests a list of chunks and returns a summary report."""
        self.initialize_db()
        summary = {
            "total_chunks": len(chunks),
            "processed_chunks": 0,
            "failed_chunks": 0,
            "total_entities": 0,
            "total_relationships": 0
        }
        
        for chunk in chunks:
            try:
                res = self.process_chunk(chunk)
                summary["processed_chunks"] += 1
                summary["total_entities"] += res["entities"]
                summary["total_relationships"] += res["relationships"]
            except Exception as e:
                logger.error(f"Failed to ingest chunk: {str(e)}")
                summary["failed_chunks"] += 1
                continue
        
        logger.info(f"Ingestion complete: {summary}")
        return summary

# Singleton instance
graph_service = GraphService()
