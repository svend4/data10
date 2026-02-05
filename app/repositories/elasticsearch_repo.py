"""
Elasticsearch Repository for Full-Text Search
Handles block indexing and search operations
"""

import os
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch, NotFoundError
from app.models import Block


class ElasticsearchRepository:
    """Repository for Elasticsearch operations"""

    def __init__(self):
        """Initialize Elasticsearch client"""
        self.es_uri = os.getenv("ELASTICSEARCH_URI", "http://localhost:9200")
        self.client = Elasticsearch([self.es_uri])
        self.index_name = "dynamic_blocks"

    def create_index(self):
        """
        Create Elasticsearch index with mappings

        Index structure:
        - title: text with german analyzer
        - content: text with german analyzer
        - type: keyword
        - source: keyword
        - tags: keyword array
        - level: integer
        - created_at: date
        """
        if self.client.indices.exists(index=self.index_name):
            return True

        mappings = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "german",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {"type": "completion"}
                        }
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "german",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "source": {"type": "keyword"},
                    "level": {"type": "integer"},
                    "tags": {"type": "keyword"},
                    "law_reference": {"type": "keyword"},
                    "effective_date": {"type": "date"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "version": {"type": "integer"},
                    # Metadata fields for filtering
                    "metadata": {
                        "properties": {
                            "category": {"type": "keyword"},
                            "subcategory": {"type": "keyword"},
                            "language": {"type": "keyword"}
                        }
                    },
                    # Semantic search embedding vector
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384,  # paraphrase-multilingual-MiniLM-L12-v2 dimension
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "german": {
                            "type": "standard",
                            "stopwords": "_german_"
                        }
                    }
                }
            }
        }

        self.client.indices.create(index=self.index_name, body=mappings)
        return True

    def index_block(self, block: Block, embedding: Optional[List[float]] = None) -> bool:
        """
        Index a block for search

        :param block: Block to index
        :param embedding: Optional semantic embedding vector
        :return: Success status
        """
        try:
            doc = {
                "id": block.id,
                "type": block.type,
                "title": block.title,
                "content": block.content,
                "source": block.source,
                "level": block.level,
                "tags": block.metadata.tags if block.metadata else [],
                "law_reference": block.metadata.law_reference if block.metadata else None,
                "effective_date": block.metadata.effective_date.isoformat() if block.metadata and block.metadata.effective_date else None,
                "created_at": block.created_at.isoformat(),
                "updated_at": block.updated_at.isoformat() if block.updated_at else None,
                "version": block.version,
                "metadata": {
                    "category": block.metadata.category if block.metadata else None,
                    "subcategory": block.metadata.subcategory if block.metadata else None,
                    "language": block.metadata.language if block.metadata else "de"
                }
            }

            # Add embedding if provided
            if embedding:
                doc["embedding"] = embedding

            self.client.index(
                index=self.index_name,
                id=block.id,
                document=doc
            )
            return True
        except Exception as e:
            print(f"Error indexing block {block.id}: {e}")
            return False

    def delete_block(self, block_id: str) -> bool:
        """
        Delete a block from index

        :param block_id: Block ID to delete
        :return: Success status
        """
        try:
            self.client.delete(index=self.index_name, id=block_id)
            return True
        except NotFoundError:
            return False
        except Exception as e:
            print(f"Error deleting block {block_id}: {e}")
            return False

    def search_blocks(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Full-text search for blocks

        :param query: Search query
        :param filters: Optional filters (type, source, tags, etc.)
        :param limit: Max results
        :param offset: Offset for pagination
        :return: Search results with metadata
        """
        # Build query
        must_clauses = []

        # Main search query
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content^2", "tags"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })

        # Apply filters
        filter_clauses = []
        if filters:
            if "type" in filters:
                filter_clauses.append({"term": {"type": filters["type"]}})
            if "source" in filters:
                filter_clauses.append({"term": {"source": filters["source"]}})
            if "tags" in filters:
                filter_clauses.append({"terms": {"tags": filters["tags"]}})
            if "category" in filters:
                filter_clauses.append({"term": {"metadata.category": filters["category"]}})
            if "level" in filters:
                filter_clauses.append({"term": {"level": filters["level"]}})

        # Build search body
        search_body = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses
                }
            },
            "from": offset,
            "size": limit,
            "sort": [
                {"_score": {"order": "desc"}},
                {"created_at": {"order": "desc"}}
            ],
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {"fragment_size": 150, "number_of_fragments": 3}
                }
            }
        }

        try:
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )

            hits = response["hits"]["hits"]
            total = response["hits"]["total"]["value"]

            results = []
            for hit in hits:
                result = {
                    "id": hit["_source"]["id"],
                    "score": hit["_score"],
                    "title": hit["_source"]["title"],
                    "content": hit["_source"]["content"],
                    "type": hit["_source"]["type"],
                    "source": hit["_source"]["source"],
                    "tags": hit["_source"]["tags"],
                    "highlights": hit.get("highlight", {})
                }
                results.append(result)

            return {
                "results": results,
                "total": total,
                "limit": limit,
                "offset": offset,
                "query": query,
                "filters": filters or {}
            }
        except Exception as e:
            print(f"Search error: {e}")
            return {
                "results": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "query": query,
                "filters": filters or {},
                "error": str(e)
            }

    def suggest(self, prefix: str, limit: int = 5) -> List[str]:
        """
        Autocomplete suggestions for block titles

        :param prefix: Prefix to search
        :param limit: Max suggestions
        :return: List of suggestions
        """
        try:
            search_body = {
                "suggest": {
                    "title-suggest": {
                        "prefix": prefix,
                        "completion": {
                            "field": "title.suggest",
                            "size": limit,
                            "skip_duplicates": True
                        }
                    }
                }
            }

            response = self.client.search(
                index=self.index_name,
                body=search_body
            )

            suggestions = []
            for option in response["suggest"]["title-suggest"][0]["options"]:
                suggestions.append(option["text"])

            return suggestions
        except Exception as e:
            print(f"Suggest error: {e}")
            return []

    def get_similar_blocks(
        self,
        block_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar blocks using More Like This query

        :param block_id: Reference block ID
        :param limit: Max results
        :return: List of similar blocks
        """
        try:
            search_body = {
                "query": {
                    "more_like_this": {
                        "fields": ["title", "content", "tags"],
                        "like": [
                            {
                                "_index": self.index_name,
                                "_id": block_id
                            }
                        ],
                        "min_term_freq": 1,
                        "min_doc_freq": 1,
                        "max_query_terms": 12
                    }
                },
                "size": limit
            }

            response = self.client.search(
                index=self.index_name,
                body=search_body
            )

            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "id": hit["_source"]["id"],
                    "title": hit["_source"]["title"],
                    "score": hit["_score"],
                    "type": hit["_source"]["type"],
                    "source": hit["_source"]["source"]
                })

            return results
        except Exception as e:
            print(f"Similar blocks error: {e}")
            return []

    def search_blocks_by_embedding(
        self,
        embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using embedding vector similarity

        Uses kNN (k-nearest neighbors) search to find semantically similar blocks
        :param embedding: Query embedding vector
        :param filters: Optional filters (type, source, etc.)
        :param limit: Max results
        :param min_score: Minimum similarity score (0-1)
        :return: List of similar blocks with scores
        """
        try:
            # Build filter clauses
            filter_clauses = []
            if filters:
                if "type" in filters:
                    filter_clauses.append({"term": {"type": filters["type"]}})
                if "source" in filters:
                    filter_clauses.append({"term": {"source": filters["source"]}})
                if "tags" in filters:
                    filter_clauses.append({"terms": {"tags": filters["tags"]}})
                if "category" in filters:
                    filter_clauses.append({"term": {"metadata.category": filters["category"]}})

            # Build kNN search query
            search_body = {
                "knn": {
                    "field": "embedding",
                    "query_vector": embedding,
                    "k": limit,
                    "num_candidates": limit * 10,  # Search space for kNN
                }
            }

            # Add filters if present
            if filter_clauses:
                search_body["knn"]["filter"] = {
                    "bool": {"must": filter_clauses}
                }

            response = self.client.search(
                index=self.index_name,
                body=search_body,
                size=limit
            )

            results = []
            for hit in response["hits"]["hits"]:
                score = hit["_score"]
                # Filter by minimum score
                if score < min_score:
                    continue

                results.append({
                    "id": hit["_source"]["id"],
                    "title": hit["_source"]["title"],
                    "content": hit["_source"]["content"],
                    "type": hit["_source"]["type"],
                    "source": hit["_source"]["source"],
                    "tags": hit["_source"]["tags"],
                    "score": score,
                    "similarity": score  # Cosine similarity (0-1)
                })

            return results
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []

    def bulk_index_blocks(
        self,
        blocks: List[Block],
        embeddings: Optional[Dict[str, List[float]]] = None
    ) -> Dict[str, int]:
        """
        Bulk index multiple blocks

        :param blocks: List of blocks to index
        :param embeddings: Optional dict mapping block_id -> embedding vector
        :return: Stats (success, failed)
        """
        from elasticsearch.helpers import bulk

        actions = []
        for block in blocks:
            source_doc = {
                "id": block.id,
                "type": block.type,
                "title": block.title,
                "content": block.content,
                "source": block.source,
                "level": block.level,
                "tags": block.metadata.tags if block.metadata else [],
                "created_at": block.created_at.isoformat(),
                "version": block.version
            }

            # Add embedding if provided
            if embeddings and block.id in embeddings:
                source_doc["embedding"] = embeddings[block.id]

            action = {
                "_index": self.index_name,
                "_id": block.id,
                "_source": source_doc
            }
            actions.append(action)

        try:
            success, failed = bulk(self.client, actions, raise_on_error=False)
            return {"success": success, "failed": failed}
        except Exception as e:
            print(f"Bulk index error: {e}")
            return {"success": 0, "failed": len(blocks)}

    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics

        :return: Index stats
        """
        try:
            stats = self.client.indices.stats(index=self.index_name)
            count = self.client.count(index=self.index_name)

            return {
                "index_name": self.index_name,
                "document_count": count["count"],
                "index_size_bytes": stats["_all"]["primaries"]["store"]["size_in_bytes"],
                "status": "healthy"
            }
        except Exception as e:
            return {
                "index_name": self.index_name,
                "status": "error",
                "error": str(e)
            }

    def close(self):
        """Close Elasticsearch connection"""
        if self.client:
            self.client.close()


# Singleton instance
es_repo = ElasticsearchRepository()
