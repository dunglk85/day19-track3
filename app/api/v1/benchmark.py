from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.services.benchmark_service import benchmark_service
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run")
async def trigger_benchmark(background_tasks: BackgroundTasks):
    """
    Triggers the 20-question benchmark as a background task.
    """
    try:
        # We run it in background because 40 LLM calls (20 q * 2 methods) will take time
        background_tasks.add_task(benchmark_service.run_full_benchmark)
        return {"status": "success", "message": f"Benchmark started in background. Results will be saved to {settings.BENCHMARK_RESULTS_DIR}/"}
    except Exception as e:
        logger.error(f"Failed to start benchmark: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not initiate benchmark")

@router.get("/status")
async def get_benchmark_status():
    """
    Checks the status or list of available benchmark results.
    """
    # Simple implementation: list files in results dir
    import os
    results_dir = settings.BENCHMARK_RESULTS_DIR
    if not os.path.exists(results_dir):
        return {"files": []}
    
    files = sorted(os.listdir(results_dir), reverse=True)
    return {"files": files}
