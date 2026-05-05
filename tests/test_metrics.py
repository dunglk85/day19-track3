import pytest
import time
from app.services.metrics_service import MetricsTracker

def test_metrics_tracker_tracking_with_cost():
    tracker = MetricsTracker()
    
    operation = "test_llm_call"
    model = "gpt-4o" # $5/$15 per 1M
    
    with tracker.track(operation, model) as metrics:
        metrics["prompt_tokens"] = 1000000 # 1M tokens
        metrics["completion_tokens"] = 1000000 # 1M tokens
        
    summary = tracker.get_summary()
    
    assert summary["total_calls"] == 1
    assert summary["total_prompt_tokens"] == 1000000
    assert summary["total_completion_tokens"] == 1000000
    # Cost should be $5 + $15 = $20
    assert summary["total_cost_usd"] == 20.0

def test_metrics_tracker_thread_safety():
    import threading
    tracker = MetricsTracker()
    
    def worker():
        for _ in range(100):
            with tracker.track("test", "gpt-4o-mini") as m:
                m["prompt_tokens"] = 10
                m["completion_tokens"] = 10
                
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    summary = tracker.get_summary()
    assert summary["total_calls"] == 1000
    assert summary["total_prompt_tokens"] == 10000
