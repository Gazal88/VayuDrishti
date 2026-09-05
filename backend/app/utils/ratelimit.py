"""
Simple in-memory rate limiter — no extra dependencies.
Good enough for a hackathon demo; replace with Redis + slowapi for production.

Usage:
    limiter = RateLimiter(max_calls=20, window_seconds=60)

    @router.post("/advisory")
    async def post_advisory(request: Request, ...):
        limiter.check(request)   # raises HTTP 429 if over limit
        ...
"""

import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self, max_calls: int = 30, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window = window_seconds
        # ip → deque of call timestamps
        self._calls: dict[str, Deque[float]] = defaultdict(deque)

    def _client_ip(self, request: Request) -> str:
        # Respect X-Forwarded-For when behind a proxy (ngrok, Render, etc.)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def check(self, request: Request) -> None:
        ip = self._client_ip(request)
        now = time.monotonic()
        q = self._calls[ip]

        # Drop timestamps outside the window
        while q and now - q[0] > self.window:
            q.popleft()

        if len(q) >= self.max_calls:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded — max {self.max_calls} requests "
                       f"per {self.window}s per IP. Try again shortly.",
            )

        q.append(now)


# Shared instances — import these directly in routers
# Advisory calls Gemini → tight limit (20/min per IP)
advisory_limiter = RateLimiter(max_calls=20, window_seconds=60)

# Dashboard / exposure are free Open-Meteo → relaxed limit
general_limiter  = RateLimiter(max_calls=60, window_seconds=60)
