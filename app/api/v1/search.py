from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.search_service import search_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Endpoint thực hiện truy vấn RAG.
    Hỗ trợ method='vector' (Flat RAG) và method='hybrid' (GraphRAG).
    """
    try:
        if request.method == "vector":
            return await search_service.perform_vector_search(request)
        elif request.method == "hybrid":
            return await search_service.perform_graph_search(request)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported search method: {request.method}")
    except Exception as e:
        logger.error(f"Search query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during search processing")
