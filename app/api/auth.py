"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List

from app.models.auth import (
    UserCreate, UserPublic, UserUpdate,
    LoginRequest, Token, RefreshTokenRequest,
    APIKeyCreate, APIKeyResponse, APIKey,
    PasswordChangeRequest, User
)
from app.services.auth_service import auth_service


router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


# Dependency: Get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current user from JWT token

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    user = await auth_service.get_current_user(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Dependency: Get current user from API key
async def get_current_user_from_api_key(
    x_api_key: Optional[str] = Header(None)
) -> Optional[User]:
    """
    Get current user from API key header

    Returns None if no API key provided
    """
    if not x_api_key:
        return None

    user = await auth_service.verify_api_key(x_api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return user


# Dependency: Get current user (supports both JWT and API key)
async def get_current_user_flexible(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None)
) -> User:
    """
    Get current user from JWT token or API key

    Tries API key first, then JWT token
    """
    # Try API key first
    if x_api_key:
        user = await auth_service.verify_api_key(x_api_key)
        if user:
            return user

    # Try JWT token
    if credentials:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        if user:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Authentication Endpoints

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user

    - **email**: Valid email address
    - **username**: Alphanumeric username (3-50 chars)
    - **password**: Strong password (min 8 chars)
    - **full_name**: Optional full name
    - **tenant_id**: Optional tenant ID for multi-tenancy
    """
    try:
        user = await auth_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Login with username/email and password

    Returns JWT access and refresh tokens

    - **username**: Username or email address
    - **password**: User password
    """
    user = await auth_service.authenticate_user(
        login_data.username,
        login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = await auth_service.create_tokens(user)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token

    - **refresh_token**: Valid refresh token
    """
    tokens = await auth_service.refresh_access_token(refresh_data.refresh_token)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    return tokens


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(current_user: User = Depends(get_current_user_flexible)):
    """
    Get current user information

    Requires authentication (JWT token or API key)
    """
    return UserPublic(**current_user.dict())


@router.put("/me", response_model=UserPublic)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user information

    Requires JWT authentication
    """
    updated_user = await auth_service.update_user(current_user.id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Change current user's password

    Requires JWT authentication

    - **old_password**: Current password
    - **new_password**: New password (min 8 chars)
    """
    success = await auth_service.change_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    return {"message": "Password changed successfully"}


# API Key Management

@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new API key

    **WARNING**: The API key is only shown once! Save it securely.

    Requires JWT authentication

    - **name**: Descriptive name for the API key
    - **scopes**: List of scopes (read, write, admin)
    - **expires_in_days**: Optional expiration (default: never)
    - **rate_limit**: Optional rate limit (requests per minute)
    """
    api_key = await auth_service.create_api_key(current_user.id, api_key_data)
    return api_key


@router.get("/api-keys", response_model=List[APIKey])
async def list_api_keys(current_user: User = Depends(get_current_user)):
    """
    List all API keys for current user

    Requires JWT authentication

    Note: Key hashes are not returned
    """
    api_keys = await auth_service.list_api_keys(current_user.id)
    return api_keys


@router.delete("/api-keys/{api_key_id}")
async def revoke_api_key(
    api_key_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Revoke (deactivate) an API key

    Requires JWT authentication

    - **api_key_id**: ID of the API key to revoke
    """
    success = await auth_service.revoke_api_key(api_key_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    return {"message": "API key revoked successfully"}


# Admin Endpoints

@router.get("/users", response_model=List[UserPublic])
async def list_users(
    tenant_id: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    List all users (admin only)

    Requires JWT authentication and admin role

    - **tenant_id**: Filter by tenant ID (optional)
    - **limit**: Maximum number of users to return
    - **skip**: Number of users to skip
    """
    # Check if user is admin
    from app.models.auth import UserRole
    if UserRole.ADMIN not in current_user.roles and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    users = await auth_service.list_users(tenant_id, limit, skip)
    return users


@router.get("/users/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID (admin only or own user)

    Requires JWT authentication
    """
    # Check if user is admin or requesting own data
    from app.models.auth import UserRole
    if (UserRole.ADMIN not in current_user.roles and
        not current_user.is_superuser and
        current_user.id != user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    user = await auth_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserPublic(**user.dict())


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete user (admin only)

    Requires JWT authentication and admin role
    """
    # Check if user is admin
    from app.models.auth import UserRole
    if UserRole.ADMIN not in current_user.roles and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Prevent self-deletion
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    success = await auth_service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User deleted successfully"}
