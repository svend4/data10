"""
Document Model - модели для сборки документов
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    """Статус документа"""
    DRAFT = "draft"
    ASSEMBLED = "assembled"
    REVIEWED = "reviewed"
    FINALIZED = "finalized"


class DocumentFormat(str, Enum):
    """Формат экспорта документа"""
    HTML = "html"
    MARKDOWN = "markdown"
    DOCX = "docx"
    PDF = "pdf"
    JSON = "json"


class TemplateSection(BaseModel):
    """Секция шаблона документа"""
    id: str = Field(..., description="ID секции")
    type: str = Field(..., description="Тип: header, content, footer")
    required: bool = Field(default=True, description="Обязательна ли секция")
    blocks: List[str] = Field(default_factory=list, description="ID блоков для включения")
    content: Optional[str] = Field(None, description="Статический контент")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Условия включения")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "legal_basis",
                "type": "content",
                "required": True,
                "blocks": ["sgb9_para29"],
                "conditions": {"budget_request": True}
            }
        }


class Template(BaseModel):
    """Шаблон документа"""
    id: str = Field(..., description="ID шаблона")
    name: str = Field(..., description="Название шаблона")
    description: Optional[str] = Field(None, description="Описание")
    sections: List[TemplateSection] = Field(..., description="Секции шаблона")
    tags: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "widerspruch_template",
                "name": "Widerspruch gegen Bescheid",
                "description": "Vorlage für Widerspruch",
                "sections": [
                    {
                        "id": "header",
                        "type": "header",
                        "required": True,
                        "blocks": ["sender_address", "recipient_address"]
                    },
                    {
                        "id": "legal_basis",
                        "type": "content",
                        "required": True,
                        "blocks": ["sgb9_para29"],
                        "conditions": {"budget_request": True}
                    }
                ],
                "tags": ["widerspruch", "legal"]
            }
        }


class DocumentBlock(BaseModel):
    """Блок в составе документа"""
    block_id: str
    content: str
    order: int
    level: int


class Document(BaseModel):
    """
    Модель собранного документа
    """
    id: str = Field(..., description="ID документа")
    title: str = Field(..., description="Заголовок документа")
    template_id: Optional[str] = Field(None, description="ID использованного шаблона")

    status: DocumentStatus = Field(default=DocumentStatus.DRAFT)

    # Блоки документа
    blocks: List[DocumentBlock] = Field(default_factory=list, description="Блоки в документе")

    # Контекст сборки
    context: Dict[str, Any] = Field(default_factory=dict, description="Контекст переменных")

    # Метаданные
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_widerspruch_001",
                "title": "Widerspruch gegen Bescheid vom 15.01.2024",
                "template_id": "widerspruch_template",
                "status": "draft",
                "blocks": [
                    {
                        "block_id": "sgb9_para29",
                        "content": "§29 Persönliches Budget...",
                        "order": 1,
                        "level": 1
                    }
                ],
                "context": {
                    "budget_request": True,
                    "bescheid_date": "15.01.2024"
                },
                "tags": ["widerspruch"]
            }
        }


class AssemblyRequest(BaseModel):
    """Запрос на сборку документа"""
    template_id: str = Field(..., description="ID шаблона")
    context: Dict[str, Any] = Field(..., description="Контекст переменных")
    title: Optional[str] = Field(None, description="Заголовок документа")

    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "widerspruch_template",
                "context": {
                    "budget_request": True,
                    "arbeitszeit": 6.5,
                    "bescheid_date": "15.01.2024"
                },
                "title": "Widerspruch gegen Bescheid vom 15.01.2024"
            }
        }


class AssemblyResponse(BaseModel):
    """Результат сборки документа"""
    document: Document
    blocks_included: int
    rules_applied: int
    message: Optional[str] = None


class ExportRequest(BaseModel):
    """Запрос на экспорт документа"""
    document_id: str
    format: DocumentFormat = DocumentFormat.DOCX

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_widerspruch_001",
                "format": "docx"
            }
        }


class DocumentCreate(BaseModel):
    """Schema для создания документа"""
    id: str
    title: str
    template_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class DocumentUpdate(BaseModel):
    """Schema для обновления документа"""
    title: Optional[str] = None
    status: Optional[DocumentStatus] = None
    blocks: Optional[List[DocumentBlock]] = None
    tags: Optional[List[str]] = None


class DocumentResponse(Document):
    """Schema для ответа API"""
    pass
