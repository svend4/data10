"""
MongoDB Repository - хранилище документов (блоки, правила, документы)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from app.config import settings
from app.models import Block, Rule, Document, Template


class MongoRepository:
    """Репозиторий для работы с MongoDB"""

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.blocks: Optional[Collection] = None
        self.rules: Optional[Collection] = None
        self.documents: Optional[Collection] = None
        self.templates: Optional[Collection] = None

    def connect(self):
        """Подключение к MongoDB"""
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB]
        self.blocks = self.db["blocks"]
        self.rules = self.db["rules"]
        self.documents = self.db["documents"]
        self.templates = self.db["templates"]

        # Создать индексы
        self._create_indexes()

    def _create_indexes(self):
        """Создать индексы для коллекций"""
        # Blocks indexes
        self.blocks.create_index([("id", ASCENDING)], unique=True)
        self.blocks.create_index([("source", ASCENDING)])
        self.blocks.create_index([("metadata.law", ASCENDING)])
        self.blocks.create_index([("metadata.tags", ASCENDING)])

        # Rules indexes
        self.rules.create_index([("id", ASCENDING)], unique=True)
        self.rules.create_index([("enabled", ASCENDING)])
        self.rules.create_index([("priority", DESCENDING)])

        # Documents indexes
        self.documents.create_index([("id", ASCENDING)], unique=True)
        self.documents.create_index([("template_id", ASCENDING)])
        self.documents.create_index([("status", ASCENDING)])
        self.documents.create_index([("created_at", DESCENDING)])

        # Templates indexes
        self.templates.create_index([("id", ASCENDING)], unique=True)

    def close(self):
        """Закрытие соединения"""
        if self.client:
            self.client.close()

    # ==================== BLOCKS ====================

    def create_block(self, block: Block) -> bool:
        """Создать блок"""
        try:
            self.blocks.insert_one(block.model_dump())
            return True
        except Exception as e:
            print(f"Error creating block: {e}")
            return False

    def get_block(self, block_id: str) -> Optional[Block]:
        """Получить блок по ID"""
        doc = self.blocks.find_one({"id": block_id})
        if doc:
            doc.pop("_id", None)  # Remove MongoDB _id
            return Block(**doc)
        return None

    def update_block(self, block_id: str, update_data: Dict[str, Any]) -> bool:
        """Обновить блок"""
        update_data["updated_at"] = datetime.utcnow()
        result = self.blocks.update_one(
            {"id": block_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    def delete_block(self, block_id: str) -> bool:
        """Удалить блок"""
        result = self.blocks.delete_one({"id": block_id})
        return result.deleted_count > 0

    def list_blocks(
        self,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Block]:
        """Получить список блоков с фильтрацией"""
        query = {}
        if source:
            query["source"] = source

        cursor = self.blocks.find(query).skip(offset).limit(limit)
        blocks = []
        for doc in cursor:
            doc.pop("_id", None)
            blocks.append(Block(**doc))
        return blocks

    def search_blocks_by_tags(self, tags: List[str]) -> List[Block]:
        """Поиск блоков по тегам"""
        cursor = self.blocks.find({"metadata.tags": {"$in": tags}})
        blocks = []
        for doc in cursor:
            doc.pop("_id", None)
            blocks.append(Block(**doc))
        return blocks

    # ==================== RULES ====================

    def create_rule(self, rule: Rule) -> bool:
        """Создать правило"""
        try:
            self.rules.insert_one(rule.model_dump())
            return True
        except Exception as e:
            print(f"Error creating rule: {e}")
            return False

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Получить правило по ID"""
        doc = self.rules.find_one({"id": rule_id})
        if doc:
            doc.pop("_id", None)
            return Rule(**doc)
        return None

    def update_rule(self, rule_id: str, update_data: Dict[str, Any]) -> bool:
        """Обновить правило"""
        update_data["updated_at"] = datetime.utcnow()
        result = self.rules.update_one(
            {"id": rule_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    def delete_rule(self, rule_id: str) -> bool:
        """Удалить правило"""
        result = self.rules.delete_one({"id": rule_id})
        return result.deleted_count > 0

    def get_enabled_rules(self) -> List[Rule]:
        """Получить все активные правила отсортированные по приоритету"""
        cursor = self.rules.find({"enabled": True}).sort("priority", DESCENDING)
        rules = []
        for doc in cursor:
            doc.pop("_id", None)
            rules.append(Rule(**doc))
        return rules

    # ==================== DOCUMENTS ====================

    def create_document(self, document: Document) -> bool:
        """Создать документ"""
        try:
            self.documents.insert_one(document.model_dump())
            return True
        except Exception as e:
            print(f"Error creating document: {e}")
            return False

    def get_document(self, document_id: str) -> Optional[Document]:
        """Получить документ по ID"""
        doc = self.documents.find_one({"id": document_id})
        if doc:
            doc.pop("_id", None)
            return Document(**doc)
        return None

    def update_document(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """Обновить документ"""
        update_data["updated_at"] = datetime.utcnow()
        result = self.documents.update_one(
            {"id": document_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    def delete_document(self, document_id: str) -> bool:
        """Удалить документ"""
        result = self.documents.delete_one({"id": document_id})
        return result.deleted_count > 0

    def list_documents(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Document]:
        """Получить список документов"""
        cursor = self.documents.find().sort("created_at", DESCENDING).skip(offset).limit(limit)
        documents = []
        for doc in cursor:
            doc.pop("_id", None)
            documents.append(Document(**doc))
        return documents

    # ==================== TEMPLATES ====================

    def create_template(self, template: Template) -> bool:
        """Создать шаблон"""
        try:
            self.templates.insert_one(template.model_dump())
            return True
        except Exception as e:
            print(f"Error creating template: {e}")
            return False

    def get_template(self, template_id: str) -> Optional[Template]:
        """Получить шаблон по ID"""
        doc = self.templates.find_one({"id": template_id})
        if doc:
            doc.pop("_id", None)
            return Template(**doc)
        return None

    def list_templates(self) -> List[Template]:
        """Получить список всех шаблонов"""
        cursor = self.templates.find()
        templates = []
        for doc in cursor:
            doc.pop("_id", None)
            templates.append(Template(**doc))
        return templates

    # ==================== STATS ====================

    def get_stats(self) -> Dict[str, int]:
        """Получить статистику по коллекциям"""
        return {
            "blocks": self.blocks.count_documents({}),
            "rules": self.rules.count_documents({}),
            "documents": self.documents.count_documents({}),
            "templates": self.templates.count_documents({})
        }


# Singleton instance
mongo_repo = MongoRepository()
