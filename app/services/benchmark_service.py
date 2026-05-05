import json
import os
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from app.services.search_service import search_service
from app.models.schemas import QueryRequest
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class BenchmarkService:
    def __init__(self):
        self.questions_path = "app/data/benchmark_questions.json"
        self.results_dir = settings.BENCHMARK_RESULTS_DIR
        os.makedirs(self.results_dir, exist_ok=True)

    def load_questions(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.questions_path):
            logger.error(f"Questions file not found: {self.questions_path}")
            return []
        with open(self.questions_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("questions", [])

    async def run_full_benchmark(self):
        """
        Runs the full 20-question benchmark for both Vector and Hybrid methods.
        Includes checkpointing and rate limiting.
        """
        questions = self.load_questions()
        if not questions:
            return None

        results = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.results_dir, f"benchmark_results_{timestamp}.json")
        
        logger.info(f"Starting benchmark for {len(questions)} questions...")
        
        for q in questions:
            query = q["query"]
            logger.info(f"Processing Question {q['id']}: {query}")
            
            try:
                # 1. Run Vector RAG
                vector_res = await search_service.perform_vector_search(
                    QueryRequest(query=query, method="vector", top_k=5)
                )
                
                # 2. Run Hybrid RAG
                hybrid_res = await search_service.perform_hybrid_search(
                    QueryRequest(query=query, method="hybrid", top_k=5)
                )
                
                result_item = {
                    "id": q["id"],
                    "category": q["category"],
                    "query": query,
                    "vector": {
                        "answer": vector_res.answer,
                        "latency_ms": vector_res.meta.latency_ms,
                        "tokens": vector_res.meta.tokens
                    },
                    "hybrid": {
                        "answer": hybrid_res.answer,
                        "latency_ms": hybrid_res.meta.latency_ms,
                        "tokens": hybrid_res.meta.tokens
                    }
                }
                results.append(result_item)
                
                # Checkpoint: Save results after each question
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "timestamp": timestamp,
                        "total_questions": len(questions),
                        "completed_questions": len(results),
                        "results": results
                    }, f, ensure_ascii=False, indent=2)
                
                # Rate limiting: Sleep 1s between questions
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing question {q['id']}: {str(e)}")
                # Continue with next question
                continue

        logger.info(f"Benchmark completed. Results finalized at {output_file}")
        return output_file

benchmark_service = BenchmarkService()
