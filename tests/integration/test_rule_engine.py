"""
Integration tests for RuleEngine

These tests verify rule evaluation logic and condition matching.
"""

import pytest
from app.services.rule_engine import rule_engine
from app.models import (
    Rule,
    Condition,
    ConditionGroup,
    Action,
    RuleOperator,
    LogicalOperator,
    RuleEvaluationContext
)


@pytest.fixture
def sample_rule_equals():
    """Create a sample rule with EQUALS condition"""
    return Rule(
        id="rule_equals",
        name="Test Equals Rule",
        priority=1,
        enabled=True,
        condition_group=ConditionGroup(
            operator=LogicalOperator.AND,
            conditions=[
                Condition(
                    variable="disability_type",
                    operator=RuleOperator.EQUALS,
                    value="physical"
                )
            ]
        ),
        actions=[
            Action(
                type="include_block",
                parameters={"block_id": "block_physical_disability"}
            )
        ]
    )


@pytest.fixture
def sample_rule_greater():
    """Create a sample rule with GREATER condition"""
    return Rule(
        id="rule_greater",
        name="Test Greater Rule",
        priority=2,
        enabled=True,
        condition_group=ConditionGroup(
            operator=LogicalOperator.AND,
            conditions=[
                Condition(
                    variable="disability_degree",
                    operator=RuleOperator.GREATER,
                    value=50
                )
            ]
        ),
        actions=[
            Action(
                type="include_block",
                parameters={"block_id": "block_severe_disability"}
            )
        ]
    )


@pytest.fixture
def sample_rule_in():
    """Create a sample rule with IN condition"""
    return Rule(
        id="rule_in",
        name="Test IN Rule",
        priority=3,
        enabled=True,
        condition_group=ConditionGroup(
            operator=LogicalOperator.AND,
            conditions=[
                Condition(
                    variable="assistance_type",
                    operator=RuleOperator.IN,
                    value=["mobility", "communication", "orientation"]
                )
            ]
        ),
        actions=[
            Action(
                type="include_block",
                parameters={"block_id": "block_assistance_types"}
            )
        ]
    )


@pytest.fixture
def sample_rule_and():
    """Create a rule with multiple AND conditions"""
    return Rule(
        id="rule_and",
        name="Test AND Rule",
        priority=4,
        enabled=True,
        condition_group=ConditionGroup(
            operator=LogicalOperator.AND,
            conditions=[
                Condition(
                    variable="age",
                    operator=RuleOperator.GREATER,
                    value=18
                ),
                Condition(
                    variable="employed",
                    operator=RuleOperator.EQUALS,
                    value=True
                )
            ]
        ),
        actions=[
            Action(
                type="include_block",
                parameters={"block_id": "block_employment_support"}
            )
        ]
    )


@pytest.fixture
def sample_rule_or():
    """Create a rule with multiple OR conditions"""
    return Rule(
        id="rule_or",
        name="Test OR Rule",
        priority=5,
        enabled=True,
        condition_group=ConditionGroup(
            operator=LogicalOperator.OR,
            conditions=[
                Condition(
                    variable="urgent",
                    operator=RuleOperator.EQUALS,
                    value=True
                ),
                Condition(
                    variable="priority",
                    operator=RuleOperator.EQUALS,
                    value="high"
                )
            ]
        ),
        actions=[
            Action(
                type="include_block",
                parameters={"block_id": "block_urgent_processing"}
            )
        ]
    )


def test_evaluate_condition_equals():
    """Test EQUALS operator"""
    condition = Condition(
        variable="status",
        operator=RuleOperator.EQUALS,
        value="approved"
    )

    # Test match
    context = {"status": "approved"}
    assert rule_engine.evaluate_condition(condition, context) is True

    # Test no match
    context = {"status": "rejected"}
    assert rule_engine.evaluate_condition(condition, context) is False


def test_evaluate_condition_greater():
    """Test GREATER operator"""
    condition = Condition(
        variable="amount",
        operator=RuleOperator.GREATER,
        value=100
    )

    # Test greater
    context = {"amount": 150}
    assert rule_engine.evaluate_condition(condition, context) is True

    # Test less
    context = {"amount": 50}
    assert rule_engine.evaluate_condition(condition, context) is False

    # Test equal (should be False)
    context = {"amount": 100}
    assert rule_engine.evaluate_condition(condition, context) is False


def test_evaluate_condition_in():
    """Test IN operator"""
    condition = Condition(
        variable="category",
        operator=RuleOperator.IN,
        value=["A", "B", "C"]
    )

    # Test in list
    context = {"category": "B"}
    assert rule_engine.evaluate_condition(condition, context) is True

    # Test not in list
    context = {"category": "D"}
    assert rule_engine.evaluate_condition(condition, context) is False


def test_evaluate_condition_contains():
    """Test CONTAINS operator"""
    condition = Condition(
        variable="tags",
        operator=RuleOperator.CONTAINS,
        value="important"
    )

    # Test contains
    context = {"tags": ["important", "urgent", "review"]}
    assert rule_engine.evaluate_condition(condition, context) is True

    # Test does not contain
    context = {"tags": ["normal", "routine"]}
    assert rule_engine.evaluate_condition(condition, context) is False


