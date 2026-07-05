import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.utils.logging import get_logger

logger = get_logger(__name__)


class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        logger.debug(f"Request:: {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")

        return response