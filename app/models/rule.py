"""
Rule Model - правила условной логики
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class RuleOperator(str, Enum):
    """Операторы для условий"""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    AND = "and"
    OR = "or"


class Condition(BaseModel):
    """Условие для правила"""
    field: str = Field(..., description="Поле для проверки")
    operator: RuleOperator = Field(..., description="Оператор сравнения")
    value: Any = Field(..., description="Значение для сравнения")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "arbeitszeit",
                "operator": ">",
                "value": 5.0
            }
        }


class ConditionGroup(BaseModel):
    """Группа условий с логическим оператором"""
    operator: RuleOperator = Field(default=RuleOperator.AND, description="Логический оператор: AND или OR")
    conditions: List[Condition] = Field(..., description="Список условий")

    class Config:
        json_schema_extra = {
            "example": {
                "operator": "and",
                "conditions": [
                    {"field": "arbeitszeit", "operator": ">", "value": 5.0},
                    {"field": "budget_change", "operator": ">=", "value": 10}
                ]
            }
        }


class Action(BaseModel):
    """Действие, выполняемое при срабатывании правила"""
    type: str = Field(..., description="Тип действия: include_block, exclude_block, set_variable")
    target: str = Field(..., description="Целевой блок или переменная")
    params: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные параметры")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "include_block",
                "target": "sgb9_para29",
                "params": {}
            }
        }


class Rule(BaseModel):
    """
    Модель правила для conditional logic
    """
    id: str = Field(..., description="Уникальный идентификатор правила")
    name: str = Field(..., description="Название правила")
    description: Optional[str] = Field(None, description="Описание правила")

    priority: int = Field(default=0, description="Приоритет выполнения (больше = выше)")
    enabled: bool = Field(default=True, description="Активно ли правило")

    # Условия
    condition_group: ConditionGroup = Field(..., description="Группа условий")

    # Действия
    actions: List[Action] = Field(..., description="Действия при срабатывании")

    # Метаданные
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rule_sgb9_para29",
                "name": "Include Persönliches Budget paragraph",
                "description": "Включить §29 при запросе персонального бюджета",
                "priority": 10,
                "enabled": True,
                "condition_group": {
                    "operator": "and",
                    "conditions": [
                        {"field": "budget_request", "operator": "==", "value": True},
                        {"field": "arbeitszeit", "operator": ">", "value": 5.0}
                    ]
                },
                "actions": [
                    {
                        "type": "include_block",
                        "target": "sgb9_para29",
                        "params": {}
                    }
                ],
                "tags": ["sgb9", "budget"]
            }
        }


class RuleCreate(BaseModel):
    """Schema для создания правила"""
    id: str
    name: str
    description: Optional[str] = None
    priority: int = 0
    enabled: bool = True
    condition_group: ConditionGroup
    actions: List[Action]
    tags: List[str] = Field(default_factory=list)


class RuleUpdate(BaseModel):
    """Schema для обновления правила"""
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None
    condition_group: Optional[ConditionGroup] = None
    actions: Optional[List[Action]] = None
    tags: Optional[List[str]] = None


class RuleResponse(Rule):
    """Schema для ответа API"""
    pass


class RuleEvaluationContext(BaseModel):
    """Контекст для оценки правил"""
    variables: Dict[str, Any] = Field(default_factory=dict, description="Переменные контекста")

    class Config:
        json_schema_extra = {
            "example": {
                "variables": {
                    "budget_request": True,
                    "arbeitszeit": 6.5,
                    "budget_change": 15
                }
            }
        }


class RuleEvaluationResult(BaseModel):
    """Результат оценки правила"""
    rule_id: str
    matched: bool
    actions: List[Action] = Field(default_factory=list)
    message: Optional[str] = None
