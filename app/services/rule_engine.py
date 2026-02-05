"""
Rule Engine - оценка и применение правил
"""

from typing import List, Dict, Any, Optional
from app.models import (
    Rule,
    RuleOperator,
    Condition,
    ConditionGroup,
    Action,
    RuleEvaluationContext,
    RuleEvaluationResult
)
from app.repositories import mongo_repo


class RuleEngine:
    """Engine для оценки правил с условной логикой"""

    def __init__(self):
        self.mongo = mongo_repo

    def evaluate_condition(self, condition: Condition, context: Dict[str, Any]) -> bool:
        """
        Оценить одно условие

        :param condition: Условие для оценки
        :param context: Контекст переменных
        :return: True если условие выполнено
        """
        # Получить значение из контекста
        field_value = context.get(condition.field)

        # Если поля нет в контексте, условие False
        if field_value is None:
            return False

        # Оценить оператор
        operator = condition.operator
        target_value = condition.value

        if operator == RuleOperator.EQUALS:
            return field_value == target_value
        elif operator == RuleOperator.NOT_EQUALS:
            return field_value != target_value
        elif operator == RuleOperator.GREATER:
            return field_value > target_value
        elif operator == RuleOperator.GREATER_EQUAL:
            return field_value >= target_value
        elif operator == RuleOperator.LESS:
            return field_value < target_value
        elif operator == RuleOperator.LESS_EQUAL:
            return field_value <= target_value
        elif operator == RuleOperator.IN:
            return field_value in target_value
        elif operator == RuleOperator.NOT_IN:
            return field_value not in target_value
        elif operator == RuleOperator.CONTAINS:
            if isinstance(field_value, str):
                return target_value in field_value
            elif isinstance(field_value, (list, tuple)):
                return target_value in field_value
            return False

        return False

    def evaluate_condition_group(
        self,
        condition_group: ConditionGroup,
        context: Dict[str, Any]
    ) -> bool:
        """
        Оценить группу условий с логическим оператором

        :param condition_group: Группа условий
        :param context: Контекст переменных
        :return: True если группа выполнена
        """
        if not condition_group.conditions:
            return True

        results = [
            self.evaluate_condition(cond, context)
            for cond in condition_group.conditions
        ]

        if condition_group.operator == RuleOperator.AND:
            return all(results)
        elif condition_group.operator == RuleOperator.OR:
            return any(results)

        return False

    def evaluate_rule(
        self,
        rule: Rule,
        context: Dict[str, Any]
    ) -> RuleEvaluationResult:
        """
        Оценить правило

        :param rule: Правило
        :param context: Контекст переменных
        :return: Результат оценки
        """
        if not rule.enabled:
            return RuleEvaluationResult(
                rule_id=rule.id,
                matched=False,
                message="Rule is disabled"
            )

        matched = self.evaluate_condition_group(rule.condition_group, context)

        return RuleEvaluationResult(
            rule_id=rule.id,
            matched=matched,
            actions=rule.actions if matched else [],
            message=f"Rule {rule.name} evaluated: {'matched' if matched else 'not matched'}"
        )

    def evaluate_all_rules(
        self,
        context: RuleEvaluationContext
    ) -> List[RuleEvaluationResult]:
        """
        Оценить все активные правила

        :param context: Контекст для оценки
        :return: Список результатов оценки
        """
        # Получить все активные правила отсортированные по приоритету
        rules = self.mongo.get_enabled_rules()

        results = []
        for rule in rules:
            result = self.evaluate_rule(rule, context.variables)
            results.append(result)

        return results

    def get_matched_actions(
        self,
        context: RuleEvaluationContext
    ) -> List[Action]:
        """
        Получить все действия из сработавших правил

        :param context: Контекст для оценки
        :return: Список действий
        """
        results = self.evaluate_all_rules(context)

        actions = []
        for result in results:
            if result.matched:
                actions.extend(result.actions)

        return actions

    def get_blocks_to_include(
        self,
        context: RuleEvaluationContext
    ) -> List[str]:
        """
        Получить список ID блоков для включения на основе правил

        :param context: Контекст для оценки
        :return: Список ID блоков
        """
        actions = self.get_matched_actions(context)

        block_ids = []
        for action in actions:
            if action.type == "include_block":
                block_ids.append(action.target)

        return list(set(block_ids))  # Убрать дубликаты

    def apply_actions(
        self,
        actions: List[Action],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Применить действия к состоянию

        :param actions: Список действий
        :param state: Текущее состояние
        :return: Обновленное состояние
        """
        new_state = state.copy()

        for action in actions:
            if action.type == "set_variable":
                new_state[action.target] = action.params.get("value")
            elif action.type == "include_block":
                if "included_blocks" not in new_state:
                    new_state["included_blocks"] = []
                if action.target not in new_state["included_blocks"]:
                    new_state["included_blocks"].append(action.target)
            elif action.type == "exclude_block":
                if "excluded_blocks" not in new_state:
                    new_state["excluded_blocks"] = []
                if action.target not in new_state["excluded_blocks"]:
                    new_state["excluded_blocks"].append(action.target)

        return new_state

    async def create_rule(self, rule: Rule) -> bool:
        """
        Создать новое правило

        :param rule: Правило
        :return: True если успешно
        """
        return self.mongo.create_rule(rule)

    async def get_rule(self, rule_id: str) -> Optional[Rule]:
        """
        Получить правило по ID

        :param rule_id: ID правила
        :return: Правило или None
        """
        return self.mongo.get_rule(rule_id)

    async def update_rule(self, rule_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Обновить правило

        :param rule_id: ID правила
        :param update_data: Данные для обновления
        :return: True если успешно
        """
        return self.mongo.update_rule(rule_id, update_data)

    async def delete_rule(self, rule_id: str) -> bool:
        """
        Удалить правило

        :param rule_id: ID правила
        :return: True если успешно
        """
        return self.mongo.delete_rule(rule_id)


# Singleton instance
rule_engine = RuleEngine()
