import pytest
from app.services.analytics_service import analytics_service

def test_analyze_file_success():
    filename = "benchmark_results_test.json"
    report = analytics_service.analyze_file(filename)
    
    assert report["summary"]["total_questions"] == 2
    assert report["vector"]["latency"]["mean"] == 2250.0
    assert report["hybrid"]["latency"]["mean"] == 3500.0
    
    # Check cost calculation (GPT-4o-mini prices)
    # Vector: (100+120)/1M * 0.15 + (50+60)/1M * 0.60 
    # = 220/1M * 0.15 + 110/1M * 0.60 = 0.000033 + 0.000066 = 0.000099
    assert report["vector"]["cost_usd"] == 0.000099
    
    assert report["comparison"]["latency_increase_pct"] > 0
    assert report["comparison"]["cost_increase_pct"] > 0
