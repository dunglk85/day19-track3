from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "GraphRAG-Tech-Company-Corpus"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Neo4j Configuration
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None

    # Model Selection
    MODEL_NAME_INDEXING: str = "gpt-4o"
    MODEL_NAME_QUERY: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Pricing per 1M tokens (USD)
    PRICING: dict = {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60}
    }

    # Chunking Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100

    # Storage Paths
    BENCHMARK_RESULTS_DIR: str = "submissions/benchmark-results"
    REPORTS_DIR: str = "submissions/reports"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
