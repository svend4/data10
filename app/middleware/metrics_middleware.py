"""
Metrics collection middleware
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

from app.services.metrics_service import metrics_service


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic metrics collection

    Tracks all HTTP requests with latency and status codes
    """

    def __init__(self, app, excluded_paths: list = None):
        """
        Initialize metrics middleware

        Args:
            app: FastAPI application
            excluded_paths: Optional list of paths to exclude from metrics
        """
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/metrics",  # Don't track metrics endpoint itself
            "/health",   # Don't track health checks
            "/docs",
            "/redoc",
            "/openapi.json"
        ]

    async def dispatch(self, request: Request, call_next):
        """
        Process request and collect metrics

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint

        Returns:
            Response
        """
        # Skip excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Get endpoint path (without query params)
        endpoint = request.url.path
        method = request.method

        # Track request in progress and measure duration
        start_time = time.time()

        # Increment in-progress counter
        metrics_service.http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        try:
            # Execute request
            response = await call_next(request)
            status_code = response.status_code

            # Track successful request
            duration = time.time() - start_time
            metrics_service.track_request(method, endpoint, status_code, duration)

            return response

        except Exception as e:
            # Track error
            duration = time.time() - start_time
            metrics_service.track_request(method, endpoint, 500, duration)
            metrics_service.track_error(type(e).__name__, endpoint)
            raise

        finally:
            # Decrement in-progress counter
            metrics_service.http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
