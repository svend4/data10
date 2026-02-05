"""
Cache Service for Performance Optimization
Provides caching for blocks, documents, and search results using Redis
"""

from typing import Optional, Any
from app.repositories import redis_repo
from app.models import Block, Document


class CacheService:
    """Service for caching operations"""

    def __init__(self):
        """Initialize CacheService"""
        self.redis = redis_repo

        # Cache key prefixes
        self.BLOCK_PREFIX = "block:"
        self.DOCUMENT_PREFIX = "document:"
        self.SEARCH_PREFIX = "search:"
        self.TEMPLATE_PREFIX = "template:"

        # TTL configurations (in seconds)
        self.BLOCK_TTL = 3600  # 1 hour
        self.DOCUMENT_TTL = 1800  # 30 minutes
        self.SEARCH_TTL = 600  # 10 minutes
        self.TEMPLATE_TTL = 7200  # 2 hours

    async def initialize(self):
        """Initialize cache service"""
        try:
            if self.redis.ping():
                print("✅ Redis cache initialized")
            else:
                print("⚠️  Redis cache not available")
        except Exception as e:
            print(f"⚠️  Redis cache initialization failed: {e}")

    # Block caching methods

    async def get_block(self, block_id: str) -> Optional[dict]:
        """
        Get block from cache

        :param block_id: Block ID
        :return: Block dict or None if not cached
        """
        key = f"{self.BLOCK_PREFIX}{block_id}"
        return self.redis.get(key)

    async def set_block(self, block_id: str, block_data: dict) -> bool:
        """
        Cache a block

        :param block_id: Block ID
        :param block_data: Block data as dict
        :return: Success status
        """
        key = f"{self.BLOCK_PREFIX}{block_id}"
        return self.redis.set(key, block_data, ttl=self.BLOCK_TTL)

    async def delete_block(self, block_id: str) -> bool:
        """
        Remove block from cache

        :param block_id: Block ID
        :return: Success status
        """
        key = f"{self.BLOCK_PREFIX}{block_id}"
        return self.redis.delete(key)

    async def clear_all_blocks(self) -> int:
        """
        Clear all cached blocks

        :return: Number of blocks cleared
        """
        return self.redis.clear_pattern(f"{self.BLOCK_PREFIX}*")

    # Document caching methods

    async def get_document(self, document_id: str) -> Optional[dict]:
        """
        Get document from cache

        :param document_id: Document ID
        :return: Document dict or None if not cached
        """
        key = f"{self.DOCUMENT_PREFIX}{document_id}"
        return self.redis.get(key)

    async def set_document(self, document_id: str, document_data: dict) -> bool:
        """
        Cache a document

        :param document_id: Document ID
        :param document_data: Document data as dict
        :return: Success status
        """
        key = f"{self.DOCUMENT_PREFIX}{document_id}"
        return self.redis.set(key, document_data, ttl=self.DOCUMENT_TTL)

    async def delete_document(self, document_id: str) -> bool:
        """
        Remove document from cache

        :param document_id: Document ID
        :return: Success status
        """
        key = f"{self.DOCUMENT_PREFIX}{document_id}"
        return self.redis.delete(key)

    async def clear_all_documents(self) -> int:
        """
        Clear all cached documents

        :return: Number of documents cleared
        """
        return self.redis.clear_pattern(f"{self.DOCUMENT_PREFIX}*")

    # Search results caching methods

    async def get_search_results(self, query_hash: str) -> Optional[dict]:
        """
        Get search results from cache

        :param query_hash: Hash of search query and filters
        :return: Search results or None if not cached
        """
        key = f"{self.SEARCH_PREFIX}{query_hash}"
        return self.redis.get(key)

    async def set_search_results(
        self,
        query_hash: str,
        results: dict
    ) -> bool:
        """
        Cache search results

        :param query_hash: Hash of search query and filters
        :param results: Search results
        :return: Success status
        """
        key = f"{self.SEARCH_PREFIX}{query_hash}"
        return self.redis.set(key, results, ttl=self.SEARCH_TTL)

    async def clear_search_cache(self) -> int:
        """
        Clear all cached search results

        :return: Number of search results cleared
        """
        return self.redis.clear_pattern(f"{self.SEARCH_PREFIX}*")

    # Template caching methods

    async def get_template(self, template_id: str) -> Optional[dict]:
        """
        Get template from cache

        :param template_id: Template ID
        :return: Template dict or None if not cached
        """
        key = f"{self.TEMPLATE_PREFIX}{template_id}"
        return self.redis.get(key)

    async def set_template(self, template_id: str, template_data: dict) -> bool:
        """
        Cache a template

        :param template_id: Template ID
        :param template_data: Template data as dict
        :return: Success status
        """
        key = f"{self.TEMPLATE_PREFIX}{template_id}"
        return self.redis.set(key, template_data, ttl=self.TEMPLATE_TTL)

    async def delete_template(self, template_id: str) -> bool:
        """
        Remove template from cache

        :param template_id: Template ID
        :return: Success status
        """
        key = f"{self.TEMPLATE_PREFIX}{template_id}"
        return self.redis.delete(key)

    async def clear_all_templates(self) -> int:
        """
        Clear all cached templates

        :return: Number of templates cleared
        """
        return self.redis.clear_pattern(f"{self.TEMPLATE_PREFIX}*")

    # Generic cache methods

    async def get(self, key: str) -> Optional[Any]:
        """
        Get any value from cache

        :param key: Cache key
        :return: Cached value or None
        """
        return self.redis.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set any value in cache

        :param key: Cache key
        :param value: Value to cache
        :param ttl: Time to live in seconds
        :return: Success status
        """
        return self.redis.set(key, value, ttl=ttl)

    async def delete(self, key: str) -> bool:
        """
        Delete any key from cache

        :param key: Cache key
        :return: Success status
        """
        return self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache

        :param key: Cache key
        :return: True if exists, False otherwise
        """
        return self.redis.exists(key)

    # Counter methods

    async def increment_counter(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter

        Useful for tracking views, downloads, etc.
        :param key: Counter key
        :param amount: Amount to increment
        :return: New value or None on error
        """
        return self.redis.increment(key, amount)

    async def decrement_counter(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Decrement a counter

        :param key: Counter key
        :param amount: Amount to decrement
        :return: New value or None on error
        """
        return self.redis.decrement(key, amount)

    async def get_counter(self, key: str) -> int:
        """
        Get counter value

        :param key: Counter key
        :return: Counter value (0 if not exists)
        """
        value = self.redis.get(key)
        return int(value) if value else 0

    # Statistics and monitoring

    async def get_cache_stats(self) -> dict:
        """
        Get cache statistics

        :return: Cache stats including memory usage, keys count
        """
        info = self.redis.get_info()

        # Count keys by prefix
        block_count = len(self.redis.client.keys(f"{self.BLOCK_PREFIX}*"))
        document_count = len(self.redis.client.keys(f"{self.DOCUMENT_PREFIX}*"))
        search_count = len(self.redis.client.keys(f"{self.SEARCH_PREFIX}*"))
        template_count = len(self.redis.client.keys(f"{self.TEMPLATE_PREFIX}*"))

        return {
            "server": info,
            "cached_items": {
                "blocks": block_count,
                "documents": document_count,
                "search_results": search_count,
                "templates": template_count,
                "total": info.get("total_keys", 0)
            }
        }

    async def clear_all(self) -> bool:
        """
        Clear entire cache

        Use with caution!
        :return: Success status
        """
        return self.redis.flush_all()

    async def health_check(self) -> dict:
        """
        Check cache health

        :return: Health status dict
        """
        try:
            is_available = self.redis.ping()
            info = self.redis.get_info() if is_available else {}

            return {
                "status": "healthy" if is_available else "down",
                "available": is_available,
                "version": info.get("version", "unknown"),
                "memory": info.get("used_memory", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": info.get("total_keys", 0)
            }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }

    async def shutdown(self):
        """Clean up resources"""
        self.redis.close()


# Singleton instance
cache_service = CacheService()
