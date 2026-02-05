"""
Redis Repository for Caching
Handles caching of blocks, documents, and search results
"""

import os
import json
from typing import Optional, Any
import redis
from datetime import timedelta


class RedisRepository:
    """Repository for Redis caching operations"""

    def __init__(self):
        """Initialize Redis client"""
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)

        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            password=self.redis_password,
            decode_responses=True
        )

        # Default TTL (Time To Live) in seconds
        self.default_ttl = 3600  # 1 hour

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set a value in cache

        :param key: Cache key
        :param value: Value to cache (will be JSON serialized)
        :param ttl: Time to live in seconds (default: 1 hour)
        :return: Success status
        """
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            return self.client.setex(
                name=key,
                time=ttl,
                value=serialized
            )
        except Exception as e:
            print(f"Redis set error for key {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache

        :param key: Cache key
        :return: Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            print(f"Redis get error for key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Delete a key from cache

        :param key: Cache key
        :return: Success status
        """
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Redis delete error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache

        :param key: Cache key
        :return: True if exists, False otherwise
        """
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Redis exists error for key {key}: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for a key

        :param key: Cache key
        :param ttl: Time to live in seconds
        :return: Success status
        """
        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            print(f"Redis expire error for key {key}: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """
        Get remaining TTL for a key

        :param key: Cache key
        :return: TTL in seconds (-1 if no expiration, -2 if not exists)
        """
        try:
            return self.client.ttl(key)
        except Exception as e:
            print(f"Redis TTL error for key {key}: {e}")
            return -2

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter

        :param key: Counter key
        :param amount: Amount to increment (default: 1)
        :return: New value or None on error
        """
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            print(f"Redis increment error for key {key}: {e}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Decrement a counter

        :param key: Counter key
        :param amount: Amount to decrement (default: 1)
        :return: New value or None on error
        """
        try:
            return self.client.decrby(key, amount)
        except Exception as e:
            print(f"Redis decrement error for key {key}: {e}")
            return None

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern

        :param pattern: Pattern to match (e.g., "block:*")
        :return: Number of keys deleted
        """
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis clear pattern error for {pattern}: {e}")
            return 0

    def flush_all(self) -> bool:
        """
        Clear all keys from current database

        Use with caution!
        :return: Success status
        """
        try:
            return self.client.flushdb()
        except Exception as e:
            print(f"Redis flush error: {e}")
            return False

    def get_info(self) -> dict:
        """
        Get Redis server information

        :return: Server info dict
        """
        try:
            info = self.client.info()
            return {
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_keys": self.client.dbsize(),
                "uptime_days": info.get("uptime_in_days")
            }
        except Exception as e:
            print(f"Redis info error: {e}")
            return {}

    def ping(self) -> bool:
        """
        Check if Redis is available

        :return: True if available, False otherwise
        """
        try:
            return self.client.ping()
        except Exception as e:
            print(f"Redis ping error: {e}")
            return False

    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()


# Singleton instance
redis_repo = RedisRepository()
