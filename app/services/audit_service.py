"""
Audit logging service
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
from pymongo import MongoClient, ASCENDING, DESCENDING
from collections import defaultdict

from app.models.audit import (
    AuditLog, AuditAction, AuditSeverity,
    AuditQuery, AuditStatistics
)


class AuditService:
    """Service for audit logging and compliance tracking"""

    def __init__(self):
        """Initialize audit service"""
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None

    async def initialize(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "content_blocks"):
        """
        Initialize MongoDB connection

        Args:
            mongo_uri: MongoDB connection URI
            db_name: Database name
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db["audit_logs"]

        # Create indexes for efficient querying
        self.collection.create_index([("timestamp", DESCENDING)])
        self.collection.create_index([("user_id", ASCENDING)])
        self.collection.create_index([("tenant_id", ASCENDING)])
        self.collection.create_index([("action", ASCENDING)])
        self.collection.create_index([("resource_type", ASCENDING)])
        self.collection.create_index([("resource_id", ASCENDING)])
        self.collection.create_index([("severity", ASCENDING)])
        self.collection.create_index([("ip_address", ASCENDING)])

        # Compound indexes for common queries
        self.collection.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
        self.collection.create_index([("tenant_id", ASCENDING), ("timestamp", DESCENDING)])
        self.collection.create_index([("resource_type", ASCENDING), ("resource_id", ASCENDING)])

        print("✅ AuditService initialized")

    async def shutdown(self):
        """Shutdown MongoDB connection"""
        if self.client:
            self.client.close()
            print("✅ AuditService shutdown")

    async def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        tenant_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> AuditLog:
        """
        Log an audit event

        Args:
            action: Action being performed
            user_id: User ID performing the action
            username: Username
            tenant_id: Tenant ID
            resource_type: Type of resource (block, document, etc.)
            resource_id: ID of the resource
            resource_name: Name of the resource
            severity: Event severity
            description: Human-readable description
            ip_address: Client IP address
            user_agent: Client user agent
            request_id: Request ID for tracing
            method: HTTP method
            endpoint: API endpoint
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
            metadata: Additional metadata
            changes: Changes made (for updates)
            error: Error message (if applicable)
            stack_trace: Stack trace (if applicable)

        Returns:
            Created audit log entry
        """
        audit_id = f"audit_{uuid.uuid4().hex}"

        audit_log = AuditLog(
            id=audit_id,
            action=action,
            severity=severity,
            description=description,
            user_id=user_id,
            username=username,
            tenant_id=tenant_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            response_time_ms=response_time_ms,
            metadata=metadata or {},
            changes=changes,
            error=error,
            stack_trace=stack_trace
        )

        # Insert into database
        self.collection.insert_one(audit_log.dict())

        return audit_log

    async def query(self, query: AuditQuery) -> List[AuditLog]:
        """
        Query audit logs

        Args:
            query: Query parameters

        Returns:
            List of matching audit logs
        """
        # Build MongoDB query
        mongo_query = {}

        if query.user_id:
            mongo_query["user_id"] = query.user_id

        if query.username:
            mongo_query["username"] = query.username

        if query.tenant_id:
            mongo_query["tenant_id"] = query.tenant_id

        if query.action:
            mongo_query["action"] = query.action

        if query.resource_type:
            mongo_query["resource_type"] = query.resource_type

        if query.resource_id:
            mongo_query["resource_id"] = query.resource_id

        if query.severity:
            mongo_query["severity"] = query.severity

        if query.ip_address:
            mongo_query["ip_address"] = query.ip_address

        # Date range
        if query.from_date or query.to_date:
            mongo_query["timestamp"] = {}
            if query.from_date:
                mongo_query["timestamp"]["$gte"] = query.from_date
            if query.to_date:
                mongo_query["timestamp"]["$lte"] = query.to_date

        # Execute query
        cursor = self.collection.find(mongo_query).sort("timestamp", DESCENDING).skip(query.skip).limit(query.limit)

        # Convert to models
        audit_logs = []
        for doc in cursor:
            doc.pop("_id", None)
            audit_logs.append(AuditLog(**doc))

        return audit_logs

    async def get_by_id(self, audit_id: str) -> Optional[AuditLog]:
        """
        Get audit log by ID

        Args:
            audit_id: Audit log ID

        Returns:
            Audit log or None if not found
        """
        doc = self.collection.find_one({"id": audit_id})
        if doc:
            doc.pop("_id", None)
            return AuditLog(**doc)
        return None

    async def get_by_resource(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific resource

        Args:
            resource_type: Resource type
            resource_id: Resource ID
            limit: Maximum number of logs to return

        Returns:
            List of audit logs
        """
        query = AuditQuery(
            resource_type=resource_type,
            resource_id=resource_id,
            limit=limit
        )
        return await self.query(query)

    async def get_by_user(
        self,
        user_id: str,
        limit: int = 100,
        from_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific user

        Args:
            user_id: User ID
            limit: Maximum number of logs to return
            from_date: Optional start date

        Returns:
            List of audit logs
        """
        query = AuditQuery(
            user_id=user_id,
            limit=limit,
            from_date=from_date
        )
        return await self.query(query)

    async def get_statistics(
        self,
        tenant_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> AuditStatistics:
        """
        Get audit log statistics

        Args:
            tenant_id: Optional tenant ID filter
            from_date: Optional start date
            to_date: Optional end date

        Returns:
            Audit statistics
        """
        # Build query
        mongo_query = {}
        if tenant_id:
            mongo_query["tenant_id"] = tenant_id

        if from_date or to_date:
            mongo_query["timestamp"] = {}
            if from_date:
                mongo_query["timestamp"]["$gte"] = from_date
            if to_date:
                mongo_query["timestamp"]["$lte"] = to_date

        # Get all matching logs
        logs = list(self.collection.find(mongo_query))

        if not logs:
            return AuditStatistics(
                total_events=0,
                events_by_action={},
                events_by_severity={},
                events_by_user={},
                events_by_resource_type={},
                failed_operations=0,
                average_response_time_ms=0.0,
                time_range={"from": datetime.utcnow(), "to": datetime.utcnow()}
            )

        # Calculate statistics
        events_by_action = defaultdict(int)
        events_by_severity = defaultdict(int)
        events_by_user = defaultdict(int)
        events_by_resource_type = defaultdict(int)
        failed_operations = 0
        response_times = []

        min_time = logs[0]["timestamp"]
        max_time = logs[0]["timestamp"]

        for log in logs:
            # Count by action
            events_by_action[log["action"]] += 1

            # Count by severity
            events_by_severity[log["severity"]] += 1

            # Count by user
            if log.get("user_id"):
                events_by_user[log["user_id"]] += 1

            # Count by resource type
            if log.get("resource_type"):
                events_by_resource_type[log["resource_type"]] += 1

            # Count failed operations
            if log.get("status_code") and log["status_code"] >= 400:
                failed_operations += 1

            # Collect response times
            if log.get("response_time_ms"):
                response_times.append(log["response_time_ms"])

            # Track time range
            timestamp = log["timestamp"]
            if timestamp < min_time:
                min_time = timestamp
            if timestamp > max_time:
                max_time = timestamp

        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0

        return AuditStatistics(
            total_events=len(logs),
            events_by_action=dict(events_by_action),
            events_by_severity=dict(events_by_severity),
            events_by_user=dict(events_by_user),
            events_by_resource_type=dict(events_by_resource_type),
            failed_operations=failed_operations,
            average_response_time_ms=round(avg_response_time, 2),
            time_range={"from": min_time, "to": max_time}
        )

    async def delete_old_logs(self, days: int = 90) -> int:
        """
        Delete audit logs older than specified days

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted logs
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = self.collection.delete_many({"timestamp": {"$lt": cutoff_date}})
        return result.deleted_count


# Global audit service instance
audit_service = AuditService()


# Import timedelta at top
from datetime import timedelta
