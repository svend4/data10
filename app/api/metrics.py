"""
Metrics API endpoint for Prometheus
"""

from fastapi import APIRouter, Response
from app.services.metrics_service import metrics_service

router = APIRouter(tags=["monitoring"])


@router.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint

    Returns metrics in Prometheus text format.
    This endpoint should be scraped by Prometheus server.

    **Metrics exposed:**

    - **HTTP metrics**: Request counts, latency, in-progress requests
    - **Authentication**: Login attempts, active sessions, API keys
    - **Database**: Operations, latency, active connections
    - **Blocks**: Total counts, CRUD operations
    - **Documents**: Assembly and export counts
    - **Search**: Query counts, latency, results
    - **ML/NLP**: Request counts, processing time, model status
    - **Cache**: Hits, misses, size, evictions
    - **Rate limiting**: Violations count
    - **Audit**: Event counts by action and severity
    - **Errors**: Error counts by type and endpoint

    **Example Prometheus scrape config:**

    ```yaml
    scrape_configs:
      - job_name: 'content_blocks_api'
        static_configs:
          - targets: ['localhost:8000']
        metrics_path: '/metrics'
        scrape_interval: 15s
    ```
    """
    metrics = metrics_service.generate_metrics()
    content_type = metrics_service.get_content_type()

    return Response(content=metrics, media_type=content_type)
