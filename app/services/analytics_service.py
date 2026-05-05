import json
import os
import statistics
from typing import List, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.results_dir = settings.BENCHMARK_RESULTS_DIR

    def calculate_cost(self, tokens: Dict[str, int], model: str = "gpt-4o-mini") -> float:
        if model not in settings.PRICING:
            model = "gpt-4o-mini"
        prices = settings.PRICING[model]
        prompt_cost = (tokens.get("prompt", 0) / 1_000_000) * prices["input"]
        completion_cost = (tokens.get("completion", 0) / 1_000_000) * prices["output"]
        return prompt_cost + completion_cost

    def get_p95(self, data: List[float]) -> float:
        if not data:
            return 0.0
        sorted_data = sorted(data)
        idx = int(0.95 * len(sorted_data))
        return sorted_data[min(idx, len(sorted_data) - 1)]

    def analyze_file(self, filename: str) -> Dict[str, Any]:
        """
        Analyzes a benchmark result file and produces a summary report.
        """
        file_path = os.path.join(self.results_dir, filename)
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read benchmark file: {str(e)}")
            return {}

        results = data.get("results", [])
        
        stats = {
            "vector": {"latencies": [], "prompt_tokens": 0, "completion_tokens": 0},
            "hybrid": {"latencies": [], "prompt_tokens": 0, "completion_tokens": 0}
        }

        for item in results:
            if "error" in item or "vector" not in item or "hybrid" not in item:
                continue
            
            # Vector
            stats["vector"]["latencies"].append(item["vector"]["latency_ms"])
            stats["vector"]["prompt_tokens"] += item["vector"]["tokens"]["prompt"]
            stats["vector"]["completion_tokens"] += item["vector"]["tokens"]["completion"]
            
            # Hybrid
            stats["hybrid"]["latencies"].append(item["hybrid"]["latency_ms"])
            stats["hybrid"]["prompt_tokens"] += item["hybrid"]["tokens"]["prompt"]
            stats["hybrid"]["completion_tokens"] += item["hybrid"]["tokens"]["completion"]

        if not stats["vector"]["latencies"]:
            return {"status": "error", "message": "No valid results found in file"}

        # Final aggregation
        report = {
            "summary": {
                "total_questions": len(results),
                "valid_responses": len(stats["vector"]["latencies"]),
                "timestamp": data.get("timestamp"),
                "file": filename
            },
            "vector": self._summarize_stats(stats["vector"]),
            "hybrid": self._summarize_stats(stats["hybrid"])
        }
        
        # Calculate comparison
        v_mean = report["vector"]["latency"]["mean"]
        h_mean = report["hybrid"]["latency"]["mean"]
        v_cost = report["vector"]["cost_usd"]
        h_cost = report["hybrid"]["cost_usd"]

        report["comparison"] = {
            "latency_increase_pct": round(((h_mean / v_mean) - 1) * 100, 2) if v_mean > 0 else 0,
            "cost_increase_pct": round(((h_cost / v_cost) - 1) * 100, 2) if v_cost > 0 else 0
        }

        return report

    def _summarize_stats(self, s: Dict[str, Any]) -> Dict[str, Any]:
        latencies = s["latencies"]
        return {
            "latency": {
                "mean": round(statistics.mean(latencies), 2) if latencies else 0,
                "p95": round(self.get_p95(latencies), 2),
                "min": round(min(latencies), 2) if latencies else 0,
                "max": round(max(latencies), 2) if latencies else 0
            },
            "tokens": {
                "prompt": s["prompt_tokens"],
                "completion": s["completion_tokens"],
                "total": s["prompt_tokens"] + s["completion_tokens"]
            },
            "cost_usd": round(self.calculate_cost({"prompt": s["prompt_tokens"], "completion": s["completion_tokens"]}), 6)
        }

analytics_service = AnalyticsService()
