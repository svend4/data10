"""
Search Service for Full-Text Search
Provides high-level search functionality using Elasticsearch
"""

from typing import List, Dict, Any, Optional
from app.repositories import es_repo, mongo_repo
from app.models import Block


class SearchService:
    """Service for search operations"""

    def __init__(self):
        """Initialize SearchService"""
        self.es_repo = es_repo
        self.mongo_repo = mongo_repo

    async def initialize(self):
        """
        Initialize service and create index

        Creates Elasticsearch index if it doesn't exist
        """
        try:
            self.es_repo.create_index()
            print("✅ Elasticsearch index initialized")
        except Exception as e:
            print(f"⚠️  Elasticsearch index initialization failed: {e}")

    async def index_block(self, block: Block) -> bool:
        """
        Index a single block

        :param block: Block to index
        :return: Success status
        """
        return self.es_repo.index_block(block)

    async def index_all_blocks(self) -> Dict[str, int]:
        """
        Index all blocks from MongoDB to Elasticsearch

        Useful for initial indexing or re-indexing
        :return: Stats (total, indexed, failed)
        """
        # Get all blocks from MongoDB
        blocks = await self.mongo_repo.get_all_blocks()

        if not blocks:
            return {"total": 0, "indexed": 0, "failed": 0}

        # Bulk index
        result = self.es_repo.bulk_index_blocks(blocks)

        return {
            "total": len(blocks),
            "indexed": result.get("success", 0),
            "failed": result.get("failed", 0)
        }

    async def search(
        self,
        query: str,
        block_type: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        level: Optional[int] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Full-text search for blocks

        :param query: Search query
        :param block_type: Filter by block type
        :param source: Filter by source (e.g., "SGB IX")
        :param tags: Filter by tags
        :param category: Filter by category
        :param level: Filter by level
        :param limit: Max results
        :param offset: Offset for pagination
        :return: Search results with metadata
        """
        # Build filters
        filters = {}
        if block_type:
            filters["type"] = block_type
        if source:
            filters["source"] = source
        if tags:
            filters["tags"] = tags
        if category:
            filters["category"] = category
        if level is not None:
            filters["level"] = level

        # Perform search
        return self.es_repo.search_blocks(
            query=query,
            filters=filters,
            limit=limit,
            offset=offset
        )

    async def suggest_titles(self, prefix: str, limit: int = 5) -> List[str]:
        """
        Autocomplete suggestions for block titles

        :param prefix: Prefix to search
        :param limit: Max suggestions
        :return: List of title suggestions
        """
        return self.es_repo.suggest(prefix, limit)

    async def find_similar_blocks(
        self,
        block_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find blocks similar to a given block

        Uses Elasticsearch More Like This query
        :param block_id: Reference block ID
        :param limit: Max results
        :return: List of similar blocks with scores
        """
        return self.es_repo.get_similar_blocks(block_id, limit)

    async def search_by_legal_reference(
        self,
        law: str,
        paragraph: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search blocks by legal reference

        :param law: Law name (e.g., "SGB IX")
        :param paragraph: Optional paragraph (e.g., "§5")
        :param limit: Max results
        :return: Search results
        """
        # Build query
        if paragraph:
            query = f"{law} {paragraph}"
            filters = {"source": law}
        else:
            query = law
            filters = {"source": law}

        return self.es_repo.search_blocks(
            query=query,
            filters=filters,
            limit=limit
        )

    async def search_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        limit: int = 10
    ) -> List[Block]:
        """
        Search blocks by tags

        :param tags: Tags to search for
        :param match_all: If True, block must have all tags; if False, any tag
        :param limit: Max results
        :return: List of blocks
        """
        # For now, use MongoDB for tag search
        # In future, could optimize with Elasticsearch
        blocks = []
        all_blocks = await self.mongo_repo.get_all_blocks()

        for block in all_blocks:
            if not block.metadata or not block.metadata.tags:
                continue

            block_tags = set(block.metadata.tags)
            search_tags = set(tags)

            if match_all:
                if search_tags.issubset(block_tags):
                    blocks.append(block)
            else:
                if block_tags.intersection(search_tags):
                    blocks.append(block)

            if len(blocks) >= limit:
                break

        return blocks[:limit]

    async def get_search_stats(self) -> Dict[str, Any]:
        """
        Get search index statistics

        :return: Index stats including document count and size
        """
        return self.es_repo.get_stats()

    async def delete_from_index(self, block_id: str) -> bool:
        """
        Delete a block from search index

        :param block_id: Block ID to delete
        :return: Success status
        """
        return self.es_repo.delete_block(block_id)

    async def reindex_block(self, block_id: str) -> bool:
        """
        Reindex a specific block

        Fetches from MongoDB and updates Elasticsearch index
        :param block_id: Block ID to reindex
        :return: Success status
        """
        # Get block from MongoDB
        block = await self.mongo_repo.get_block(block_id)
        if not block:
            return False

        # Reindex in Elasticsearch
        return self.es_repo.index_block(block)

    async def shutdown(self):
        """Clean up resources"""
        self.es_repo.close()


# Singleton instance
search_service = SearchService()
