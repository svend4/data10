"""
Unit tests for security utilities
"""

import pytest
from datetime import datetime, timedelta
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    verify_api_key,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


class TestPasswordHashing:
    """Test password hashing utilities"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "MySecurePassword123!"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt hash prefix

    def test_hash_password_different_hashes(self):
        """Test that same password gets different hashes (salt)"""
        password = "MySecurePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different due to random salt

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "MySecurePassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "MySecurePassword123!"
        hashed = hash_password(password)

        assert verify_password("WrongPassword!", hashed) is False

    def test_hash_empty_password(self):
        """Test hashing empty password"""
        hashed = hash_password("")

        assert hashed is not None
        assert verify_password("", hashed) is True

    def test_hash_long_password(self):
        """Test hashing very long password"""
        password = "A" * 1000
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True

    def test_hash_unicode_password(self):
        """Test hashing password with unicode characters"""
        password = "Пароль123!@#$%^&*()"
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Test JWT token utilities"""

    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "user_123", "roles": ["user"]}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": "user_123", "roles": ["user"]}
        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        """Test decoding access token"""
        data = {"sub": "user_123", "roles": ["user"]}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user_123"
        assert decoded["roles"] == ["user"]
        assert decoded["type"] == "access"

    def test_decode_refresh_token(self):
        """Test decoding refresh token"""
        data = {"sub": "user_123", "roles": ["user"]}
        token = create_refresh_token(data)
        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user_123"
        assert decoded["type"] == "refresh"

    def test_token_expiration(self):
        """Test token expiration"""
        data = {"sub": "user_123"}

        # Create token with short expiration (1 second)
        token = create_access_token(data, expires_delta=timedelta(seconds=1))

        # Token should be valid immediately
        decoded = decode_token(token)
        assert decoded is not None

        # Wait for expiration
        import time
        time.sleep(2)

        # Token should be expired
        decoded = decode_token(token)
        assert decoded is None

    def test_invalid_token(self):
        """Test decoding invalid token"""
        decoded = decode_token("invalid.token.here")
        assert decoded is None

    def test_token_contains_metadata(self):
        """Test that token contains required metadata"""
        data = {"sub": "user_123", "roles": ["admin"]}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert "sub" in decoded
        assert "exp" in decoded
        assert "iat" in decoded
        assert "type" in decoded

    def test_token_iat_exp_relationship(self):
        """Test that exp is after iat"""
        data = {"sub": "user_123"}
        token = create_access_token(data)
        decoded = decode_token(token)

        iat = decoded["iat"]
        exp = decoded["exp"]

        # exp should be approximately ACCESS_TOKEN_EXPIRE_MINUTES after iat
        expected_diff = ACCESS_TOKEN_EXPIRE_MINUTES * 60
        actual_diff = exp - iat

        # Allow 1 second tolerance
        assert abs(actual_diff - expected_diff) < 1

    def test_custom_expiration(self):
        """Test token with custom expiration"""
        data = {"sub": "user_123"}
        custom_expires = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_expires)
        decoded = decode_token(token)

        iat = decoded["iat"]
        exp = decoded["exp"]

        # Should expire in 60 minutes
        expected_diff = 60 * 60
        actual_diff = exp - iat

        assert abs(actual_diff - expected_diff) < 1


class TestAPIKeys:
    """Test API key utilities"""

    def test_generate_api_key(self):
        """Test generating API key"""
        api_key = generate_api_key()

        assert api_key is not None
        assert isinstance(api_key, str)
        assert len(api_key) > 20  # Should be reasonably long

    def test_generate_different_keys(self):
        """Test that different API keys are generated"""
        key1 = generate_api_key()
        key2 = generate_api_key()

        assert key1 != key2

    def test_verify_api_key_correct(self):
        """Test verifying correct API key"""
        api_key = generate_api_key()
        hashed_key = hash_password(api_key)

        assert verify_api_key(api_key, hashed_key) is True

    def test_verify_api_key_incorrect(self):
        """Test verifying incorrect API key"""
        api_key = generate_api_key()
        hashed_key = hash_password(api_key)

        wrong_key = generate_api_key()
        assert verify_api_key(wrong_key, hashed_key) is False

    def test_api_key_format(self):
        """Test API key format"""
        api_key = generate_api_key()

        # Should be URL-safe (no special chars)
        import re
        assert re.match(r'^[A-Za-z0-9_-]+$', api_key)


class TestSecurityEdgeCases:
    """Test edge cases and security scenarios"""

    def test_none_password(self):
        """Test handling None password"""
        with pytest.raises(Exception):
            hash_password(None)

    def test_none_token(self):
        """Test decoding None token"""
        decoded = decode_token(None)
        assert decoded is None

    def test_empty_token(self):
        """Test decoding empty token"""
        decoded = decode_token("")
        assert decoded is None

    def test_malformed_token(self):
        """Test decoding malformed token"""
        decoded = decode_token("not.a.valid.token.format")
        assert decoded is None

    def test_token_tampering(self):
        """Test that tampering with token invalidates it"""
        data = {"sub": "user_123"}
        token = create_access_token(data)

        # Tamper with token (change one character)
        if len(token) > 10:
            tampered = token[:10] + "X" + token[11:]
            decoded = decode_token(tampered)
            assert decoded is None

    def test_password_hash_timing_attack_resistance(self):
        """Test that password verification is timing attack resistant"""
        import time

        password = "MySecurePassword123!"
        hashed = hash_password(password)

        # Time correct password
        start = time.time()
        verify_password(password, hashed)
        time_correct = time.time() - start

        # Time incorrect password
        start = time.time()
        verify_password("WrongPassword!", hashed)
        time_incorrect = time.time() - start

        # Times should be similar (bcrypt is timing-safe)
        # Allow up to 2x difference (generous margin)
        ratio = max(time_correct, time_incorrect) / min(time_correct, time_incorrect)
        assert ratio < 2.0

    def test_token_replay_attack_prevention(self):
        """Test that tokens have unique iat timestamps"""
        data = {"sub": "user_123"}

        import time

        token1 = create_access_token(data)
        time.sleep(0.1)  # Small delay
        token2 = create_access_token(data)

        # Tokens should be different due to different iat
        assert token1 != token2

        decoded1 = decode_token(token1)
        decoded2 = decode_token(token2)

        # iat should be different
        assert decoded1["iat"] != decoded2["iat"]
