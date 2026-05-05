from fastapi import FastAPI, status, Response
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import db
from app.api.v1.search import router as search_router
from app.api.v1.indexing import router as indexing_router
from app.api.v1.benchmark import router as benchmark_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.report import router as report_router
from app.api.middleware import LoggingMiddleware
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting up FastAPI application...")
    try:
        db.connect()
    except Exception as e:
        logger.error(f"Initial Neo4j connection failed during startup: {e}")
    
    yield
    
    # Shutdown logic
    logger.info("Shutting down FastAPI application...")
    db.close()

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI application for Tech Company Corpus GraphRAG",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(LoggingMiddleware)
app.include_router(search_router, prefix="/api/v1")
app.include_router(indexing_router, prefix="/api/v1/indexing", tags=["Indexing"])
app.include_router(benchmark_router, prefix="/api/v1/benchmark", tags=["Benchmark"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(report_router, prefix="/api/v1/report", tags=["Report"])

class StatusResponse(BaseModel):
    status: str
    message: str

@app.get("/", response_model=StatusResponse)
async def root():
    return {
        "status": "success",
        "message": f"{settings.APP_NAME} API is running"
    }

@app.get("/health")
async def health_check(response: Response):
    neo4j_alive = await db.check_health()
    vector_alive = await db.check_vector_health() if neo4j_alive else False

    is_healthy = neo4j_alive and vector_alive
    
    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "databases": {
            "neo4j": "connected" if neo4j_alive else "disconnected",
            "vector_db": "connected" if vector_alive else "disconnected"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
