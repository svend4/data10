"""
Block Model - основная единица контента
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BlockMetadata(BaseModel):
    """Метаданные блока"""
    law: Optional[str] = None  # SGB IX, BGB, GG
    paragraph: Optional[str] = None  # §5, §29
    absatz: Optional[int] = None  # Absatz number
    satz: Optional[int] = None  # Satz number
    language: str = "de"
    effective_date: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom: Dict[str, Any] = Field(default_factory=dict)


class BlockRelationships(BaseModel):
    """Связи блока с другими блоками"""
    references: List[str] = Field(default_factory=list)  # Ссылки на другие блоки
    parent: Optional[str] = None  # Родительский блок
    children: List[str] = Field(default_factory=list)  # Дочерние блоки
    related: List[str] = Field(default_factory=list)  # Семантически связанные блоки


class Block(BaseModel):
    """
    Основная модель информационного блока
    """
    id: str = Field(..., description="Уникальный идентификатор блока")
    type: str = Field(..., description="Тип блока: paragraph, section, article")
    title: str = Field(..., description="Заголовок блока")
    content: str = Field(..., description="Содержимое блока")
    source: str = Field(..., description="Источник: SGB IX, BGB, Custom")
    level: int = Field(default=1, description="Уровень детализации")

    metadata: BlockMetadata = Field(default_factory=BlockMetadata)
    relationships: BlockRelationships = Field(default_factory=BlockRelationships)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, description="Версия блока")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sgb9_para29",
                "type": "paragraph",
                "title": "§29 Persönliches Budget",
                "content": "Auf Antrag der Leistungsberechtigten...",
                "source": "SGB IX",
                "level": 1,
                "metadata": {
                    "law": "SGB IX",
                    "paragraph": "29",
                    "language": "de",
                    "tags": ["persönliches budget", "teilhabe"]
                },
                "relationships": {
                    "references": ["sgb9_para5"],
                    "parent": None,
                    "children": ["sgb9_para29_abs1", "sgb9_para29_abs2"]
                }
            }
        }


class BlockCreate(BaseModel):
    """Schema для создания нового блока"""
    id: str
    type: str
    title: str
    content: str
    source: str
    level: int = 1
    metadata: Optional[BlockMetadata] = None
    relationships: Optional[BlockRelationships] = None


class BlockUpdate(BaseModel):
    """Schema для обновления блока"""
    title: Optional[str] = None
    content: Optional[str] = None
    level: Optional[int] = None
    metadata: Optional[BlockMetadata] = None
    relationships: Optional[BlockRelationships] = None


class BlockResponse(Block):
    """Schema для ответа API"""
    pass
