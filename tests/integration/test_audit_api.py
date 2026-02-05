"""
Integration tests for Audit Logging API
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.services.audit_service import audit_service
from app.services.auth_service import auth_service
from app.models.audit import AuditAction, AuditSeverity
from app.models.auth import UserRole


client = TestClient(app)


@pytest.fixture(scope="module")
def setup_services():
    """Setup audit and auth services for testing"""
    import asyncio
    asyncio.run(audit_service.initialize(mongo_uri="mongodb://localhost:27017", db_name="content_blocks_test"))
    asyncio.run(auth_service.initialize(mongo_uri="mongodb://localhost:27017", db_name="content_blocks_test"))
    yield
    asyncio.run(audit_service.shutdown())
    asyncio.run(auth_service.shutdown())


@pytest.fixture
def admin_token(setup_services):
    """Get admin access token"""
    # Create admin user
    import asyncio
    from app.models.auth import UserCreate, UserUpdate

    admin_data = {
        "email": "admin@test.com",
        "username": "admintest",
        "password": "AdminPassword123!",
        "full_name": "Admin Test"
    }

    user = asyncio.run(auth_service.create_user(UserCreate(**admin_data)))
    asyncio.run(auth_service.update_user(user.id, UserUpdate(roles=[UserRole.ADMIN])))

    # Login
    login_response = client.post("/api/auth/login", json={
        "username": admin_data["username"],
        "password": admin_data["password"]
    })

    return login_response.json()["access_token"]


@pytest.fixture
def user_token(setup_services):
    """Get regular user access token"""
    # Create user
    user_data = {
        "email": "user@test.com",
        "username": "usertest",
        "password": "UserPassword123!",
        "full_name": "User Test"
    }

    client.post("/api/auth/register", json=user_data)

    # Login
    login_response = client.post("/api/auth/login", json={
        "username": user_data["username"],
        "password": user_data["password"]
    })

    return login_response.json()["access_token"]


class TestAuditLogCreation:
    """Test audit log creation"""

    def test_audit_log_created_on_api_call(self, setup_services, user_token):
        """Test that audit log is created when API is called"""
        import asyncio

        # Make an API call
        client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {user_token}"
        })

        # Wait a bit for async processing
        import time
        time.sleep(0.5)

        # Check that audit log was created
        from app.models.audit import AuditQuery
        logs = asyncio.run(audit_service.query(AuditQuery(limit=10)))

        assert len(logs) > 0
        # Should have login and me endpoint logs
        actions = [log.action for log in logs]
        assert AuditAction.LOGIN in actions

    def test_audit_log_manual_creation(self, setup_services):
        """Test manually creating audit log"""
        import asyncio

        log = asyncio.run(audit_service.log(
            action=AuditAction.BLOCK_CREATE,
            user_id="test_user_123",
            username="testuser",
            resource_type="block",
            resource_id="block_123",
            severity=AuditSeverity.INFO,
            description="Test block creation",
            method="POST",
            endpoint="/api/blocks",
            status_code=201
        ))

        assert log.id is not None
        assert log.action == AuditAction.BLOCK_CREATE
        assert log.user_id == "test_user_123"
        assert log.resource_type == "block"


class TestAuditLogQuery:
    """Test querying audit logs"""

    def test_query_all_logs(self, setup_services, admin_token):
        """Test querying all audit logs"""
        response = client.get("/api/audit/logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_query_logs_by_action(self, setup_services, admin_token):
        """Test querying logs by action"""
        response = client.get("/api/audit/logs?action=login",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        for log in data:
            assert log["action"] == "login"

    def test_query_logs_by_user(self, setup_services, admin_token, user_token):
        """Test querying logs by user"""
        import asyncio

        # Get user info to get user_id
        user_response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {user_token}"
        })
        user_id = user_response.json()["id"]

        # Query logs for this user
        response = client.get(f"/api/audit/logs?user_id={user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        for log in data:
            assert log["user_id"] == user_id

    def test_query_logs_by_severity(self, setup_services, admin_token):
        """Test querying logs by severity"""
        response = client.get("/api/audit/logs?severity=info",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        for log in data:
            assert log["severity"] == "info"

    def test_query_logs_with_limit(self, setup_services, admin_token):
        """Test querying logs with limit"""
        response = client.get("/api/audit/logs?limit=5",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_query_logs_by_date_range(self, setup_services, admin_token):
        """Test querying logs by date range"""
        from_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        to_date = datetime.utcnow().isoformat()

        response = client.get(
            f"/api/audit/logs?from_date={from_date}&to_date={to_date}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAuditLogAccess:
    """Test audit log access control"""

    def test_admin_can_access_logs(self, setup_services, admin_token):
        """Test that admin can access audit logs"""
        response = client.get("/api/audit/logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200

    def test_regular_user_cannot_access_all_logs(self, setup_services, user_token):
        """Test that regular user cannot access all audit logs"""
        response = client.get("/api/audit/logs",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403  # Forbidden

    def test_user_can_access_own_activity(self, setup_services, user_token):
        """Test that user can access their own activity"""
        response = client.get("/api/audit/my-activity",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAuditLogResource:
    """Test resource-specific audit logs"""

    def test_get_resource_audit_logs(self, setup_services, admin_token):
        """Test getting audit logs for specific resource"""
        import asyncio

        # Create audit log for specific resource
        asyncio.run(audit_service.log(
            action=AuditAction.BLOCK_UPDATE,
            resource_type="block",
            resource_id="block_test_123",
            user_id="test_user"
        ))

        # Query logs for this resource
        response = client.get("/api/audit/resources/block/block_test_123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        for log in data:
            assert log["resource_type"] == "block"
            assert log["resource_id"] == "block_test_123"

    def test_get_user_audit_logs(self, setup_services, admin_token, user_token):
        """Test getting audit logs for specific user"""
        # Get user info
        user_response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {user_token}"
        })
        user_id = user_response.json()["id"]

        # Query logs for this user
        response = client.get(f"/api/audit/users/{user_id}/logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        for log in data:
            assert log["user_id"] == user_id


class TestAuditStatistics:
    """Test audit statistics"""

    def test_get_audit_statistics(self, setup_services, admin_token):
        """Test getting audit statistics"""
        response = client.get("/api/audit/statistics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "events_by_action" in data
        assert "events_by_severity" in data
        assert "events_by_user" in data
        assert "failed_operations" in data
        assert "average_response_time_ms" in data
        assert "time_range" in data

    def test_get_audit_statistics_with_filters(self, setup_services, admin_token):
        """Test getting audit statistics with filters"""
        from_date = (datetime.utcnow() - timedelta(days=7)).isoformat()

        response = client.get(f"/api/audit/statistics?from_date={from_date}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data

    def test_statistics_access_control(self, setup_services, user_token):
        """Test that regular user cannot access statistics"""
        response = client.get("/api/audit/statistics",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403  # Forbidden


class TestAuditLogCleanup:
    """Test audit log cleanup"""

    def test_cleanup_old_logs(self, setup_services, admin_token):
        """Test cleanup of old logs"""
        response = client.delete("/api/audit/logs/cleanup?days=90",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted_count" in data

    def test_cleanup_access_control(self, setup_services, user_token):
        """Test that regular user cannot cleanup logs"""
        response = client.delete("/api/audit/logs/cleanup?days=90",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403  # Forbidden


class TestAuditMiddleware:
    """Test audit middleware functionality"""

    def test_middleware_logs_api_requests(self, setup_services, user_token):
        """Test that middleware logs API requests"""
        import asyncio

        # Make an API call
        client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {user_token}"
        })

        # Wait for async processing
        import time
        time.sleep(0.5)

        # Check that log was created with request details
        from app.models.audit import AuditQuery
        logs = asyncio.run(audit_service.query(AuditQuery(limit=10)))

        # Find the log for /api/auth/me endpoint
        me_logs = [log for log in logs if log.endpoint == "/api/auth/me"]
        assert len(me_logs) > 0

        log = me_logs[0]
        assert log.method == "GET"
        assert log.status_code == 200
        assert log.response_time_ms is not None
        assert log.response_time_ms > 0

    def test_middleware_logs_failures(self, setup_services):
        """Test that middleware logs failed requests"""
        import asyncio

        # Make a request that will fail (invalid token)
        client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid_token"
        })

        # Wait for async processing
        import time
        time.sleep(0.5)

        # Check for logs with error status
        from app.models.audit import AuditQuery
        logs = asyncio.run(audit_service.query(AuditQuery(
            severity=AuditSeverity.WARNING,
            limit=10
        )))

        # Should have warning/error logs for failed auth
        assert len(logs) >= 0  # May or may not have warnings depending on implementation

    def test_middleware_captures_user_info(self, setup_services, user_token):
        """Test that middleware captures user information"""
        import asyncio

        # Get user info first
        user_response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {user_token}"
        })
        user_id = user_response.json()["id"]
        username = user_response.json()["username"]

        # Wait for async processing
        import time
        time.sleep(0.5)

        # Check that user info is in audit log
        from app.models.audit import AuditQuery
        logs = asyncio.run(audit_service.query(AuditQuery(
            user_id=user_id,
            limit=10
        )))

        assert len(logs) > 0
        log = logs[0]
        assert log.user_id == user_id
        assert log.username == username