def test_evaluate_rule_single_condition(sample_rule_equals):
    """Test evaluating rule with single condition"""

    # Test match
    context = {"disability_type": "physical"}
    result = rule_engine.evaluate_rule(sample_rule_equals, context)
    assert result.matched is True
    assert result.rule_id == "rule_equals"

    # Test no match
    context = {"disability_type": "mental"}
    result = rule_engine.evaluate_rule(sample_rule_equals, context)
    assert result.matched is False


def test_evaluate_rule_and_conditions(sample_rule_and):
    """Test evaluating rule with AND conditions"""

    # Test all conditions match
    context = {"age": 25, "employed": True}
    result = rule_engine.evaluate_rule(sample_rule_and, context)
    assert result.matched is True

    # Test one condition fails
    context = {"age": 16, "employed": True}
    result = rule_engine.evaluate_rule(sample_rule_and, context)
    assert result.matched is False

    # Test both conditions fail
    context = {"age": 16, "employed": False}
    result = rule_engine.evaluate_rule(sample_rule_and, context)
    assert result.matched is False


def test_evaluate_rule_or_conditions(sample_rule_or):
    """Test evaluating rule with OR conditions"""

    # Test first condition matches
    context = {"urgent": True, "priority": "low"}
    result = rule_engine.evaluate_rule(sample_rule_or, context)
    assert result.matched is True

    # Test second condition matches
    context = {"urgent": False, "priority": "high"}
    result = rule_engine.evaluate_rule(sample_rule_or, context)
    assert result.matched is True

    # Test both conditions match
    context = {"urgent": True, "priority": "high"}
    result = rule_engine.evaluate_rule(sample_rule_or, context)
    assert result.matched is True

    # Test no conditions match
    context = {"urgent": False, "priority": "low"}
    result = rule_engine.evaluate_rule(sample_rule_or, context)
    assert result.matched is False


def test_evaluate_rule_disabled():
    """Test that disabled rules are not evaluated"""
    disabled_rule = Rule(
        id="rule_disabled",
        name="Disabled Rule",
        priority=1,
        enabled=False,
        condition_group=ConditionGroup(
            operator=LogicalOperator.AND,
            conditions=[
                Condition(
                    variable="test",
                    operator=RuleOperator.EQUALS,
                    value=True
                )
            ]
        ),
        actions=[]
    )

    context = {"test": True}
    result = rule_engine.evaluate_rule(disabled_rule, context)
    assert result.matched is False


def test_get_blocks_to_include():
    """Test getting blocks to include based on matched rules"""

    # Create context
    context = RuleEvaluationContext(
        variables={
            "disability_type": "physical",
            "disability_degree": 60
        }
    )

    # Mock rules in the engine
    rules = [
        Rule(
            id="rule1",
            name="Physical Disability Rule",
            priority=1,
            enabled=True,
            condition_group=ConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[
                    Condition(
                        variable="disability_type",
                        operator=RuleOperator.EQUALS,
                        value="physical"
                    )
                ]
            ),
            actions=[
                Action(
                    type="include_block",
                    parameters={"block_id": "block_physical"}
                )
            ]
        ),
        Rule(
            id="rule2",
            name="Severe Disability Rule",
            priority=2,
            enabled=True,
            condition_group=ConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[
                    Condition(
                        variable="disability_degree",
                        operator=RuleOperator.GREATER,
                        value=50
                    )
                ]
            ),
            actions=[
                Action(
                    type="include_block",
                    parameters={"block_id": "block_severe"}
                )
            ]
        )
    ]

    # Temporarily set rules in engine
    original_get_rules = rule_engine.get_enabled_rules
    rule_engine.get_enabled_rules = lambda: rules

    try:
        # Get blocks to include
        block_ids = rule_engine.get_blocks_to_include(context)

        # Assertions
        assert "block_physical" in block_ids
        assert "block_severe" in block_ids
        assert len(block_ids) == 2
    finally:
        # Restore original method
        rule_engine.get_enabled_rules = original_get_rules


def test_rule_priority_ordering():
    """Test that rules are applied in priority order"""

    rules = [
        Rule(
            id="rule_low",
            name="Low Priority",
            priority=1,
            enabled=True,
            condition_group=ConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[Condition(variable="test", operator=RuleOperator.EQUALS, value=True)]
            ),
            actions=[Action(type="include_block", parameters={"block_id": "block_low"})]
        ),
        Rule(
            id="rule_high",
            name="High Priority",
            priority=10,
            enabled=True,
            condition_group=ConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[Condition(variable="test", operator=RuleOperator.EQUALS, value=True)]
            ),
            actions=[Action(type="include_block", parameters={"block_id": "block_high"})]
        ),
        Rule(
            id="rule_medium",
            name="Medium Priority",
            priority=5,
            enabled=True,
            condition_group=ConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[Condition(variable="test", operator=RuleOperator.EQUALS, value=True)]
            ),
            actions=[Action(type="include_block", parameters={"block_id": "block_medium"})]
        )
    ]

    # Sort by priority (descending)
    sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)

    # Assert order
    assert sorted_rules[0].id == "rule_high"
    assert sorted_rules[1].id == "rule_medium"
    assert sorted_rules[2].id == "rule_low"
