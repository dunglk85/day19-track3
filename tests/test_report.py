import pytest
import os
from app.services.report_service import report_service

@pytest.mark.asyncio
async def test_generate_final_report_success():
    # Use the test benchmark file created in story 4.2
    filename = "benchmark_results_test.json"
    path = await report_service.generate_final_report(filename)
    
    assert path != ""
    assert os.path.exists(path)
    assert "final_report_" in path
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "# Final Lab Report" in content
        assert "## 1. Kiến trúc Hệ thống" in content
        assert "```mermaid" in content
        assert "Vector RAG (Baseline)" in content

@pytest.mark.asyncio
async def test_get_graph_mermaid():
    mermaid = await report_service.get_graph_mermaid(5)
    assert "graph TD" in mermaid
    # Depending on DB content, there might be actual edges
    # At minimum it shouldn't crash
