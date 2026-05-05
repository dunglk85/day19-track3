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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
