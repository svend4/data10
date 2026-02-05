"""
Prometheus metrics service
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional
import time


class MetricsService:
    """Service for collecting and exposing Prometheus metrics"""

    def __init__(self):
        """Initialize metrics"""
        # Application info
        self.app_info = Info('app_info', 'Application information')
        self.app_info.info({
            'version': '4.0.0',
            'name': 'Dynamic Content Blocks API',
            'phase': '4'
        })

        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )

        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request latency',
            ['method', 'endpoint']
        )

        self.http_requests_in_progress = Gauge(
            'http_requests_in_progress',
            'HTTP requests currently being processed',
            ['method', 'endpoint']
        )

        # Authentication metrics
        self.auth_attempts_total = Counter(
            'auth_attempts_total',
            'Total authentication attempts',
            ['method', 'status']  # method=jwt/apikey, status=success/failure
        )

        self.active_sessions = Gauge(
            'active_sessions',
            'Number of active user sessions'
        )

        self.api_keys_total = Gauge(
            'api_keys_total',
            'Total number of active API keys'
        )

        # Database metrics
        self.db_operations_total = Counter(
            'db_operations_total',
            'Total database operations',
            ['database', 'operation', 'status']
        )

        self.db_operation_duration_seconds = Histogram(
            'db_operation_duration_seconds',
            'Database operation latency',
            ['database', 'operation']
        )

        self.db_connections_active = Gauge(
            'db_connections_active',
            'Active database connections',
            ['database']
        )

        # Block metrics
        self.blocks_total = Gauge(
            'blocks_total',
            'Total number of blocks',
            ['type']
        )

        self.blocks_created_total = Counter(
            'blocks_created_total',
            'Total blocks created',
            ['type']
        )

        self.blocks_updated_total = Counter(
            'blocks_updated_total',
            'Total blocks updated',
            ['type']
        )

        self.blocks_deleted_total = Counter(
            'blocks_deleted_total',
            'Total blocks deleted',
            ['type']
        )

        # Document metrics
        self.documents_assembled_total = Counter(
            'documents_assembled_total',
            'Total documents assembled'
        )

        self.documents_exported_total = Counter(
            'documents_exported_total',
            'Total documents exported',
            ['format']  # text, markdown, docx
        )

        # Search metrics
        self.search_queries_total = Counter(
            'search_queries_total',
            'Total search queries',
            ['type']  # keyword, semantic
        )

        self.search_duration_seconds = Histogram(
            'search_duration_seconds',
            'Search query latency',
            ['type']
        )

        self.search_results_count = Histogram(
            'search_results_count',
            'Number of search results',
            ['type']
        )

        # ML metrics
        self.ml_requests_total = Counter(
            'ml_requests_total',
            'Total ML/NLP requests',
            ['operation']  # analyze, classify, summarize, embedding
        )

        self.ml_processing_duration_seconds = Histogram(
            'ml_processing_duration_seconds',
            'ML processing latency',
            ['operation']
        )

        self.ml_model_loaded = Gauge(
            'ml_model_loaded',
            'ML model loaded status',
            ['model']
        )

        # Cache metrics
        self.cache_hits_total = Counter(
            'cache_hits_total',
            'Total cache hits'
        )

        self.cache_misses_total = Counter(
            'cache_misses_total',
            'Total cache misses'
        )

        self.cache_size_bytes = Gauge(
            'cache_size_bytes',
            'Current cache size in bytes'
        )

        self.cache_evictions_total = Counter(
            'cache_evictions_total',
            'Total cache evictions'
        )

        # Rate limiting metrics
        self.rate_limit_exceeded_total = Counter(
            'rate_limit_exceeded_total',
            'Total rate limit violations',
            ['identifier_type']  # user, ip
        )

        # Audit metrics
        self.audit_events_total = Counter(
            'audit_events_total',
            'Total audit events',
            ['action', 'severity']
        )

        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['type', 'endpoint']
        )

        print("✅ MetricsService initialized")

    # HTTP request tracking

    def track_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """
        Track HTTP request

        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: Response status code
            duration: Request duration in seconds
        """
        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status_code).inc()
        self.http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

    def request_in_progress(self, method: str, endpoint: str):
        """Context manager for tracking requests in progress"""
        class RequestContext:
            def __init__(self, metrics, method, endpoint):
                self.metrics = metrics
                self.method = method
                self.endpoint = endpoint
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                self.metrics.http_requests_in_progress.labels(method=self.method, endpoint=self.endpoint).inc()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.metrics.http_requests_in_progress.labels(method=self.method, endpoint=self.endpoint).dec()
                duration = time.time() - self.start_time
                return False

        return RequestContext(self, method, endpoint)

    # Authentication metrics

    def track_auth_attempt(self, method: str, success: bool):
        """Track authentication attempt"""
        status = "success" if success else "failure"
        self.auth_attempts_total.labels(method=method, status=status).inc()

    def set_active_sessions(self, count: int):
        """Set active sessions count"""
        self.active_sessions.set(count)

    def set_api_keys_total(self, count: int):
        """Set total API keys count"""
        self.api_keys_total.set(count)

    # Database metrics

    def track_db_operation(self, database: str, operation: str, success: bool, duration: float):
        """Track database operation"""
        status = "success" if success else "failure"
        self.db_operations_total.labels(database=database, operation=operation, status=status).inc()
        self.db_operation_duration_seconds.labels(database=database, operation=operation).observe(duration)

    def set_db_connections(self, database: str, count: int):
        """Set active database connections"""
        self.db_connections_active.labels(database=database).set(count)

    # Block metrics

    def set_blocks_total(self, block_type: str, count: int):
        """Set total blocks count"""
        self.blocks_total.labels(type=block_type).set(count)

    def track_block_created(self, block_type: str):
        """Track block creation"""
        self.blocks_created_total.labels(type=block_type).inc()

    def track_block_updated(self, block_type: str):
        """Track block update"""
        self.blocks_updated_total.labels(type=block_type).inc()

    def track_block_deleted(self, block_type: str):
        """Track block deletion"""
        self.blocks_deleted_total.labels(type=block_type).inc()

    # Document metrics

    def track_document_assembled(self):
        """Track document assembly"""
        self.documents_assembled_total.inc()

    def track_document_exported(self, format: str):
        """Track document export"""
        self.documents_exported_total.labels(format=format).inc()

    # Search metrics

    def track_search_query(self, search_type: str, duration: float, results_count: int):
        """Track search query"""
        self.search_queries_total.labels(type=search_type).inc()
        self.search_duration_seconds.labels(type=search_type).observe(duration)
        self.search_results_count.labels(type=search_type).observe(results_count)

    # ML metrics

    def track_ml_request(self, operation: str, duration: float):
        """Track ML/NLP request"""
        self.ml_requests_total.labels(operation=operation).inc()
        self.ml_processing_duration_seconds.labels(operation=operation).observe(duration)

    def set_ml_model_status(self, model: str, loaded: bool):
        """Set ML model loaded status"""
        self.ml_model_loaded.labels(model=model).set(1 if loaded else 0)

    # Cache metrics

    def track_cache_hit(self):
        """Track cache hit"""
        self.cache_hits_total.inc()

    def track_cache_miss(self):
        """Track cache miss"""
        self.cache_misses_total.inc()

    def set_cache_size(self, size_bytes: int):
        """Set cache size"""
        self.cache_size_bytes.set(size_bytes)

    def track_cache_eviction(self):
        """Track cache eviction"""
        self.cache_evictions_total.inc()

    # Rate limiting metrics

    def track_rate_limit_exceeded(self, identifier_type: str):
        """Track rate limit violation"""
        self.rate_limit_exceeded_total.labels(identifier_type=identifier_type).inc()

    # Audit metrics

    def track_audit_event(self, action: str, severity: str):
        """Track audit event"""
        self.audit_events_total.labels(action=action, severity=severity).inc()

    # Error metrics

    def track_error(self, error_type: str, endpoint: str):
        """Track error"""
        self.errors_total.labels(type=error_type, endpoint=endpoint).inc()

    # Metrics export

    def generate_metrics(self) -> bytes:
        """
        Generate Prometheus metrics

        Returns:
            Metrics in Prometheus text format
        """
        return generate_latest()

    def get_content_type(self) -> str:
        """
        Get content type for metrics

        Returns:
            Content type string
        """
        return CONTENT_TYPE_LATEST


# Global metrics service instance
metrics_service = MetricsService()
