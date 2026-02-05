"""
Neo4j Repository - работа с графовой базой данных
"""

from typing import List, Optional, Dict, Any
from neo4j import GraphDatabase, Driver
from app.config import settings
from app.models import Block, BlockRelationships


class Neo4jRepository:
    """Репозиторий для работы с Neo4j графом"""

    def __init__(self):
        self.driver: Optional[Driver] = None

    def connect(self):
        """Подключение к Neo4j"""
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        """Закрытие соединения"""
        if self.driver:
            self.driver.close()

    def create_block_node(self, block: Block) -> bool:
        """
        Создать узел блока в графе

        :param block: Блок для создания
        :return: True если успешно
        """
        with self.driver.session() as session:
            result = session.execute_write(self._create_block_tx, block)
            return result

    @staticmethod
    def _create_block_tx(tx, block: Block):
        """Transaction для создания блока"""
        query = """
        MERGE (b:Block {id: $id})
        SET b.type = $type,
            b.title = $title,
            b.source = $source,
            b.level = $level,
            b.created_at = datetime($created_at),
            b.updated_at = datetime($updated_at),
            b.version = $version
        RETURN b
        """
        result = tx.run(
            query,
            id=block.id,
            type=block.type,
            title=block.title,
            source=block.source,
            level=block.level,
            created_at=block.created_at.isoformat(),
            updated_at=block.updated_at.isoformat(),
            version=block.version
        )
        return result.single() is not None

    def create_relationships(self, block_id: str, relationships: BlockRelationships) -> bool:
        """
        Создать связи блока с другими блоками

        :param block_id: ID блока
        :param relationships: Связи для создания
        :return: True если успешно
        """
        with self.driver.session() as session:
            # Parent relationship
            if relationships.parent:
                session.execute_write(
                    self._create_parent_relationship_tx,
                    block_id,
                    relationships.parent
                )

            # Children relationships
            for child_id in relationships.children:
                session.execute_write(
                    self._create_child_relationship_tx,
                    block_id,
                    child_id
                )

            # References
            for ref_id in relationships.references:
                session.execute_write(
                    self._create_reference_relationship_tx,
                    block_id,
                    ref_id
                )

            # Related
            for related_id in relationships.related:
                session.execute_write(
                    self._create_related_relationship_tx,
                    block_id,
                    related_id
                )

            return True

    @staticmethod
    def _create_parent_relationship_tx(tx, child_id: str, parent_id: str):
        """Создать связь PARENT"""
        query = """
        MATCH (child:Block {id: $child_id})
        MATCH (parent:Block {id: $parent_id})
        MERGE (child)-[:PARENT]->(parent)
        """
        tx.run(query, child_id=child_id, parent_id=parent_id)

    @staticmethod
    def _create_child_relationship_tx(tx, parent_id: str, child_id: str):
        """Создать связь CHILD"""
        query = """
        MATCH (parent:Block {id: $parent_id})
        MATCH (child:Block {id: $child_id})
        MERGE (parent)-[:CHILD]->(child)
        """
        tx.run(query, parent_id=parent_id, child_id=child_id)

    @staticmethod
    def _create_reference_relationship_tx(tx, from_id: str, to_id: str):
        """Создать связь REFERENCES"""
        query = """
        MATCH (from:Block {id: $from_id})
        MATCH (to:Block {id: $to_id})
        MERGE (from)-[:REFERENCES]->(to)
        """
        tx.run(query, from_id=from_id, to_id=to_id)

    @staticmethod
    def _create_related_relationship_tx(tx, from_id: str, to_id: str):
        """Создать связь RELATED_TO"""
        query = """
        MATCH (from:Block {id: $from_id})
        MATCH (to:Block {id: $to_id})
        MERGE (from)-[:RELATED_TO]->(to)
        """
        tx.run(query, from_id=from_id, to_id=to_id)

    def get_block_relationships(self, block_id: str) -> Optional[BlockRelationships]:
        """
        Получить все связи блока

        :param block_id: ID блока
        :return: Объект BlockRelationships или None
        """
        with self.driver.session() as session:
            result = session.execute_read(self._get_relationships_tx, block_id)
            return result

    @staticmethod
    def _get_relationships_tx(tx, block_id: str) -> Optional[BlockRelationships]:
        """Transaction для получения связей"""
        query = """
        MATCH (b:Block {id: $block_id})
        OPTIONAL MATCH (b)-[:PARENT]->(parent:Block)
        OPTIONAL MATCH (b)-[:CHILD]->(child:Block)
        OPTIONAL MATCH (b)-[:REFERENCES]->(ref:Block)
        OPTIONAL MATCH (b)-[:RELATED_TO]->(related:Block)
        RETURN
            parent.id as parent_id,
            collect(DISTINCT child.id) as children_ids,
            collect(DISTINCT ref.id) as references_ids,
            collect(DISTINCT related.id) as related_ids
        """
        result = tx.run(query, block_id=block_id)
        record = result.single()

        if not record:
            return None

        return BlockRelationships(
            parent=record["parent_id"],
            children=[cid for cid in record["children_ids"] if cid],
            references=[rid for rid in record["references_ids"] if rid],
            related=[rid for rid in record["related_ids"] if rid]
        )

    def find_related_blocks(self, block_id: str, max_depth: int = 2) -> List[str]:
        """
        Найти все связанные блоки на определенную глубину

        :param block_id: ID блока
        :param max_depth: Максимальная глубина поиска
        :return: Список ID связанных блоков
        """
        with self.driver.session() as session:
            result = session.execute_read(
                self._find_related_blocks_tx,
                block_id,
                max_depth
            )
            return result

    @staticmethod
    def _find_related_blocks_tx(tx, block_id: str, max_depth: int) -> List[str]:
        """Transaction для поиска связанных блоков"""
        query = """
        MATCH path = (b:Block {id: $block_id})-[*1..$max_depth]-(related:Block)
        RETURN DISTINCT related.id as id
        """
        result = tx.run(query, block_id=block_id, max_depth=max_depth)
        return [record["id"] for record in result]

    def delete_block(self, block_id: str) -> bool:
        """
        Удалить блок и все его связи

        :param block_id: ID блока
        :return: True если успешно
        """
        with self.driver.session() as session:
            result = session.execute_write(self._delete_block_tx, block_id)
            return result

    @staticmethod
    def _delete_block_tx(tx, block_id: str) -> bool:
        """Transaction для удаления блока"""
        query = """
        MATCH (b:Block {id: $block_id})
        DETACH DELETE b
        RETURN count(b) as deleted_count
        """
        result = tx.run(query, block_id=block_id)
        record = result.single()
        return record["deleted_count"] > 0 if record else False

    def get_all_blocks(self) -> List[Dict[str, Any]]:
        """
        Получить все блоки из графа

        :return: Список блоков
        """
        with self.driver.session() as session:
            result = session.execute_read(self._get_all_blocks_tx)
            return result

    @staticmethod
    def _get_all_blocks_tx(tx) -> List[Dict[str, Any]]:
        """Transaction для получения всех блоков"""
        query = """
        MATCH (b:Block)
        RETURN b.id as id, b.type as type, b.title as title,
               b.source as source, b.level as level
        ORDER BY b.id
        """
        result = tx.run(query)
        return [dict(record) for record in result]


# Singleton instance
neo4j_repo = Neo4jRepository()
