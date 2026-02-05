"""
Audit log API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.models.audit import (
    AuditLog, AuditQuery, AuditAction,
    AuditSeverity, AuditStatistics
)
from app.models.auth import User, UserRole
from app.services.audit_service import audit_service
from app.api.auth import get_current_user


router = APIRouter(prefix="/audit", tags=["audit"])


# Dependency: Require admin access
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require admin role

    Raises:
        HTTPException: If user is not admin
    """
    if UserRole.ADMIN not in current_user.roles and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/logs", response_model=List[AuditLog])
async def get_audit_logs(
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    tenant_id: Optional[str] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    severity: Optional[AuditSeverity] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    ip_address: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(require_admin)
):
    """
    Query audit logs (admin only)

    Filter audit logs by various criteria:

    - **user_id**: Filter by user ID
    - **username**: Filter by username
    - **tenant_id**: Filter by tenant ID
    - **action**: Filter by action type
    - **resource_type**: Filter by resource type (block, document, etc.)
    - **resource_id**: Filter by resource ID
    - **severity**: Filter by severity (info, warning, error, critical)
    - **from_date**: Start date (ISO 8601 format)
    - **to_date**: End date (ISO 8601 format)
    - **ip_address**: Filter by IP address
    - **limit**: Maximum number of results (1-1000)
    - **skip**: Number of results to skip
    """
    query = AuditQuery(
        user_id=user_id,
        username=username,
        tenant_id=tenant_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        severity=severity,
        from_date=from_date,
        to_date=to_date,
        ip_address=ip_address,
        limit=limit,
        skip=skip
    )

    logs = await audit_service.query(query)
    return logs


@router.get("/logs/{audit_id}", response_model=AuditLog)
async def get_audit_log(
    audit_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Get audit log by ID (admin only)

    - **audit_id**: Audit log ID
    """
    log = await audit_service.get_by_id(audit_id)

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )

    return log


@router.get("/resources/{resource_type}/{resource_id}", response_model=List[AuditLog])
async def get_resource_audit_logs(
    resource_type: str,
    resource_id: str,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_admin)
):
    """
    Get audit logs for a specific resource (admin only)

    Returns all audit events related to a specific resource

    - **resource_type**: Type of resource (block, document, template, user)
    - **resource_id**: Resource ID
    - **limit**: Maximum number of results (1-1000)
    """
    logs = await audit_service.get_by_resource(resource_type, resource_id, limit)
    return logs


@router.get("/users/{user_id}/logs", response_model=List[AuditLog])
async def get_user_audit_logs(
    user_id: str,
    from_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_admin)
):
    """
    Get audit logs for a specific user (admin only)

    Returns all audit events performed by a specific user

    - **user_id**: User ID
    - **from_date**: Optional start date (ISO 8601 format)
    - **limit**: Maximum number of results (1-1000)
    """
    logs = await audit_service.get_by_user(user_id, limit, from_date)
    return logs


@router.get("/my-activity", response_model=List[AuditLog])
async def get_my_activity(
    from_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's audit logs

    Returns audit events performed by the current user

    - **from_date**: Optional start date (ISO 8601 format)
    - **limit**: Maximum number of results (1-1000)
    """
    logs = await audit_service.get_by_user(current_user.id, limit, from_date)
    return logs


@router.get("/statistics", response_model=AuditStatistics)
async def get_audit_statistics(
    tenant_id: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    current_user: User = Depends(require_admin)
):
    """
    Get audit log statistics (admin only)

    Returns aggregate statistics about audit events:
    - Total events
    - Events by action type
    - Events by severity
    - Events by user
    - Events by resource type
    - Failed operations count
    - Average response time

    - **tenant_id**: Optional tenant ID filter
    - **from_date**: Optional start date (ISO 8601 format)
    - **to_date**: Optional end date (ISO 8601 format)
    """
    stats = await audit_service.get_statistics(tenant_id, from_date, to_date)
    return stats


@router.delete("/logs/cleanup")
async def cleanup_old_logs(
    days: int = Query(90, ge=1, le=3650),
    current_user: User = Depends(require_admin)
):
    """
    Delete old audit logs (admin only)

    Deletes audit logs older than the specified number of days.
    Useful for compliance with data retention policies.

    - **days**: Number of days to keep (default: 90, max: 3650/10 years)
    """
    deleted_count = await audit_service.delete_old_logs(days)

    return {
        "message": f"Deleted {deleted_count} audit logs older than {days} days",
        "deleted_count": deleted_count
    }
