import time
from collections import defaultdict, deque

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_limit: int, window_seconds: int) -> None:
        super().__init__(app)
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self.buckets: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        identifier = f"{request.client.host if request.client else 'unknown'}:{request.url.path}"
        now = time.time()
        bucket = self.buckets[identifier]
        while bucket and bucket[0] <= now - self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.default_limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
            )
        bucket.append(now)
        return await call_next(request)

