from fastapi import APIRouter, HTTPException
from app.services.loader_service import loader_service
from app.services.graph_service import graph_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/load")
async def load_and_index():
    """
    Triggers the full pipeline: Load documents -> Chunk -> Extract -> Index in Neo4j.
    """
    try:
        # 1. Load documents from data/ directory
        docs = loader_service.load_documents()
        if not docs:
            return {"status": "success", "message": "No documents found in data/ directory"}
            
        # 2. Chunk documents
        chunks = loader_service.chunk_documents(docs)
        
        # 3. Process and index chunks
        summary = graph_service.ingest_documents(chunks)
        
        return {
            "status": "success",
            "message": "Indexing completed successfully",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Indexing API failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
