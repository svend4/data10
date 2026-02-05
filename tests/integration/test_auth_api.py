"""
Integration tests for Authentication API
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import auth_service
from app.models.auth import UserRole


client = TestClient(app)


@pytest.fixture(scope="module")
def setup_auth_service():
    """Setup auth service for testing"""
    # Initialize auth service
    import asyncio
    asyncio.run(auth_service.initialize(mongo_uri="mongodb://localhost:27017", db_name="content_blocks_test"))
    yield
    # Cleanup
    asyncio.run(auth_service.shutdown())


@pytest.fixture
def test_user():
    """Create a test user"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }


@pytest.fixture
def admin_user():
    """Create an admin user"""
    return {
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "AdminPassword123!",
        "full_name": "Admin User"
    }


class TestUserRegistration:
    """Test user registration"""

    def test_register_new_user(self, setup_auth_service, test_user):
        """Test registering a new user"""
        response = client.post("/api/auth/register", json=test_user)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["username"] == test_user["username"]
        assert data["full_name"] == test_user["full_name"]
        assert "hashed_password" not in data  # Password should not be returned
        assert data["is_active"] is True
        assert UserRole.USER in data["roles"]

    def test_register_duplicate_email(self, setup_auth_service, test_user):
        """Test registering with duplicate email"""
        # Register first user
        client.post("/api/auth/register", json=test_user)

        # Try to register with same email
        duplicate_user = test_user.copy()
        duplicate_user["username"] = "differentusername"
        response = client.post("/api/auth/register", json=duplicate_user)

        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()

    def test_register_duplicate_username(self, setup_auth_service, test_user):
        """Test registering with duplicate username"""
        # Register first user
        client.post("/api/auth/register", json=test_user)

        # Try to register with same username
        duplicate_user = test_user.copy()
        duplicate_user["email"] = "different@example.com"
        response = client.post("/api/auth/register", json=duplicate_user)

        assert response.status_code == 400
        assert "username already taken" in response.json()["detail"].lower()

    def test_register_invalid_email(self, setup_auth_service):
        """Test registering with invalid email"""
        invalid_user = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "Password123!"
        }
        response = client.post("/api/auth/register", json=invalid_user)

        assert response.status_code == 422  # Validation error

    def test_register_weak_password(self, setup_auth_service):
        """Test registering with weak password"""
        weak_password_user = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak"  # Too short
        }
        response = client.post("/api/auth/register", json=weak_password_user)

        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login"""

    def test_login_with_username(self, setup_auth_service, test_user):
        """Test login with username"""
        # Register user
        client.post("/api/auth/register", json=test_user)

        # Login
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # 30 minutes

    def test_login_with_email(self, setup_auth_service, test_user):
        """Test login with email"""
        # Register user
        client.post("/api/auth/register", json=test_user)

        # Login with email
        login_data = {
            "username": test_user["email"],  # Can use email as username
            "password": test_user["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, setup_auth_service, test_user):
        """Test login with wrong password"""
        # Register user
        client.post("/api/auth/register", json=test_user)

        # Login with wrong password
        login_data = {
            "username": test_user["username"],
            "password": "WrongPassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "incorrect username or password" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, setup_auth_service):
        """Test login with nonexistent user"""
        login_data = {
            "username": "nonexistent",
            "password": "Password123!"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401


class TestTokenRefresh:
    """Test token refresh"""

    def test_refresh_access_token(self, setup_auth_service, test_user):
        """Test refreshing access token"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_invalid_token(self, setup_auth_service):
        """Test refreshing with invalid token"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid_token"
        })

        assert response.status_code == 401


class TestCurrentUser:
    """Test getting current user"""

    def test_get_current_user(self, setup_auth_service, test_user):
        """Test getting current user info"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # Get current user
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {access_token}"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["username"] == test_user["username"]

    def test_get_current_user_no_token(self, setup_auth_service):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")

        assert response.status_code == 403  # No authorization header

    def test_get_current_user_invalid_token(self, setup_auth_service):
        """Test getting current user with invalid token"""
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid_token"
        })

        assert response.status_code == 401


class TestPasswordChange:
    """Test password change"""

    def test_change_password(self, setup_auth_service, test_user):
        """Test changing password"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # Change password
        new_password = "NewPassword123!"
        response = client.post("/api/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": test_user["password"],
                "new_password": new_password
            }
        )

        assert response.status_code == 200

        # Verify new password works
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": new_password
        })
        assert login_response.status_code == 200

    def test_change_password_wrong_old_password(self, setup_auth_service, test_user):
        """Test changing password with wrong old password"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # Try to change password with wrong old password
        response = client.post("/api/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": "WrongPassword123!",
                "new_password": "NewPassword123!"
            }
        )

        assert response.status_code == 400


class TestAPIKeys:
    """Test API key management"""

    def test_create_api_key(self, setup_auth_service, test_user):
        """Test creating API key"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # Create API key
        response = client.post("/api/auth/api-keys",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "Test API Key",
                "scopes": ["read", "write"],
                "expires_in_days": 30,
                "rate_limit": 1000
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test API Key"
        assert "key" in data  # Plain key (only shown once)
        assert data["key"].startswith("sk_")
        assert data["scopes"] == ["read", "write"]

    def test_list_api_keys(self, setup_auth_service, test_user):
        """Test listing API keys"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # Create API key
        client.post("/api/auth/api-keys",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"name": "Test Key", "scopes": ["read"]}
        )

        # List API keys
        response = client.get("/api/auth/api-keys",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Test Key"
        assert "key_hash" in data[0]  # Hash is returned
        assert "key" not in data[0]  # Plain key is not returned

    def test_revoke_api_key(self, setup_auth_service, test_user):
        """Test revoking API key"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # Create API key
        create_response = client.post("/api/auth/api-keys",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"name": "Test Key", "scopes": ["read"]}
        )
        api_key_id = create_response.json()["id"]

        # Revoke API key
        response = client.delete(f"/api/auth/api-keys/{api_key_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200

    def test_use_api_key_for_authentication(self, setup_auth_service, test_user):
        """Test using API key for authentication"""
        # Register and login
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # Create API key
        create_response = client.post("/api/auth/api-keys",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"name": "Test Key", "scopes": ["read", "write"]}
        )
        api_key = create_response.json()["key"]

        # Use API key to access endpoint
        response = client.get("/api/auth/me", headers={
            "X-API-Key": api_key
        })

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user["username"]


class TestUserManagement:
    """Test user management (admin)"""

    def test_list_users_as_admin(self, setup_auth_service, admin_user):
        """Test listing users as admin"""
        # Create admin user manually
        import asyncio
        from app.models.auth import UserCreate

        user_create = UserCreate(**admin_user)
        created_user = asyncio.run(auth_service.create_user(user_create))

        # Make user admin
        from app.models.auth import UserUpdate
        asyncio.run(auth_service.update_user(
            created_user.id,
            UserUpdate(roles=[UserRole.ADMIN])
        ))

        # Login as admin
        login_response = client.post("/api/auth/login", json={
            "username": admin_user["username"],
            "password": admin_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # List users
        response = client.get("/api/auth/users",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_list_users_as_non_admin(self, setup_auth_service, test_user):
        """Test listing users as non-admin (should fail)"""
        # Register and login as regular user
        client.post("/api/auth/register", json=test_user)
        login_response = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        })
        access_token = login_response.json()["access_token"]

        # Try to list users
        response = client.get("/api/auth/users",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 403  # Forbidden
