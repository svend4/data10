"""
Rate limiting middleware
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
import time
from collections import defaultdict
import asyncio


class RateLimiter:
    """
    Rate limiter implementation with sliding window algorithm

    Supports both in-memory and Redis backends
    """

    def __init__(
        self,
        redis_client=None,
        default_limit: int = 100,
        window_seconds: int = 60
    ):
        """
        Initialize rate limiter

        Args:
            redis_client: Optional Redis client for distributed rate limiting
            default_limit: Default number of requests allowed per window
            window_seconds: Time window in seconds
        """
        self.redis = redis_client
        self.default_limit = default_limit
        self.window_seconds = window_seconds

        # In-memory storage (fallback if no Redis)
        self.memory_store: Dict[str, list] = defaultdict(list)
        self.cleanup_task = None

    async def start(self):
        """Start background cleanup task"""
        if not self.redis:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop background cleanup task"""
        if self.cleanup_task:
            self.cleanup_task.cancel()

    async def _cleanup_loop(self):
        """Background task to clean up old entries"""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                await self._cleanup_memory()
            except asyncio.CancelledError:
                break

    async def _cleanup_memory(self):
        """Remove old entries from memory store"""
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        keys_to_delete = []
        for key, timestamps in self.memory_store.items():
            # Filter out old timestamps
            self.memory_store[key] = [ts for ts in timestamps if ts > cutoff_time]

            # Mark empty keys for deletion
            if not self.memory_store[key]:
                keys_to_delete.append(key)

        # Delete empty keys
        for key in keys_to_delete:
            del self.memory_store[key]

    async def is_allowed(
        self,
        key: str,
        limit: Optional[int] = None
    ) -> tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed

        Args:
            key: Unique identifier (e.g., user_id, IP address)
            limit: Optional custom limit (overrides default)

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        limit = limit or self.default_limit
        current_time = time.time()
        window_start = current_time - self.window_seconds

        if self.redis:
            return await self._check_redis(key, limit, current_time, window_start)
        else:
            return await self._check_memory(key, limit, current_time, window_start)

    async def _check_redis(
        self,
        key: str,
        limit: int,
        current_time: float,
        window_start: float
    ) -> tuple[bool, Dict[str, int]]:
        """Check rate limit using Redis"""
        redis_key = f"rate_limit:{key}"

        # Remove old entries
        self.redis.zremrangebyscore(redis_key, 0, window_start)

        # Count requests in current window
        current_count = self.redis.zcard(redis_key)

        # Calculate reset time
        oldest_timestamp = self.redis.zrange(redis_key, 0, 0, withscores=True)
        if oldest_timestamp:
            reset_time = int(oldest_timestamp[0][1] + self.window_seconds)
        else:
            reset_time = int(current_time + self.window_seconds)

        rate_limit_info = {
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "reset": reset_time
        }

        if current_count >= limit:
            return False, rate_limit_info

        # Add current request
        self.redis.zadd(redis_key, {str(current_time): current_time})
        self.redis.expire(redis_key, self.window_seconds)

        rate_limit_info["remaining"] -= 1
        return True, rate_limit_info

    async def _check_memory(
        self,
        key: str,
        limit: int,
        current_time: float,
        window_start: float
    ) -> tuple[bool, Dict[str, int]]:
        """Check rate limit using in-memory storage"""
        # Get or create timestamp list
        timestamps = self.memory_store[key]

        # Remove old timestamps
        timestamps = [ts for ts in timestamps if ts > window_start]
        self.memory_store[key] = timestamps

        # Calculate reset time
        if timestamps:
            reset_time = int(timestamps[0] + self.window_seconds)
        else:
            reset_time = int(current_time + self.window_seconds)

        rate_limit_info = {
            "limit": limit,
            "remaining": max(0, limit - len(timestamps)),
            "reset": reset_time
        }

        if len(timestamps) >= limit:
            return False, rate_limit_info

        # Add current timestamp
        timestamps.append(current_time)
        rate_limit_info["remaining"] -= 1

        return True, rate_limit_info


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI

    Applies rate limits to all requests based on user ID or IP address
    """

    def __init__(
        self,
        app,
        rate_limiter: RateLimiter,
        get_identifier: Optional[Callable] = None,
        excluded_paths: Optional[list] = None
    ):
        """
        Initialize rate limit middleware

        Args:
            app: FastAPI application
            rate_limiter: RateLimiter instance
            get_identifier: Optional function to extract identifier from request
            excluded_paths: Optional list of paths to exclude from rate limiting
        """
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.get_identifier = get_identifier or self._default_identifier
        self.excluded_paths = excluded_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]

    def _default_identifier(self, request: Request) -> str:
        """
        Default identifier: use user ID if authenticated, else IP address

        Args:
            request: FastAPI request

        Returns:
            Unique identifier string
        """
        # Try to get user from request state (set by auth middleware)
        user = getattr(request.state, "user", None)
        if user:
            return f"user:{user.id}"

        # Fall back to IP address
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint

        Returns:
            Response or rate limit error
        """
        # Skip excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Get identifier
        identifier = self.get_identifier(request)

        # Check rate limit
        is_allowed, rate_info = await self.rate_limiter.is_allowed(identifier)

        # Add rate limit headers to response
        response = None
        if is_allowed:
            response = await call_next(request)
        else:
            # Rate limit exceeded
            retry_after = rate_info["reset"] - int(time.time())
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": retry_after
                }
            )

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])

        if not is_allowed:
            retry_after = rate_info["reset"] - int(time.time())
            response.headers["Retry-After"] = str(retry_after)

        return response


# Helper functions for route-specific rate limiting

def create_rate_limit_dependency(
    rate_limiter: RateLimiter,
    limit: int,
    window_seconds: Optional[int] = None
):
    """
    Create a dependency for route-specific rate limiting

    Example:
        rate_limit = create_rate_limit_dependency(limiter, limit=10, window_seconds=60)

        @app.get("/api/endpoint")
        async def endpoint(_: None = Depends(rate_limit)):
            return {"message": "Success"}

    Args:
        rate_limiter: RateLimiter instance
        limit: Number of requests allowed
        window_seconds: Optional window (uses limiter's default if not specified)

    Returns:
        Dependency function
    """
    async def rate_limit_dependency(request: Request):
        # Get identifier
        user = getattr(request.state, "user", None)
        if user:
            identifier = f"user:{user.id}"
        else:
            client_host = request.client.host if request.client else "unknown"
            identifier = f"ip:{client_host}"

        # Create custom limiter if window specified
        if window_seconds:
            custom_limiter = RateLimiter(
                redis_client=rate_limiter.redis,
                default_limit=limit,
                window_seconds=window_seconds
            )
            is_allowed, rate_info = await custom_limiter.is_allowed(identifier, limit)
        else:
            is_allowed, rate_info = await rate_limiter.is_allowed(identifier, limit)

        if not is_allowed:
            retry_after = rate_info["reset"] - int(time.time())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(retry_after)
                }
            )

        return None

    return rate_limit_dependency
