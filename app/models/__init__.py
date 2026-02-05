"""
Models package
"""

from .block import (
    Block,
    BlockMetadata,
    BlockRelationships,
    BlockCreate,
    BlockUpdate,
    BlockResponse,
)

from .rule import (
    Rule,
    RuleOperator,
    Condition,
    ConditionGroup,
    Action,
    RuleCreate,
    RuleUpdate,
    RuleResponse,
    RuleEvaluationContext,
    RuleEvaluationResult,
)

from .document import (
    Document,
    DocumentStatus,
    DocumentFormat,
    Template,
    TemplateSection,
    DocumentBlock,
    AssemblyRequest,
    AssemblyResponse,
    ExportRequest,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
)

from .version import (
    BlockVersion,
    VersionDiff,
    BlockVersionCreate,
    VersionHistory,
)

__all__ = [
    # Block
    "Block",
    "BlockMetadata",
    "BlockRelationships",
    "BlockCreate",
    "BlockUpdate",
    "BlockResponse",
    # Rule
    "Rule",
    "RuleOperator",
    "Condition",
    "ConditionGroup",
    "Action",
    "RuleCreate",
    "RuleUpdate",
    "RuleResponse",
    "RuleEvaluationContext",
    "RuleEvaluationResult",
    # Document
    "Document",
    "DocumentStatus",
    "DocumentFormat",
    "Template",
    "TemplateSection",
    "DocumentBlock",
    "AssemblyRequest",
    "AssemblyResponse",
    "ExportRequest",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    # Version
    "BlockVersion",
    "VersionDiff",
    "BlockVersionCreate",
    "VersionHistory",
]
