import time
import logging
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    # Endpoints to exclude from logging to reduce noise
    EXCLUDED_PATHS = ["/health", "/", "/favicon.ico"]

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        process_time = (time.perf_counter() - start_time) * 1000
        
        log_dict = {
            "event": "http_request",
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2)
        }
        
        # Add custom header for latency
        response.headers["X-Process-Time"] = str(round(process_time, 2))
        
        logger.info(json.dumps(log_dict))
        
        return response
