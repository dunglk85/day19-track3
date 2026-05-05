from fastapi import APIRouter, HTTPException
from app.services.report_service import report_service
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/export/{filename}")
async def export_report(filename: str):
    """
    Generates and saves the final Markdown report for a specific benchmark file.
    """
    path = await report_service.generate_final_report(filename)
    if not path:
        raise HTTPException(status_code=404, detail="Benchmark data not found or analysis failed")
    
    return {"status": "success", "message": f"Report generated at {path}", "path": path}

@router.post("/export-latest")
async def export_latest_report():
    """
    Automatically finds the latest benchmark result and generates the final report.
    """
    import os
    results_dir = settings.BENCHMARK_RESULTS_DIR
    if not os.path.exists(results_dir):
        raise HTTPException(status_code=404, detail="No benchmark results found")
    
    files = [f for f in os.listdir(results_dir) if f.startswith("benchmark_results_") and f.endswith(".json")]
    if not files:
        raise HTTPException(status_code=404, detail="No benchmark files found")
    
    latest_file = sorted(files, reverse=True)[0]
    path = await report_service.generate_final_report(latest_file)
    
    if not path:
        raise HTTPException(status_code=500, detail="Failed to generate report from latest benchmark")
        
    return {"status": "success", "message": f"Report generated at {path}", "path": path}
