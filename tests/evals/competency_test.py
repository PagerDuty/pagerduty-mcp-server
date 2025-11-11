"""Common test fixtures for MCP tool call evaluation."""

from abc import ABC, abstractmethod
from typing import Any

from deepdiff import DeepDiff

from .mcp_tool_tracer import MockedMCPServer


class CompetencyTest(ABC):
    """A base class for competency tests that helps define and verify expected tool calls."""

    def __init__(
        self,
        query: str,
        expected_tools: list[dict[str, Any]],
        allowed_helper_tools: list[str] | None = None,
        description: str | None = None,
        max_conversation_turns: int = 5,
        model: str = "gpt-4.1",
    ):
        """Initialize a competency test case.

        Args:
            query: The user query to test
            expected_tools: List of expected tool calls with parameters
            allowed_helper_tools: List of tool names that are allowed to be called
            description: Optional description of the test case
            max_conversation_turns: Maximum number of conversation turns allowed
            model: The model to use for the test (default: "gpt-4.1")
        """
        self.query = query
        self.expected_tools = expected_tools
        self.allowed_helper_tools = allowed_helper_tools
        self.description = description or query
        self.max_conversation_turns = max_conversation_turns
        self.model = model

    @abstractmethod
    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register mock responses for the expected tool calls.

        This is a placeholder method - implementations should
        override this with domain-specific mock responses.

        Args:
            mcp: The tool tracer to register responses with
        """

    def verify_tool_calls(self, mcp: MockedMCPServer) -> bool:
        """Verify that the expected incident tools were called correctly."""
        # Check that all expected incident tools were called
        for expected in self.expected_tools:
            tool_name = expected["tool_name"]
            expected_params = expected.get("parameters", {})

            if not self._verify_tool_called(mcp, tool_name, expected_params):
                print(f"Expected tool {tool_name} was not called correctly")
                return False

        # Check that no disallowed tools were called
        if self.allowed_helper_tools:
            all_called_tools = mcp.get_called_tool_names()
            expected_tool_names = {tool["tool_name"] for tool in self.expected_tools}
            allowed_tools = set(self.allowed_helper_tools) | expected_tool_names

            for tool_name in all_called_tools:
                if tool_name not in allowed_tools:
                    print(f"Disallowed tool {tool_name} was called")
                    return False
        return True

    def _verify_tool_called(self, mcp: MockedMCPServer, tool_name: str, expected_params: dict[str, Any]) -> bool:
        """Verify a tool was called with expected parameters."""
        actual_calls = mcp.get_calls_for_tool(tool_name)
        if not actual_calls:
            return False

        return any(self._params_are_compatible(expected_params, call["parameters"]) for call in actual_calls)

    def _params_are_compatible(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Check if actual parameters are compatible with expected ones.

        Compatible means:
        1. All expected fields are present with correct values
        2. Additional fields in actual are allowed (flexible)
        3. Nested objects are checked
        4. None and {} are considered equivalent for optional model parameters

        Args:
            expected: Expected parameter structure
            actual: Actual parameters from LLM call

        Returns:
            True if parameters are compatible
        """
        if not self._has_required_structure(expected, actual):
            return False

        # For Alert Grouping Settings, use specialized validation
        if self._is_alert_grouping_tool_call(expected, actual):
            return self._validate_alert_grouping_params(expected, actual)

        # Normalize parameters before comparison (treat None and {} as equivalent)
        normalized_expected = self._normalize_optional_models(expected)
        normalized_actual = self._normalize_optional_models(actual)

        # Default to strict validation for other domains
        diff = DeepDiff(normalized_expected, normalized_actual, ignore_order=True)

        compatibility_issues = []

        # Missing keys/values (these break compatibility)
        # Storing the details in case we want to log them
        if "dictionary_item_removed" in diff:
            compatibility_issues.extend(diff["dictionary_item_removed"])
        if "iterable_item_removed" in diff:
            compatibility_issues.extend(diff["iterable_item_removed"])
        if "values_changed" in diff:
            compatibility_issues.extend(
                [f"{k}: {v['old_value']} -> {v['new_value']}" for k, v in diff["values_changed"].items()]
            )
        if "type_changes" in diff:
            compatibility_issues.extend(
                [f"{k}: {v['old_type']} -> {v['new_type']}" for k, v in diff["type_changes"].items()]
            )

        return len(compatibility_issues) == 0

    def _normalize_optional_models(self, params: dict[str, Any]) -> dict[str, Any]:
        """Normalize optional model parameters by treating None and {} as equivalent.

        This handles the case where LLMs may pass either:
        - {"query_model": null} (explicit None)
        - {"query_model": {}} (empty object)

        Both are functionally equivalent for optional Pydantic model parameters,
        as they result in the same default behavior in the tool implementation.

        Args:
            params: Parameter dictionary to normalize

        Returns:
            Normalized parameter dictionary
        """
        normalized = {}
        for key, value in params.items():
            # Treat empty dict as None for consistency
            if isinstance(value, dict) and len(value) == 0:
                normalized[key] = None
            elif isinstance(value, dict):
                # Recursively normalize nested dicts
                normalized[key] = self._normalize_optional_models(value)
            else:
                normalized[key] = value
        return normalized

    def _has_required_structure(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Check if actual has the basic required structure."""

        def check_structure(exp_item: Any, act_item: Any) -> bool:
            if isinstance(exp_item, dict) and isinstance(act_item, dict):
                for key in exp_item:
                    if key not in act_item:
                        return False
                    if not check_structure(exp_item[key], act_item[key]):
                        return False
                return True
            if isinstance(exp_item, list) and isinstance(act_item, list):
                return True  # Allow flexibility in list contents
            return True  # Allow value differences for leaf nodes

        return check_structure(expected, actual)

    def _is_alert_grouping_tool_call(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Check if this is an Alert Grouping Settings tool call."""
        # Look for alert grouping setting creation/update patterns
        create_model = expected.get("create_model") or actual.get("create_model")
        update_model = expected.get("update_model") or actual.get("update_model")

        return (create_model and "alert_grouping_setting" in create_model) or (
            update_model and "alert_grouping_setting" in update_model
        )

    def _validate_alert_grouping_params(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Specialized validation for Alert Grouping Settings parameters."""
        # Extract alert grouping setting from expected and actual
        exp_setting = self._extract_alert_grouping_setting(expected)
        act_setting = self._extract_alert_grouping_setting(actual)

        if not exp_setting or not act_setting:
            return False

        # Validate core requirements
        if not self._validate_core_alert_grouping_fields(exp_setting, act_setting):
            return False

        # Validate type-specific configuration
        return self._validate_alert_grouping_config(exp_setting, act_setting)

    def _extract_alert_grouping_setting(self, params: dict[str, Any]) -> dict[str, Any] | None:
        """Extract alert grouping setting from parameters."""
        for model_key in ["create_model", "update_model"]:
            if model_key in params and "alert_grouping_setting" in params[model_key]:
                return params[model_key]["alert_grouping_setting"]
        return None

    def _validate_core_alert_grouping_fields(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate core Alert Grouping Settings fields."""
        # Type must match exactly
        if expected.get("type") != actual.get("type"):
            return False

        # Services must be present and have valid IDs
        exp_services = expected.get("services", [])
        act_services = actual.get("services", [])

        if not exp_services or not act_services:
            return False

        # Check that service IDs are present (allow additional fields like summary)
        exp_service_ids = {s.get("id") for s in exp_services if s.get("id")}
        act_service_ids = {s.get("id") for s in act_services if s.get("id")}

        return exp_service_ids == act_service_ids

    def _validate_alert_grouping_config(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate Alert Grouping Settings configuration with flexible value acceptance."""
        exp_config = expected.get("config", {})
        act_config = actual.get("config", {})

        setting_type = expected.get("type")

        if setting_type == "content_based":
            return self._validate_content_based_config(exp_config, act_config)
        if setting_type == "content_based_intelligent":
            return self._validate_content_based_intelligent_config(exp_config, act_config)
        if setting_type == "time":
            return self._validate_time_config(exp_config, act_config)
        if setting_type == "intelligent":
            return self._validate_intelligent_config(exp_config, act_config)

        return False

    def _validate_content_based_config(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate content-based configuration with flexible values."""
        # Aggregate must be valid (allow any valid choice)
        act_aggregate = actual.get("aggregate")
        if act_aggregate not in ["all", "any"]:
            return False

        # Fields must be present and non-empty
        act_fields = actual.get("fields", [])
        if not act_fields or not isinstance(act_fields, list):
            return False

        # Time window must be valid (allow any valid value, including 0 for recommended)
        act_time_window = actual.get("time_window")
        return isinstance(act_time_window, int) and act_time_window >= 0

    def _validate_content_based_intelligent_config(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate content-based intelligent configuration."""
        return self._validate_content_based_config(expected, actual)  # Same validation rules

    def _validate_time_config(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate time-based configuration."""
        act_timeout = actual.get("timeout")
        return isinstance(act_timeout, int) and act_timeout >= 0

    def _validate_intelligent_config(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate intelligent configuration with flexible values."""
        # Time window must be valid
        act_time_window = actual.get("time_window")
        if not isinstance(act_time_window, int) or act_time_window < 0:
            return False

        # iag_fields is optional but if present, must be valid
        act_iag_fields = actual.get("iag_fields")
        return act_iag_fields is None or (isinstance(act_iag_fields, list) and act_iag_fields)
