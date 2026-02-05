"""
Audit logging middleware
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional
import time
import uuid

from app.models.audit import AuditAction, AuditSeverity
from app.services.audit_service import audit_service


# Map HTTP methods and endpoints to audit actions
ENDPOINT_ACTION_MAP = {
    # Auth endpoints
    ("/api/auth/register", "POST"): AuditAction.REGISTER,
    ("/api/auth/login", "POST"): AuditAction.LOGIN,
    ("/api/auth/change-password", "POST"): AuditAction.PASSWORD_CHANGE,
    ("/api/auth/api-keys", "POST"): AuditAction.API_KEY_CREATE,

    # Block endpoints
    ("/api/blocks", "POST"): AuditAction.BLOCK_CREATE,
    ("/api/blocks", "GET"): AuditAction.BLOCK_READ,

    # Document endpoints
    ("/api/documents/assemble", "POST"): AuditAction.DOCUMENT_ASSEMBLE,

    # Search endpoints
    ("/api/search", "POST"): AuditAction.SEARCH_QUERY,
    ("/api/search/semantic", "POST"): AuditAction.SEMANTIC_SEARCH,

    # ML endpoints
    ("/api/ml/analyze", "POST"): AuditAction.ML_ANALYZE,
    ("/api/ml/classify", "POST"): AuditAction.ML_CLASSIFY,
    ("/api/ml/summarize", "POST"): AuditAction.ML_SUMMARIZE,

    # Bulk endpoints
    ("/api/bulk/create", "POST"): AuditAction.BULK_CREATE,
    ("/api/bulk/update", "POST"): AuditAction.BULK_UPDATE,
    ("/api/bulk/delete", "POST"): AuditAction.BULK_DELETE,
    ("/api/bulk/import", "POST"): AuditAction.BULK_IMPORT,
    ("/api/bulk/export", "POST"): AuditAction.BULK_EXPORT,

    # Template endpoints
    ("/api/templates", "POST"): AuditAction.TEMPLATE_CREATE,

    # User admin endpoints
    ("/api/auth/users", "POST"): AuditAction.USER_CREATE,
}


def get_audit_action(path: str, method: str, resource_id: Optional[str] = None) -> Optional[AuditAction]:
    """
    Determine audit action from path and method

    Args:
        path: Request path
        method: HTTP method
        resource_id: Optional resource ID from path

    Returns:
        AuditAction or None
    """
    # Check exact match first
    key = (path, method)
    if key in ENDPOINT_ACTION_MAP:
        return ENDPOINT_ACTION_MAP[key]

    # Handle dynamic routes with IDs
    if resource_id:
        # Block operations
        if "/api/blocks/" in path:
            if method == "GET":
                return AuditAction.BLOCK_READ
            elif method == "PUT":
                return AuditAction.BLOCK_UPDATE
            elif method == "DELETE":
                return AuditAction.BLOCK_DELETE

        # Document operations
        if "/api/documents/" in path:
            if "export" in path:
                return AuditAction.DOCUMENT_EXPORT
            elif method == "DELETE":
                return AuditAction.DOCUMENT_DELETE

        # Template operations
        if "/api/templates/" in path:
            if method == "PUT":
                return AuditAction.TEMPLATE_UPDATE
            elif method == "DELETE":
                return AuditAction.TEMPLATE_DELETE

        # User operations
        if "/api/auth/users/" in path:
            if method == "PUT":
                return AuditAction.USER_UPDATE
            elif method == "DELETE":
                return AuditAction.USER_DELETE

        # Version restore
        if "/api/versions/" in path and "/restore" in path:
            return AuditAction.BLOCK_RESTORE

        # API key revoke
        if "/api/auth/api-keys/" in path and method == "DELETE":
            return AuditAction.API_KEY_REVOKE

    return None


def extract_resource_info(path: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extract resource type and ID from path

    Args:
        path: Request path

    Returns:
        Tuple of (resource_type, resource_id)
    """
    resource_type = None
    resource_id = None

    # Extract from path segments
    if "/blocks/" in path:
        resource_type = "block"
        parts = path.split("/blocks/")
        if len(parts) > 1:
            resource_id = parts[1].split("/")[0].split("?")[0]

    elif "/documents/" in path:
        resource_type = "document"
        parts = path.split("/documents/")
        if len(parts) > 1:
            resource_id = parts[1].split("/")[0].split("?")[0]

    elif "/templates/" in path:
        resource_type = "template"
        parts = path.split("/templates/")
        if len(parts) > 1:
            resource_id = parts[1].split("/")[0].split("?")[0]

    elif "/users/" in path:
        resource_type = "user"
        parts = path.split("/users/")
        if len(parts) > 1:
            resource_id = parts[1].split("/")[0].split("?")[0]

    return resource_type, resource_id


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic audit logging

    Logs all API requests with user, action, and response information
    """

    def __init__(
        self,
        app,
        excluded_paths: Optional[list] = None,
        log_reads: bool = False
    ):
        """
        Initialize audit middleware

        Args:
            app: FastAPI application
            excluded_paths: Optional list of paths to exclude from audit
            log_reads: Whether to log read operations (can be verbose)
        """
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        self.log_reads = log_reads

    async def dispatch(self, request: Request, call_next):
        """
        Process request and log audit event

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint

        Returns:
            Response
        """
        # Skip excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Skip audit endpoints themselves (prevent recursion)
        if "/api/audit" in request.url.path:
            return await call_next(request)

        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Extract resource info
        resource_type, resource_id = extract_resource_info(request.url.path)

        # Determine audit action
        action = get_audit_action(request.url.path, request.method, resource_id)

        # Skip if no action defined or if read and log_reads is False
        if not action:
            return await call_next(request)

        if action == AuditAction.BLOCK_READ and not self.log_reads:
            return await call_next(request)

        # Get user information (if authenticated)
        user = getattr(request.state, "user", None)
        user_id = user.id if user else None
        username = user.username if user else None
        tenant_id = user.tenant_id if user else None

        # Get client information
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Start timing
        start_time = time.time()

        # Execute request
        response = await call_next(request)

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Determine severity based on status code
        severity = AuditSeverity.INFO
        if response.status_code >= 500:
            severity = AuditSeverity.ERROR
        elif response.status_code >= 400:
            severity = AuditSeverity.WARNING

        # Create audit log
        try:
            await audit_service.log(
                action=action,
                user_id=user_id,
                username=username,
                tenant_id=tenant_id,
                resource_type=resource_type,
                resource_id=resource_id,
                severity=severity,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                response_time_ms=round(response_time_ms, 2)
            )
        except Exception as e:
            # Don't fail the request if audit logging fails
            print(f"⚠️  Failed to log audit event: {e}")

        return response
