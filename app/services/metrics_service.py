import time
import logging
import json
import threading
from typing import Optional, Dict, Any
from contextlib import contextmanager
from app.core.config import settings

logger = logging.getLogger(__name__)

class MetricsTracker:
    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_latency_ms = 0
        self.total_cost_usd = 0.0
        self.call_count = 0
        self._lock = threading.Lock()

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates cost based on model and token counts."""
        if not model or model not in settings.PRICING:
            return 0.0
        
        pricing = settings.PRICING[model]
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    @contextmanager
    def track(self, operation_name: str, model_name: Optional[str] = None):
        """Context manager to track LLM call metrics with thread safety."""
        start_time = time.perf_counter()
        metrics = {
            "operation": operation_name,
            "model": model_name,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        
        try:
            yield metrics
        finally:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            p_tokens = metrics.get("prompt_tokens", 0)
            c_tokens = metrics.get("completion_tokens", 0)
            cost = self._calculate_cost(model_name, p_tokens, c_tokens)
            
            with self._lock:
                # Update totals
                self.total_latency_ms += latency_ms
                self.total_prompt_tokens += p_tokens
                self.total_completion_tokens += c_tokens
                self.total_cost_usd += cost
                self.call_count += 1
            
            # Log the individual call metrics
            log_data = {
                "event": "llm_call_metrics",
                "operation": operation_name,
                "model": model_name,
                "prompt_tokens": p_tokens,
                "completion_tokens": c_tokens,
                "total_tokens": p_tokens + c_tokens,
                "cost_usd": round(cost, 6),
                "latency_ms": round(latency_ms, 2)
            }
            logger.info(json.dumps(log_data))

    def get_summary(self) -> Dict[str, Any]:
        """Returns a summary of all tracked metrics."""
        with self._lock:
            return {
                "total_calls": self.call_count,
                "total_prompt_tokens": self.total_prompt_tokens,
                "total_completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
                "total_cost_usd": round(self.total_cost_usd, 6),
                "total_latency_ms": round(self.total_latency_ms, 2),
                "average_latency_ms": round(self.total_latency_ms / self.call_count, 2) if self.call_count > 0 else 0
            }

# Global instance for easy access across the application
metrics_tracker = MetricsTracker()
