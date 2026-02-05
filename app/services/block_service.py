"""
Block Service - бизнес-логика для работы с блоками
"""

from typing import List, Optional, Dict, Any
from app.models import Block, BlockCreate, BlockUpdate
from app.repositories import mongo_repo, neo4j_repo


class BlockService:
    """Сервис для работы с блоками"""

    def __init__(self):
        self.mongo = mongo_repo
        self.neo4j = neo4j_repo

    async def initialize(self):
        """Инициализация подключений к БД"""
        self.mongo.connect()
        self.neo4j.connect()

    async def shutdown(self):
        """Закрытие подключений"""
        self.mongo.close()
        self.neo4j.close()

    async def create_block(
        self,
        block_data: BlockCreate,
        created_by: Optional[str] = None,
        create_version: bool = True
    ) -> Optional[Block]:
        """
        Создать новый блок

        :param block_data: Данные для создания блока
        :param created_by: Автор создания
        :param create_version: Создавать ли первую версию (по умолчанию True)
        :return: Созданный блок или None
        """
        # Создать полный объект Block
        block = Block(**block_data.model_dump())

        # Сохранить в MongoDB
        mongo_success = self.mongo.create_block(block)
        if not mongo_success:
            return None

        # Создать узел в Neo4j
        neo4j_success = self.neo4j.create_block_node(block)
        if not neo4j_success:
            # Rollback: удалить из MongoDB
            self.mongo.delete_block(block.id)
            return None

        # Создать связи в Neo4j
        if block.relationships:
            self.neo4j.create_relationships(block.id, block.relationships)

        # Создать первую версию
        if create_version:
            try:
                # Импортируем здесь чтобы избежать циклических зависимостей
                from app.services.version_service import version_service
                await version_service.create_version(
                    block,
                    change_summary="Initial version",
                    created_by=created_by
                )
            except Exception as e:
                print(f"⚠️  Failed to create initial version: {e}")

        return block

    async def get_block(self, block_id: str) -> Optional[Block]:
        """
        Получить блок по ID

        :param block_id: ID блока
        :return: Блок или None
        """
        return self.mongo.get_block(block_id)

    async def update_block(
        self,
        block_id: str,
        update_data: BlockUpdate,
        change_summary: Optional[str] = None,
        created_by: Optional[str] = None,
        create_version: bool = True
    ) -> Optional[Block]:
        """
        Обновить блок

        :param block_id: ID блока
        :param update_data: Данные для обновления
        :param change_summary: Описание изменений
        :param created_by: Автор изменений
        :param create_version: Создавать ли версию (по умолчанию True)
        :return: Обновленный блок или None
        """
        # Фильтровать None значения
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        if not update_dict:
            return await self.get_block(block_id)

        # Получить текущий блок перед обновлением
        current_block = await self.get_block(block_id)
        if not current_block:
            return None

        # Увеличить номер версии
        if "version" not in update_dict:
            update_dict["version"] = current_block.version + 1

        # Обновить timestamp
        from datetime import datetime
        update_dict["updated_at"] = datetime.utcnow()

        # Обновить в MongoDB
        success = self.mongo.update_block(block_id, update_dict)
        if not success:
            return None

        # Получить обновлённый блок
        updated_block = await self.get_block(block_id)
        if not updated_block:
            return None

        # Создать версию, если требуется
        if create_version:
            try:
                # Импортируем здесь чтобы избежать циклических зависимостей
                from app.services.version_service import version_service
                await version_service.create_version(
                    updated_block,
                    change_summary=change_summary,
                    created_by=created_by
                )
            except Exception as e:
                print(f"⚠️  Failed to create version: {e}")

        # Если обновлены relationships, обновить в Neo4j
        if "relationships" in update_dict:
            # Сначала удалить старые связи (упрощенно - удалить и пересоздать узел)
            # В production лучше обновлять связи точечно
            pass

        return updated_block

    async def delete_block(self, block_id: str) -> bool:
        """
        Удалить блок

        :param block_id: ID блока
        :return: True если успешно
        """
        # Удалить из Neo4j (включая все связи)
        neo4j_success = self.neo4j.delete_block(block_id)

        # Удалить из MongoDB
        mongo_success = self.mongo.delete_block(block_id)

        return neo4j_success and mongo_success

    async def list_blocks(
        self,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Block]:
        """
        Получить список блоков

        :param source: Фильтр по источнику
        :param limit: Лимит
        :param offset: Смещение
        :return: Список блоков
        """
        return self.mongo.list_blocks(source=source, limit=limit, offset=offset)

    async def search_by_tags(self, tags: List[str]) -> List[Block]:
        """
        Поиск блоков по тегам

        :param tags: Список тегов
        :return: Список блоков
        """
        return self.mongo.search_blocks_by_tags(tags)

    async def get_related_blocks(self, block_id: str, max_depth: int = 2) -> List[Block]:
        """
        Получить связанные блоки через граф

        :param block_id: ID блока
        :param max_depth: Максимальная глубина поиска
        :return: Список связанных блоков
        """
        # Найти ID связанных блоков через Neo4j
        related_ids = self.neo4j.find_related_blocks(block_id, max_depth)

        # Получить полные блоки из MongoDB
        blocks = []
        for rel_id in related_ids:
            block = self.mongo.get_block(rel_id)
            if block:
                blocks.append(block)

        return blocks

    async def get_block_with_relationships(self, block_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить блок со всеми связями из графа

        :param block_id: ID блока
        :return: Dict с блоком и его связями
        """
        # Получить блок из MongoDB
        block = self.mongo.get_block(block_id)
        if not block:
            return None

        # Получить актуальные связи из Neo4j
        relationships = self.neo4j.get_block_relationships(block_id)

        return {
            "block": block,
            "relationships": relationships,
            "related_blocks": await self.get_related_blocks(block_id, max_depth=1)
        }

    async def import_blocks(self, blocks: List[Block]) -> Dict[str, Any]:
        """
        Массовый импорт блоков

        :param blocks: Список блоков
        :return: Статистика импорта
        """
        success_count = 0
        failed_count = 0
        failed_ids = []

        for block in blocks:
            try:
                result = await self.create_block(
                    BlockCreate(**block.model_dump(exclude={'created_at', 'updated_at', 'version'}))
                )
                if result:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_ids.append(block.id)
            except Exception as e:
                failed_count += 1
                failed_ids.append(block.id)
                print(f"Error importing block {block.id}: {e}")

        return {
            "total": len(blocks),
            "success": success_count,
            "failed": failed_count,
            "failed_ids": failed_ids
        }


# Singleton instance
block_service = BlockService()
