"""
Assembly Service - сборка документов из блоков
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from app.models import (
    Document,
    DocumentBlock,
    DocumentStatus,
    Template,
    AssemblyRequest,
    AssemblyResponse,
    RuleEvaluationContext
)
from app.repositories import mongo_repo
from app.services.block_service import block_service
from app.services.rule_engine import rule_engine


class AssemblyService:
    """Сервис для сборки документов из блоков"""

    def __init__(self):
        self.mongo = mongo_repo
        self.block_service = block_service
        self.rule_engine = rule_engine

    async def assemble_document(
        self,
        request: AssemblyRequest
    ) -> AssemblyResponse:
        """
        Собрать документ по запросу

        :param request: Запрос на сборку
        :return: Результат сборки
        """
        # Получить шаблон
        template = self.mongo.get_template(request.template_id)
        if not template:
            raise ValueError(f"Template {request.template_id} not found")

        # Оценить правила для определения каких блоков включать
        context = RuleEvaluationContext(variables=request.context)
        block_ids_from_rules = self.rule_engine.get_blocks_to_include(context)

        # Собрать блоки из секций шаблона
        blocks_to_include = []
        rules_applied = 0

        for section in template.sections:
            # Проверить условия секции
            if section.conditions:
                section_matches = self._check_section_conditions(
                    section.conditions,
                    request.context
                )
                if not section_matches:
                    continue

            # Добавить блоки из секции
            blocks_to_include.extend(section.blocks)

        # Добавить блоки из правил
        blocks_to_include.extend(block_ids_from_rules)
        rules_applied = len(block_ids_from_rules)

        # Убрать дубликаты, сохранив порядок
        unique_blocks = list(dict.fromkeys(blocks_to_include))

        # Получить полные блоки из БД
        document_blocks = []
        for order, block_id in enumerate(unique_blocks):
            block = await self.block_service.get_block(block_id)
            if block:
                doc_block = DocumentBlock(
                    block_id=block.id,
                    content=block.content,
                    order=order,
                    level=block.level
                )
                document_blocks.append(doc_block)

        # Создать документ
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        title = request.title or f"Document from {template.name}"

        document = Document(
            id=document_id,
            title=title,
            template_id=request.template_id,
            status=DocumentStatus.ASSEMBLED,
            blocks=document_blocks,
            context=request.context
        )

        # Сохранить документ
        self.mongo.create_document(document)

        return AssemblyResponse(
            document=document,
            blocks_included=len(document_blocks),
            rules_applied=rules_applied,
            message=f"Document assembled successfully with {len(document_blocks)} blocks"
        )

    def _check_section_conditions(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Проверить условия секции шаблона

        :param conditions: Условия секции
        :param context: Контекст переменных
        :return: True если условия выполнены
        """
        for key, expected_value in conditions.items():
            actual_value = context.get(key)
            if actual_value != expected_value:
                return False
        return True

    async def create_template(self, template: Template) -> bool:
        """
        Создать шаблон документа

        :param template: Шаблон
        :return: True если успешно
        """
        return self.mongo.create_template(template)

    async def get_template(self, template_id: str) -> Optional[Template]:
        """
        Получить шаблон

        :param template_id: ID шаблона
        :return: Шаблон или None
        """
        return self.mongo.get_template(template_id)

    async def list_templates(self) -> List[Template]:
        """
        Получить список всех шаблонов

        :return: Список шаблонов
        """
        return self.mongo.list_templates()

    async def get_document(self, document_id: str) -> Optional[Document]:
        """
        Получить документ

        :param document_id: ID документа
        :return: Документ или None
        """
        return self.mongo.get_document(document_id)

    async def list_documents(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """
        Получить список документов

        :param limit: Лимит
        :param offset: Смещение
        :return: Список документов
        """
        return self.mongo.list_documents(limit=limit, offset=offset)

    async def update_document_status(
        self,
        document_id: str,
        status: DocumentStatus
    ) -> bool:
        """
        Обновить статус документа

        :param document_id: ID документа
        :param status: Новый статус
        :return: True если успешно
        """
        return self.mongo.update_document(document_id, {"status": status})

    async def render_document_text(self, document_id: str) -> str:
        """
        Рендеринг документа в текстовый формат

        :param document_id: ID документа
        :return: Текст документа
        """
        document = await self.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        lines = []
        lines.append(f"# {document.title}\n")

        for doc_block in sorted(document.blocks, key=lambda b: b.order):
            # Отступ по уровню
            indent = "  " * (doc_block.level - 1)
            lines.append(f"{indent}{doc_block.content}\n")

        return "\n".join(lines)

    async def export_document_markdown(self, document_id: str) -> str:
        """
        Экспорт документа в Markdown формат

        :param document_id: ID документа
        :return: Markdown текст
        """
        document = await self.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        lines = []
        lines.append(f"# {document.title}\n")
        lines.append(f"**Status**: {document.status}")
        lines.append(f"**Created**: {document.created_at.strftime('%Y-%m-%d %H:%M')}\n")

        if document.template_id:
            lines.append(f"**Template**: {document.template_id}\n")

        lines.append("---\n")

        for doc_block in sorted(document.blocks, key=lambda b: b.order):
            # Заголовки по уровню
            heading = "#" * min(doc_block.level + 1, 6)
            lines.append(f"{heading} Block {doc_block.block_id}\n")
            lines.append(f"{doc_block.content}\n")

        return "\n".join(lines)


# Singleton instance
assembly_service = AssemblyService()
