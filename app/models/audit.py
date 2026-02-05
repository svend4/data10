"""
Audit logging models
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AuditAction(str, Enum):
    """Audit action types"""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    PASSWORD_CHANGE = "password_change"
    API_KEY_CREATE = "api_key_create"
    API_KEY_REVOKE = "api_key_revoke"

    # Blocks
    BLOCK_CREATE = "block_create"
    BLOCK_READ = "block_read"
    BLOCK_UPDATE = "block_update"
    BLOCK_DELETE = "block_delete"
    BLOCK_RESTORE = "block_restore"

    # Documents
    DOCUMENT_CREATE = "document_create"
    DOCUMENT_ASSEMBLE = "document_assemble"
    DOCUMENT_EXPORT = "document_export"
    DOCUMENT_DELETE = "document_delete"

    # Templates
    TEMPLATE_CREATE = "template_create"
    TEMPLATE_UPDATE = "template_update"
    TEMPLATE_DELETE = "template_delete"

    # Search
    SEARCH_QUERY = "search_query"
    SEMANTIC_SEARCH = "semantic_search"

    # ML
    ML_ANALYZE = "ml_analyze"
    ML_CLASSIFY = "ml_classify"
    ML_SUMMARIZE = "ml_summarize"

    # Bulk operations
    BULK_CREATE = "bulk_create"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"
    BULK_IMPORT = "bulk_import"
    BULK_EXPORT = "bulk_export"

    # Admin
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"


class AuditSeverity(str, Enum):
    """Audit event severity"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(BaseModel):
    """Audit log entry"""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Action details
    action: AuditAction
    severity: AuditSeverity = AuditSeverity.INFO
    description: Optional[str] = None

    # User information
    user_id: Optional[str] = None
    username: Optional[str] = None
    tenant_id: Optional[str] = None

    # Request information
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None

    # Resource information
    resource_type: Optional[str] = None  # block, document, template, user
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None

    # Operation details
    method: Optional[str] = None  # GET, POST, PUT, DELETE
    endpoint: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None

    # Additional data
    metadata: Dict[str, Any] = {}

    # Changes (for update operations)
    changes: Optional[Dict[str, Any]] = None

    # Error details (if applicable)
    error: Optional[str] = None
    stack_trace: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "audit_abc123def456",
                "timestamp": "2024-02-05T14:30:00Z",
                "action": "block_update",
                "severity": "info",
                "description": "Updated block content",
                "user_id": "user_xyz",
                "username": "johndoe",
                "tenant_id": "tenant_123",
                "ip_address": "192.168.1.100",
                "resource_type": "block",
                "resource_id": "block_abc123",
                "method": "PUT",
                "endpoint": "/api/blocks/block_abc123",
                "status_code": 200,
                "response_time_ms": 45.2,
                "changes": {
                    "content": {
                        "old": "Old content",
                        "new": "New content"
                    }
                }
            }
        }


class AuditQuery(BaseModel):
    """Query parameters for audit log search"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    tenant_id: Optional[str] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    severity: Optional[AuditSeverity] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    ip_address: Optional[str] = None
    limit: int = 100
    skip: int = 0


class AuditStatistics(BaseModel):
    """Audit log statistics"""
    total_events: int
    events_by_action: Dict[str, int]
    events_by_severity: Dict[str, int]
    events_by_user: Dict[str, int]
    events_by_resource_type: Dict[str, int]
    failed_operations: int
    average_response_time_ms: float
    time_range: Dict[str, datetime]

    class Config:
        json_schema_extra = {
            "example": {
                "total_events": 1234,
                "events_by_action": {
                    "block_create": 345,
                    "block_update": 567,
                    "login": 123
                },
                "events_by_severity": {
                    "info": 1100,
                    "warning": 100,
                    "error": 34
                },
                "events_by_user": {
                    "user_123": 456,
                    "user_456": 234
                },
                "events_by_resource_type": {
                    "block": 678,
                    "document": 345
                },
                "failed_operations": 34,
                "average_response_time_ms": 125.5,
                "time_range": {
                    "from": "2024-02-01T00:00:00Z",
                    "to": "2024-02-05T23:59:59Z"
                }
            }
        }
