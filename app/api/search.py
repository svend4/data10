"""
Search API endpoints
Full-text search and related operations
"""

from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from app.services import search_service


router = APIRouter()


class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., description="Search query")
    type: Optional[str] = Field(None, description="Filter by block type")
    source: Optional[str] = Field(None, description="Filter by source (e.g., SGB IX)")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    category: Optional[str] = Field(None, description="Filter by category")
    level: Optional[int] = Field(None, description="Filter by level")
    limit: int = Field(10, ge=1, le=100, description="Max results")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class SearchResponse(BaseModel):
    """Search response model"""
    results: List[dict]
    total: int
    limit: int
    offset: int
    query: str
    filters: dict


class SuggestResponse(BaseModel):
    """Autocomplete suggestions response"""
    suggestions: List[str]
    prefix: str


class SimilarBlocksResponse(BaseModel):
    """Similar blocks response"""
    similar_blocks: List[dict]
    reference_block_id: str


class IndexStatsResponse(BaseModel):
    """Search index statistics"""
    index_name: str
    document_count: int
    index_size_bytes: Optional[int] = None
    status: str


@router.post("/", response_model=SearchResponse)
async def search_blocks(request: SearchRequest):
    """
    Full-text search for blocks

    Searches through block titles, content, and tags using Elasticsearch.
    Supports filtering by type, source, tags, category, and level.

    Example:
    ```json
    {
      "query": "Leistungen zur Teilhabe",
      "source": "SGB IX",
      "tags": ["§5"],
      "limit": 10
    }
    ```
    """
    try:
        results = await search_service.search(
            query=request.query,
            block_type=request.type,
            source=request.source,
            tags=request.tags,
            category=request.category,
            level=request.level,
            limit=request.limit,
            offset=request.offset
        )
        return SearchResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=SearchResponse)
async def search_blocks_get(
    q: str = Query(..., description="Search query"),
    type: Optional[str] = Query(None, description="Filter by block type"),
    source: Optional[str] = Query(None, description="Filter by source"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    category: Optional[str] = Query(None, description="Filter by category"),
    level: Optional[int] = Query(None, description="Filter by level"),
    limit: int = Query(10, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Full-text search for blocks (GET method)

    Query parameters:
    - q: Search query (required)
    - type: Block type filter (optional)
    - source: Source filter (optional)
    - tags: Comma-separated tags (optional)
    - category: Category filter (optional)
    - level: Level filter (optional)
    - limit: Max results (default: 10, max: 100)
    - offset: Offset for pagination (default: 0)

    Example:
    ```
    GET /api/search?q=Teilhabe&source=SGB+IX&tags=§5&limit=10
    ```
    """
    try:
        # Parse tags
        tags_list = tags.split(",") if tags else None

        results = await search_service.search(
            query=q,
            block_type=type,
            source=source,
            tags=tags_list,
            category=category,
            level=level,
            limit=limit,
            offset=offset
        )
        return SearchResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest", response_model=SuggestResponse)
async def suggest_titles(
    prefix: str = Query(..., description="Prefix to autocomplete"),
    limit: int = Query(5, ge=1, le=20, description="Max suggestions")
):
    """
    Autocomplete suggestions for block titles

    Returns title suggestions based on prefix match.

    Example:
    ```
    GET /api/search/suggest?prefix=Leist&limit=5
    ```

    Returns:
    ```json
    {
      "suggestions": [
        "Leistungen zur Teilhabe",
        "Leistungsträger",
        "Leistungserbringer"
      ],
      "prefix": "Leist"
    }
    ```
    """
    try:
        suggestions = await search_service.suggest_titles(prefix, limit)
        return SuggestResponse(suggestions=suggestions, prefix=prefix)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{block_id}", response_model=SimilarBlocksResponse)
async def get_similar_blocks(
    block_id: str,
    limit: int = Query(5, ge=1, le=20, description="Max similar blocks")
):
    """
    Find blocks similar to a given block

    Uses Elasticsearch More Like This query to find blocks with similar
    content, title, and tags.

    Example:
    ```
    GET /api/search/similar/sgb9_para5?limit=5
    ```

    Returns blocks ranked by similarity score.
    """
    try:
        similar_blocks = await search_service.find_similar_blocks(block_id, limit)
        if not similar_blocks:
            raise HTTPException(
                status_code=404,
                detail=f"No similar blocks found for {block_id}"
            )
        return SimilarBlocksResponse(
            similar_blocks=similar_blocks,
            reference_block_id=block_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/legal/{law}", response_model=SearchResponse)
async def search_by_legal_reference(
    law: str,
    paragraph: Optional[str] = Query(None, description="Paragraph reference (e.g., §5)"),
    limit: int = Query(10, ge=1, le=100, description="Max results")
):
    """
    Search blocks by legal reference

    Search for blocks from a specific law and optionally a specific paragraph.

    Examples:
    ```
    GET /api/search/legal/SGB%20IX?limit=10
    GET /api/search/legal/SGB%20IX?paragraph=§5&limit=10
    ```
    """
    try:
        results = await search_service.search_by_legal_reference(
            law=law,
            paragraph=paragraph,
            limit=limit
        )
        return SearchResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=IndexStatsResponse)
async def get_search_stats():
    """
    Get search index statistics

    Returns information about the Elasticsearch index including:
    - Document count
    - Index size
    - Index status

    Example:
    ```
    GET /api/search/stats
    ```
    """
    try:
        stats = await search_service.get_search_stats()
        return IndexStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reindex")
async def reindex_all_blocks():
    """
    Reindex all blocks from MongoDB to Elasticsearch

    This operation:
    1. Fetches all blocks from MongoDB
    2. Bulk indexes them to Elasticsearch
    3. Returns statistics

    Useful for:
    - Initial setup
    - Rebuilding search index
    - Syncing after bulk updates

    Example:
    ```
    POST /api/search/reindex
    ```

    Returns:
    ```json
    {
      "message": "Reindexing completed",
      "total": 100,
      "indexed": 98,
      "failed": 2
    }
    ```
    """
    try:
        stats = await search_service.index_all_blocks()
        return {
            "message": "Reindexing completed",
            **stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{block_id}")
async def delete_from_index(block_id: str):
    """
    Delete a block from search index

    Removes the block from Elasticsearch index.
    Note: This does NOT delete from MongoDB, only from search index.

    Example:
    ```
    DELETE /api/search/sgb9_para5
    ```
    """
    try:
        success = await search_service.delete_from_index(block_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Block {block_id} not found in search index"
            )
        return {"message": f"Block {block_id} removed from search index"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reindex/{block_id}")
async def reindex_single_block(block_id: str):
    """
    Reindex a single block

    Fetches the block from MongoDB and updates it in the search index.

    Example:
    ```
    POST /api/search/reindex/sgb9_para5
    ```
    """
    try:
        success = await search_service.reindex_block(block_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Block {block_id} not found in MongoDB"
            )
        return {"message": f"Block {block_id} reindexed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
