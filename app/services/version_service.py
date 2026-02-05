"""
Version Service для управления версиями блоков
Отслеживание истории изменений и откат к предыдущим версиям
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.repositories import mongo_repo
from app.models import (
    Block,
    BlockVersion,
    VersionDiff,
    BlockVersionCreate,
    VersionHistory
)


class VersionService:
    """Сервис для управления версиями блоков"""

    def __init__(self):
        """Initialize VersionService"""
        self.mongo = mongo_repo
        self.versions_collection = "block_versions"

    async def initialize(self):
        """Инициализация сервиса версий"""
        # Создание индексов для версий
        try:
            self.mongo.db[self.versions_collection].create_index("block_id")
            self.mongo.db[self.versions_collection].create_index([
                ("block_id", 1),
                ("version", -1)
            ])
            self.mongo.db[self.versions_collection].create_index("is_current")
            print("✅ Version service initialized")
        except Exception as e:
            print(f"⚠️  Version service initialization warning: {e}")

    async def create_version(
        self,
        block: Block,
        change_summary: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> BlockVersion:
        """
        Создать новую версию блока

        :param block: Блок для версионирования
        :param change_summary: Описание изменений
        :param created_by: Автор изменений
        :return: Созданная версия
        """
        # Создаём snapshot блока
        version = BlockVersion(
            id=f"{block.id}:{block.version}",
            block_id=block.id,
            version=block.version,
            type=block.type,
            title=block.title,
            content=block.content,
            source=block.source,
            level=block.level,
            metadata=block.metadata.dict() if block.metadata else {},
            relationships=block.relationships.dict() if block.relationships else {},
            created_at=datetime.utcnow(),
            created_by=created_by,
            change_summary=change_summary,
            is_current=True
        )

        # Сбросить is_current для предыдущих версий
        self.mongo.db[self.versions_collection].update_many(
            {"block_id": block.id},
            {"$set": {"is_current": False}}
        )

        # Сохранить новую версию
        self.mongo.db[self.versions_collection].insert_one(version.dict())

        return version

    async def get_version(
        self,
        block_id: str,
        version: int
    ) -> Optional[BlockVersion]:
        """
        Получить конкретную версию блока

        :param block_id: ID блока
        :param version: Номер версии
        :return: Версия блока или None
        """
        version_data = self.mongo.db[self.versions_collection].find_one({
            "block_id": block_id,
            "version": version
        })

        if version_data:
            return BlockVersion(**version_data)
        return None

    async def get_current_version(self, block_id: str) -> Optional[BlockVersion]:
        """
        Получить текущую версию блока

        :param block_id: ID блока
        :return: Текущая версия или None
        """
        version_data = self.mongo.db[self.versions_collection].find_one({
            "block_id": block_id,
            "is_current": True
        })

        if version_data:
            return BlockVersion(**version_data)
        return None

    async def get_version_history(
        self,
        block_id: str,
        limit: int = 10
    ) -> VersionHistory:
        """
        Получить историю версий блока

        :param block_id: ID блока
        :param limit: Максимальное количество версий
        :return: История версий
        """
        # Получаем все версии блока
        versions_data = list(
            self.mongo.db[self.versions_collection]
            .find({"block_id": block_id})
            .sort("version", -1)
            .limit(limit)
        )

        versions = [BlockVersion(**v) for v in versions_data]

        # Определяем текущую версию
        current_version = 1
        for v in versions:
            if v.is_current:
                current_version = v.version
                break

        return VersionHistory(
            block_id=block_id,
            total_versions=len(versions),
            current_version=current_version,
            versions=versions
        )

    async def restore_version(
        self,
        block_id: str,
        version: int,
        created_by: Optional[str] = None
    ) -> Optional[Block]:
        """
        Откатить блок к предыдущей версии

        Создаёт новую версию блока на основе старой
        :param block_id: ID блока
        :param version: Номер версии для восстановления
        :param created_by: Автор восстановления
        :return: Восстановленный блок или None
        """
        # Получаем версию для восстановления
        old_version = await self.get_version(block_id, version)
        if not old_version:
            return None

        # Получаем текущий блок
        current_block = await self.mongo.get_block(block_id)
        if not current_block:
            return None

        # Создаём новый блок с данными из старой версии
        # но с новым номером версии
        restored_block = Block(
            id=current_block.id,
            type=old_version.type,
            title=old_version.title,
            content=old_version.content,
            source=old_version.source,
            level=old_version.level,
            metadata=current_block.metadata,  # Сохраняем текущие метаданные
            relationships=current_block.relationships,  # Сохраняем текущие связи
            created_at=current_block.created_at,
            updated_at=datetime.utcnow(),
            version=current_block.version + 1
        )

        # Обновляем блок в MongoDB
        success = await self.mongo.update_block(
            block_id,
            restored_block.dict()
        )

        if success:
            # Создаём новую версию
            await self.create_version(
                restored_block,
                change_summary=f"Restored from version {version}",
                created_by=created_by
            )
            return restored_block

        return None

    async def compare_versions(
        self,
        block_id: str,
        old_version: int,
        new_version: int
    ) -> Optional[VersionDiff]:
        """
        Сравнить две версии блока

        :param block_id: ID блока
        :param old_version: Номер старой версии
        :param new_version: Номер новой версии
        :return: Разница между версиями или None
        """
        old = await self.get_version(block_id, old_version)
        new = await self.get_version(block_id, new_version)

        if not old or not new:
            return None

        # Сравниваем поля
        changes = {}
        comparable_fields = ["type", "title", "content", "source", "level"]

        for field in comparable_fields:
            old_value = getattr(old, field)
            new_value = getattr(new, field)
            if old_value != new_value:
                changes[field] = {
                    "old": old_value,
                    "new": new_value
                }

        return VersionDiff(
            block_id=block_id,
            old_version=old_version,
            new_version=new_version,
            changes=changes,
            changed_at=new.created_at
        )

    async def delete_version(
        self,
        block_id: str,
        version: int
    ) -> bool:
        """
        Удалить версию блока

        Внимание: текущую версию нельзя удалить
        :param block_id: ID блока
        :param version: Номер версии
        :return: Успешность операции
        """
        # Проверяем, что это не текущая версия
        version_data = await self.get_version(block_id, version)
        if not version_data or version_data.is_current:
            return False

        # Удаляем версию
        result = self.mongo.db[self.versions_collection].delete_one({
            "block_id": block_id,
            "version": version
        })

        return result.deleted_count > 0

    async def delete_all_versions(self, block_id: str) -> int:
        """
        Удалить все версии блока

        :param block_id: ID блока
        :return: Количество удалённых версий
        """
        result = self.mongo.db[self.versions_collection].delete_many({
            "block_id": block_id
        })

        return result.deleted_count

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику по версиям

        :return: Статистика
        """
        total_versions = self.mongo.db[self.versions_collection].count_documents({})

        # Количество блоков с версиями
        pipeline = [
            {"$group": {"_id": "$block_id"}},
            {"$count": "total_blocks"}
        ]
        blocks_with_versions = list(
            self.mongo.db[self.versions_collection].aggregate(pipeline)
        )
        total_blocks = blocks_with_versions[0]["total_blocks"] if blocks_with_versions else 0

        # Средне количество версий на блок
        avg_versions = total_versions / total_blocks if total_blocks > 0 else 0

        return {
            "total_versions": total_versions,
            "blocks_with_versions": total_blocks,
            "average_versions_per_block": round(avg_versions, 2)
        }

    async def shutdown(self):
        """Очистка ресурсов"""
        pass


# Singleton instance
version_service = VersionService()
