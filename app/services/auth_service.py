"""
Authentication service for user management and JWT tokens
"""

from datetime import datetime, timedelta
from typing import Optional, List
import uuid
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

from app.models.auth import (
    User, UserCreate, UserUpdate, UserInDB, UserPublic,
    Token, TokenPayload, APIKey, APIKeyCreate, APIKeyResponse,
    UserRole
)
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_api_key, verify_api_key,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)


class AuthService:
    """Authentication service"""

    def __init__(self):
        """Initialize auth service"""
        self.client: Optional[MongoClient] = None
        self.db = None
        self.users_collection = None
        self.api_keys_collection = None

    async def initialize(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "content_blocks"):
        """
        Initialize MongoDB connection

        Args:
            mongo_uri: MongoDB connection URI
            db_name: Database name
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.users_collection = self.db["users"]
        self.api_keys_collection = self.db["api_keys"]

        # Create indexes
        self.users_collection.create_index([("email", ASCENDING)], unique=True)
        self.users_collection.create_index([("username", ASCENDING)], unique=True)
        self.users_collection.create_index([("tenant_id", ASCENDING)])
        self.api_keys_collection.create_index([("user_id", ASCENDING)])
        self.api_keys_collection.create_index([("key_prefix", ASCENDING)])

        print("✅ AuthService initialized")

    async def shutdown(self):
        """Shutdown MongoDB connection"""
        if self.client:
            self.client.close()
            print("✅ AuthService shutdown")

    # User Management

    async def create_user(self, user_data: UserCreate) -> UserPublic:
        """
        Create a new user

        Args:
            user_data: User creation data

        Returns:
            Created user (public data)

        Raises:
            ValueError: If email or username already exists
        """
        # Check if user exists
        if self.users_collection.find_one({"email": user_data.email}):
            raise ValueError("Email already registered")

        if self.users_collection.find_one({"username": user_data.username}):
            raise ValueError("Username already taken")

        # Create user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        hashed_password = hash_password(user_data.password)

        user = User(
            id=user_id,
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            tenant_id=user_data.tenant_id
        )

        # Insert into database
        try:
            self.users_collection.insert_one(user.dict())
        except DuplicateKeyError as e:
            raise ValueError("User with this email or username already exists")

        return UserPublic(**user.dict())

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_data = self.users_collection.find_one({"id": user_id})
        if user_data:
            user_data.pop("_id", None)
            return User(**user_data)
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = self.users_collection.find_one({"email": email})
        if user_data:
            user_data.pop("_id", None)
            return User(**user_data)
        return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        user_data = self.users_collection.find_one({"username": username})
        if user_data:
            user_data.pop("_id", None)
            return User(**user_data)
        return None

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserPublic]:
        """
        Update user

        Args:
            user_id: User ID
            user_update: Fields to update

        Returns:
            Updated user or None if not found
        """
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()

        result = self.users_collection.update_one(
            {"id": user_id},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            user = await self.get_user_by_id(user_id)
            return UserPublic(**user.dict()) if user else None

        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        result = self.users_collection.delete_one({"id": user_id})
        return result.deleted_count > 0

    async def list_users(
        self,
        tenant_id: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[UserPublic]:
        """List users with optional filtering"""
        query = {}
        if tenant_id:
            query["tenant_id"] = tenant_id

        users_data = self.users_collection.find(query).skip(skip).limit(limit)
        users = []
        for user_data in users_data:
            user_data.pop("_id", None)
            users.append(UserPublic(**user_data))

        return users

    # Authentication

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username/email and password

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            User if authenticated, None otherwise
        """
        # Try username first
        user = await self.get_user_by_username(username)

        # Try email if not found
        if not user:
            user = await self.get_user_by_email(username)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        # Update last login
        self.users_collection.update_one(
            {"id": user.id},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return user

    async def create_tokens(self, user: User) -> Token:
        """
        Create access and refresh tokens for user

        Args:
            user: User to create tokens for

        Returns:
            Token object with access and refresh tokens
        """
        token_data = {
            "sub": user.id,
            "roles": [role.value for role in user.roles],
            "tenant_id": user.tenant_id
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def refresh_access_token(self, refresh_token: str) -> Optional[Token]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            New token pair or None if invalid
        """
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        user = await self.get_user_by_id(user_id)

        if not user or not user.is_active:
            return None

        return await self.create_tokens(user)

    async def verify_token(self, token: str) -> Optional[TokenPayload]:
        """
        Verify and decode token

        Args:
            token: JWT token

        Returns:
            Token payload or None if invalid
        """
        payload = decode_token(token)
        if not payload:
            return None

        try:
            return TokenPayload(**payload)
        except Exception:
            return None

    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current user from token

        Args:
            token: JWT token

        Returns:
            User or None if invalid
        """
        payload = await self.verify_token(token)
        if not payload:
            return None

        user = await self.get_user_by_id(payload.sub)
        if not user or not user.is_active:
            return None

        return user

    # API Keys

    async def create_api_key(self, user_id: str, api_key_data: APIKeyCreate) -> APIKeyResponse:
        """
        Create API key for user

        Args:
            user_id: User ID
            api_key_data: API key creation data

        Returns:
            API key response with plain key (shown once!)
        """
        # Generate API key
        api_key = generate_api_key()
        key_prefix = f"sk_{api_key[:8]}"
        key_hash = hash_password(api_key)

        # Calculate expiration
        expires_at = None
        if api_key_data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=api_key_data.expires_in_days)

        # Create API key record
        api_key_id = f"apikey_{uuid.uuid4().hex[:12]}"
        api_key_record = APIKey(
            id=api_key_id,
            user_id=user_id,
            name=api_key_data.name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=api_key_data.scopes,
            rate_limit=api_key_data.rate_limit,
            expires_at=expires_at
        )

        self.api_keys_collection.insert_one(api_key_record.dict())

        return APIKeyResponse(
            id=api_key_id,
            name=api_key_data.name,
            key=api_key,  # Plain key - only shown once!
            key_prefix=key_prefix,
            scopes=api_key_data.scopes,
            expires_at=expires_at,
            created_at=api_key_record.created_at
        )

    async def verify_api_key(self, api_key: str) -> Optional[User]:
        """
        Verify API key and return associated user

        Args:
            api_key: Plain API key

        Returns:
            User if valid, None otherwise
        """
        # Find API key by prefix
        key_prefix = f"sk_{api_key[:8]}"
        api_key_data = self.api_keys_collection.find_one({"key_prefix": key_prefix})

        if not api_key_data:
            return None

        api_key_data.pop("_id", None)
        api_key_record = APIKey(**api_key_data)

        # Verify key
        if not verify_password(api_key, api_key_record.key_hash):
            return None

        # Check if active
        if not api_key_record.is_active:
            return None

        # Check expiration
        if api_key_record.expires_at and api_key_record.expires_at < datetime.utcnow():
            return None

        # Update last used
        self.api_keys_collection.update_one(
            {"id": api_key_record.id},
            {"$set": {"last_used": datetime.utcnow()}}
        )

        # Get user
        user = await self.get_user_by_id(api_key_record.user_id)
        return user

    async def list_api_keys(self, user_id: str) -> List[APIKey]:
        """List API keys for user (without hashes)"""
        api_keys_data = self.api_keys_collection.find({"user_id": user_id})
        api_keys = []
        for api_key_data in api_keys_data:
            api_key_data.pop("_id", None)
            api_keys.append(APIKey(**api_key_data))

        return api_keys

    async def revoke_api_key(self, api_key_id: str, user_id: str) -> bool:
        """Revoke (deactivate) API key"""
        result = self.api_keys_collection.update_one(
            {"id": api_key_id, "user_id": user_id},
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0

    # Password Management

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            True if successful, False otherwise
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            return False

        # Update password
        new_hash = hash_password(new_password)
        result = self.users_collection.update_one(
            {"id": user_id},
            {"$set": {"hashed_password": new_hash, "updated_at": datetime.utcnow()}}
        )

        return result.modified_count > 0


# Global auth service instance
auth_service = AuthService()
