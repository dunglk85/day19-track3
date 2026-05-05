from fastapi import FastAPI
from pydantic import BaseModel
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI application for Tech Company Corpus GraphRAG",
    version=settings.APP_VERSION
)

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
async def health_check():
    # Placeholder for database connectivity checks in next stories
    return {
        "status": "healthy",
        "databases": {
            "neo4j": "pending",
            "vector_db": "pending"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
