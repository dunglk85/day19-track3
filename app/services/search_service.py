import logging
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings
from app.repositories.neo4j_repo import neo4j_repo
from app.services.embedding_service import embedding_service
from app.services.metrics_service import metrics_tracker
from app.models.schemas import QueryRequest, QueryResponse, SearchMeta
import time
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.repo = neo4j_repo
        self.embedding_service = embedding_service
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.gen_model = settings.MODEL_NAME_QUERY
        self.vector_index_name = "chunk_vector_index"

    async def perform_vector_search(self, request: QueryRequest) -> QueryResponse:
        """Performs a standard Vector-only RAG search."""
        start_time = time.perf_counter()
        
        # 1. Generate query embedding
        query_vector = self.embedding_service.get_embeddings([request.query])[0]
        
        # 2. Search for top-K chunks
        search_results = self.repo.vector_search(
            index_name=self.vector_index_name,
            query_vector=query_vector,
            top_k=request.top_k
        )
        
        context_chunks = [res["text"] for res in search_results]
        
        # 3. Guard against context overflow (simple character limit for now)
        # 128k context is approx 500k characters. Let's limit to 400k.
        max_chars = 400000
        context_text = ""
        for chunk in context_chunks:
            if len(context_text) + len(chunk) < max_chars:
                context_text += chunk + "\n\n"
            else:
                logger.warning("Context truncated due to length limits")
                break
        
        # 4. Generate answer using LLM
        prompt = f"""Bạn là một trợ lý AI thông minh. Hãy trả lời câu hỏi của người dùng dựa TRỰC TIẾP và DUY NHẤT vào ngữ cảnh được cung cấp dưới đây. 
Nếu thông tin không có trong ngữ cảnh, hãy nói rằng bạn không biết, đừng tự ý bịa ra câu trả lời.

Ngữ cảnh:
{context_text}

        Câu hỏi: {request.query}
        Trả lời:"""

        return await self._generate_answer_with_retry(prompt, request.query, context_chunks, start_time)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _generate_answer_with_retry(self, prompt: str, query: str, context_chunks: List[str], start_time: float) -> QueryResponse:
        with metrics_tracker.track("generate_answer", model_name=self.gen_model) as metrics:
            try:
                response = self.client.chat.completions.create(
                    model=self.gen_model,
                    messages=[
                        {"role": "system", "content": "Bạn là trợ lý phân tích dữ liệu Tech Company Corpus."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                
                answer = response.choices[0].message.content
                metrics["prompt_tokens"] = response.usage.prompt_tokens
                metrics["completion_tokens"] = response.usage.completion_tokens
                
            except Exception as e:
                logger.error(f"Answer generation failed: {str(e)}")
                raise e

        # 5. Construct response with metrics
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        meta = SearchMeta(
            tokens={
                "prompt": metrics["prompt_tokens"],
                "completion": metrics["completion_tokens"],
                "total": metrics["prompt_tokens"] + metrics["completion_tokens"]
            },
            latency_ms=round(latency_ms, 2)
        )

        return QueryResponse(
            answer=answer,
            context=context_chunks,
            meta=meta
        )

# Singleton instance
search_service = SearchService()
