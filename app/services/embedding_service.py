import logging
from typing import List
from openai import OpenAI
from app.core.config import settings
from app.services.metrics_service import metrics_tracker

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL # text-embedding-3-large

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of texts using OpenAI."""
        if not texts:
            return []
        
        with metrics_tracker.track("generate_embeddings", model_name=self.model) as metrics:
            try:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.model
                )
                
                # Update metrics
                metrics["prompt_tokens"] = response.usage.prompt_tokens
                
                # Extract embeddings
                embeddings = [data.embedding for data in response.data]
                return embeddings
                
            except Exception as e:
                logger.error(f"Embedding generation failed: {str(e)}")
                raise e

# Singleton instance
embedding_service = EmbeddingService()
