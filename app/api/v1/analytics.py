from fastapi import APIRouter, HTTPException
from app.services.analytics_service import analytics_service
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/report/{filename}")
async def get_analytics_report(filename: str):
    """
    Generates a detailed cost and performance report for a specific benchmark file.
    """
    report = analytics_service.analyze_file(filename)
    if not report:
        raise HTTPException(status_code=404, detail="Benchmark report not found or invalid")
    
    if "status" in report and report["status"] == "error":
        raise HTTPException(status_code=400, detail=report["message"])
        
    return report

@router.get("/latest")
async def get_latest_report():
    """
    Automatically finds the latest benchmark file and generates a report.
    """
    import os
    results_dir = settings.BENCHMARK_RESULTS_DIR
    if not os.path.exists(results_dir):
        raise HTTPException(status_code=404, detail="No benchmark results found")
    
    files = [f for f in os.listdir(results_dir) if f.startswith("benchmark_results_") and f.endswith(".json")]
    if not files:
        raise HTTPException(status_code=404, detail="No benchmark files found")
    
    latest_file = sorted(files, reverse=True)[0]
    return analytics_service.analyze_file(latest_file)
