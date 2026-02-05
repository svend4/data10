"""
Authentication and authorization models
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    roles: List[UserRole] = [UserRole.USER]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # API key for programmatic access
    api_key_hash: Optional[str] = None
    api_key_created_at: Optional[datetime] = None

    # Multi-tenancy
    tenant_id: Optional[str] = None

    # Metadata
    metadata: dict = {}

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_abc123",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
                "roles": ["user"],
                "tenant_id": "tenant_xyz"
            }
        }


class UserCreate(BaseModel):
    """User creation request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    tenant_id: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username must be alphanumeric or contain underscores')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecureP@ssw0rd",
                "full_name": "John Doe"
            }
        }


class UserUpdate(BaseModel):
    """User update request"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[UserRole]] = None


class UserInDB(User):
    """User model as stored in database"""
    pass


class UserPublic(BaseModel):
    """Public user model (no sensitive data)"""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool
    roles: List[UserRole]
    created_at: datetime
    tenant_id: Optional[str] = None


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # user_id
    exp: datetime
    iat: datetime
    type: str  # "access" or "refresh"
    roles: List[str] = []
    tenant_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request"""
    username: str  # Can be username or email
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "SecureP@ssw0rd"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class APIKey(BaseModel):
    """API key model"""
    id: str
    user_id: str
    name: str
    key_hash: str
    key_prefix: str  # First 8 chars for identification
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

    # Permissions
    scopes: List[str] = ["read"]  # read, write, admin

    # Rate limiting
    rate_limit: Optional[int] = None  # requests per minute

    class Config:
        json_schema_extra = {
            "example": {
                "id": "apikey_abc123",
                "user_id": "user_xyz",
                "name": "Production API Key",
                "key_prefix": "sk_live_",
                "is_active": True,
                "scopes": ["read", "write"],
                "rate_limit": 1000
            }
        }


class APIKeyCreate(BaseModel):
    """API key creation request"""
    name: str = Field(..., min_length=1, max_length=100)
    scopes: List[str] = ["read"]
    expires_in_days: Optional[int] = None  # None = never expires
    rate_limit: Optional[int] = 1000

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production API Key",
                "scopes": ["read", "write"],
                "expires_in_days": 365,
                "rate_limit": 1000
            }
        }


class APIKeyResponse(BaseModel):
    """API key creation response (includes plain key once)"""
    id: str
    name: str
    key: str  # Plain API key (only shown once!)
    key_prefix: str
    scopes: List[str]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "apikey_abc123",
                "name": "Production API Key",
                "key": "sk_live_1234567890abcdef",
                "key_prefix": "sk_live_",
                "scopes": ["read", "write"],
                "expires_at": "2025-02-05T00:00:00",
                "created_at": "2024-02-05T14:30:00"
            }
        }


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    old_password: str
    new_password: str = Field(..., min_length=8)


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
