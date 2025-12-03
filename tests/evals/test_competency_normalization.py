"""Unit tests for competency test parameter normalization."""

from tests.evals.competency_test import CompetencyTest
from tests.evals.mcp_tool_tracer import MockedMCPServer


class MockCompetencyTest(CompetencyTest):
    """Mock implementation for testing."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """No-op for testing."""


def test_normalize_optional_models_with_empty_dict():
    """Test that empty dict is normalized to None."""
    test = MockCompetencyTest(
        query="test",
        expected_tools=[],
    )

    params = {"query_model": {}}
    normalized = test._normalize_optional_models(params)

    assert normalized["query_model"] is None


def test_normalize_optional_models_with_none():
    """Test that None remains None."""
    test = MockCompetencyTest(
        query="test",
        expected_tools=[],
    )

    params = {"query_model": None}
    normalized = test._normalize_optional_models(params)

    assert normalized["query_model"] is None


def test_normalize_optional_models_with_values():
    """Test that non-empty dict is preserved."""
    test = MockCompetencyTest(
        query="test",
        expected_tools=[],
    )

    params = {"query_model": {"limit": 10, "query": "test"}}
    normalized = test._normalize_optional_models(params)

    assert normalized["query_model"] == {"limit": 10, "query": "test"}


def test_normalize_optional_models_nested():
    """Test that nested empty dicts are normalized."""
    test = MockCompetencyTest(
        query="test",
        expected_tools=[],
    )

    params = {
        "outer": {"inner": {}, "value": "test"},
        "query_model": {},
    }
    normalized = test._normalize_optional_models(params)

    assert normalized["query_model"] is None
    assert normalized["outer"]["inner"] is None
    assert normalized["outer"]["value"] == "test"


def test_params_are_compatible_null_vs_empty():
    """Test that None and {} are considered compatible."""
    test = MockCompetencyTest(
        query="test",
        expected_tools=[],
    )

    # Test that None and {} are compatible
    expected = {"query_model": None}
    actual = {"query_model": {}}

    assert test._params_are_compatible(expected, actual)


def test_params_are_compatible_empty_vs_null():
    """Test that {} and None are considered compatible (reverse)."""
    test = MockCompetencyTest(
        query="test",
        expected_tools=[],
    )

    # Test the reverse: expected has {}, actual has None
    expected = {"query_model": {}}
    actual = {"query_model": None}

    assert test._params_are_compatible(expected, actual)


def test_params_are_compatible_both_null():
    """Test that None and None are compatible."""
    test = MockCompetencyTest(
        query="test",
        expected_tools=[],
    )

    expected = {"query_model": None}
    actual = {"query_model": None}

    assert test._params_are_compatible(expected, actual)


def test_params_are_compatible_both_empty():
    """Test that {} and {} are compatible."""
    test = MockCompetencyTest(
        query="test",
        expected_tools=[],
    )

    expected = {"query_model": {}}
    actual = {"query_model": {}}

    assert test._params_are_compatible(expected, actual)


def test_params_are_compatible_with_values():
    """Test that actual values still need to match."""
    test = MockCompetencyTest(
        query="test",
        expected_tools=[],
    )

    expected = {"query_model": {"limit": 10}}
    actual = {"query_model": {"limit": 5}}

    # Values don't match, should not be compatible
    assert not test._params_are_compatible(expected, actual)

    # Exact match should be compatible
    actual = {"query_model": {"limit": 10}}
    assert test._params_are_compatible(expected, actual)
