"""
Block Version Model - для отслеживания истории изменений блоков
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BlockVersion(BaseModel):
    """
    Версия блока - снимок состояния блока в определённый момент времени
    """
    id: str = Field(..., description="ID версии (block_id:version_number)")
    block_id: str = Field(..., description="ID блока")
    version: int = Field(..., description="Номер версии")

    # Snapshot данных блока
    type: str = Field(..., description="Тип блока")
    title: str = Field(..., description="Заголовок блока")
    content: str = Field(..., description="Содержимое блока")
    source: str = Field(..., description="Источник")
    level: int = Field(..., description="Уровень детализации")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, Any] = Field(default_factory=dict)

    # Информация об изменении
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Когда создана версия")
    created_by: Optional[str] = Field(None, description="Кто создал версию (user_id)")
    change_summary: Optional[str] = Field(None, description="Краткое описание изменений")
    is_current: bool = Field(default=False, description="Текущая версия")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sgb9_para5:2",
                "block_id": "sgb9_para5",
                "version": 2,
                "type": "paragraph",
                "title": "§ 5 SGB IX - Leistungen zur Teilhabe (updated)",
                "content": "Updated content...",
                "source": "SGB IX",
                "level": 1,
                "metadata": {"law": "SGB IX", "paragraph": "§5"},
                "relationships": {"parent": None, "children": []},
                "created_at": "2024-01-20T14:30:00",
                "created_by": "user_123",
                "change_summary": "Updated title and content",
                "is_current": True
            }
        }


class VersionDiff(BaseModel):
    """
    Разница между двумя версиями блока
    """
    block_id: str = Field(..., description="ID блока")
    old_version: int = Field(..., description="Старая версия")
    new_version: int = Field(..., description="Новая версия")

    changes: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Изменения по полям: {field: {old: value, new: value}}"
    )

    changed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "block_id": "sgb9_para5",
                "old_version": 1,
                "new_version": 2,
                "changes": {
                    "title": {
                        "old": "§ 5 SGB IX - Leistungen zur Teilhabe",
                        "new": "§ 5 SGB IX - Leistungen zur Teilhabe (updated)"
                    },
                    "content": {
                        "old": "Old content...",
                        "new": "New content..."
                    }
                },
                "changed_at": "2024-01-20T14:30:00"
            }
        }


class BlockVersionCreate(BaseModel):
    """Создание новой версии блока"""
    block_id: str = Field(..., description="ID блока")
    change_summary: Optional[str] = Field(None, description="Описание изменений")
    created_by: Optional[str] = Field(None, description="Автор изменений")


class VersionHistory(BaseModel):
    """История версий блока"""
    block_id: str = Field(..., description="ID блока")
    total_versions: int = Field(..., description="Общее количество версий")
    current_version: int = Field(..., description="Текущая версия")
    versions: list[BlockVersion] = Field(default_factory=list, description="Список версий")

    class Config:
        json_schema_extra = {
            "example": {
                "block_id": "sgb9_para5",
                "total_versions": 3,
                "current_version": 3,
                "versions": [
                    {
                        "version": 1,
                        "created_at": "2024-01-15T10:00:00",
                        "change_summary": "Initial version"
                    },
                    {
                        "version": 2,
                        "created_at": "2024-01-18T14:30:00",
                        "change_summary": "Updated content"
                    },
                    {
                        "version": 3,
                        "created_at": "2024-01-20T16:45:00",
                        "change_summary": "Fixed typo",
                        "is_current": True
                    }
                ]
            }
        }
