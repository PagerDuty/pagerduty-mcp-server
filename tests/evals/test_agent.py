"""Test agent for evaluating LLM MCP tool call competency."""

import asyncio
import json
import logging
from collections.abc import Sequence
from typing import Any

from deepdiff import DeepDiff
from pydantic import BaseModel

from pagerduty_mcp.server import add_read_only_tool, add_write_tool
from pagerduty_mcp.tools import read_tools, write_tools
from mcp.server.fastmcp import FastMCP
from pagerduty_mcp_evals.test_cases.agent_competency_test import AgentCompetencyTest
from tests.evals.llm_clients import BedrockClient, LLMClient, OpenAIClient
from tests.evals.mcp_tool_tracer import MockedMCPServer


class TestResult(BaseModel):
    """Model for test results."""

    query: str
    description: str
    expected_tools: list[dict[str, Any]]
    actual_tools: list[dict[str, Any]]
    success: bool
    gpt_response: str | None = None
    error: str | None = None


class TestReport(BaseModel):
    """Model for the test report."""

    llm_type: str
    total_tests: int
    successful_tests: int
    success_rate: float
    results: list[TestResult]


class TestAgent:
    """Agent for testing LLM competency with MCP tools.

    This agent submits competency questions to an LLM and
    verifies that the correct MCP tools are called with
    the right parameters.
    """

    def __init__(
        self,
        llm_type: str = "gpt",
        aws_region: str = "us-west-2",
        delay_between_tests: float = 0.0,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
    ):
        """Initialize the test agent.

        Args:
            llm_type: The type of LLM to test ("gpt", "bedrock")
            aws_region: AWS region for Bedrock (only used when llm_type="bedrock")
            delay_between_tests: Delay in seconds between test executions (default: 0.0)
            max_retries: Maximum retry attempts for throttled requests (default: 3)
            initial_retry_delay: Initial delay for exponential backoff in seconds (default: 1.0)
        """
        self.llm_type = llm_type
        self.aws_region = aws_region
        self.delay_between_tests = delay_between_tests
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.results = []
        self.mocked_mcp = MockedMCPServer()
        self.llm: LLMClient = self._initialize_llm(llm_type, aws_region, max_retries, initial_retry_delay)

    def _initialize_llm(
        self, llm_type: str, aws_region: str, max_retries: int, initial_retry_delay: float
    ) -> LLMClient:
        """Initialize the specified LLM client.

        Args:
            llm_type: The type of LLM to initialize
            aws_region: AWS region for Bedrock
            max_retries: Maximum retry attempts for throttled requests
            initial_retry_delay: Initial delay for exponential backoff

        Returns:
            Initialized LLM client
        """
        if llm_type == "gpt":
            return OpenAIClient()
        if llm_type == "bedrock":
            return BedrockClient(
                region_name=aws_region,
                max_retries=max_retries,
                initial_retry_delay=initial_retry_delay,
            )
        raise ValueError(f"LLM type {llm_type} is not supported. Choose from: gpt, bedrock")

    def _get_available_tools(self) -> list[dict[str, Any]]:
        """Get tool schemas directly from MCP server (like dbt-labs approach)."""
        # Create temp MCP server with same setup as real server
        temp_mcp = FastMCP("test-server")

        for tool in read_tools:
            add_read_only_tool(temp_mcp, tool)
        for tool in write_tools:
            add_write_tool(temp_mcp, tool)

        # Get tools using MCP's built-in schema generation (async)
        async def get_mcp_tools():
            mcp_tools = await temp_mcp.list_tools()
            return [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description or t.name,
                        "parameters": t.inputSchema or {"type": "object", "properties": {}},
                    },
                }
                for t in mcp_tools  # mcp_tools is already a list, not an object with .tools
            ]

        # Run async function in sync context
        return asyncio.run(get_mcp_tools())

    def _execute_tool_call(self, function_name: str, function_args: dict[str, Any]) -> Any:
        """Execute a tool call directly using the MCP client instead of going through OpenAI's function calling.

        Args:
            function_name: The name of the tool to call
            function_args: The arguments to pass to the tool

        Returns:
            The result of the tool call
        """
        print(f"Directly calling MCP tool: {function_name} with args: {function_args}")

        # Execute the tool call through our mock client
        return self.mocked_mcp.invoke_tool(function_name, **function_args)

    def _verify_tool_calls(self, test_case: AgentCompetencyTest, actual_tool_calls: list[dict[str, Any]]) -> bool:
        """Verify that all expected tool calls were made with the correct parameters."""
        calls_by_tool: dict[str, list[dict[str, Any]]] = {}
        for call in actual_tool_calls:
            calls_by_tool.setdefault(call["tool_name"], []).append(call)

        for expected in test_case.expected_tool_calls:
            tool_calls = calls_by_tool.get(expected.name)
            if not tool_calls:
                print(f"Expected tool {expected.name} was not called")
                return False
            # If parameters are specified, verify at least one call matched them
            if expected.parameters is not None:
                if not any(
                    self._params_are_compatible(expected.parameters, call["parameters"]) for call in tool_calls
                ):
                    print(f"Expected tool {expected.name} was not called with the expected parameters")
                    return False
        return True

    def _params_are_compatible(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Check if actual parameters are compatible with expected ones.

        Compatible means:
        1. All expected fields are present with correct values
        2. Additional fields in actual are allowed (flexible)
        3. Nested objects are checked
        4. None and {} are considered equivalent for optional model parameters
        """
        if not self._has_required_structure(expected, actual):
            return False

        # For Alert Grouping Settings, use specialized validation
        if self._is_alert_grouping_tool_call(expected, actual):
            return self._validate_alert_grouping_params(expected, actual)

        # Normalize parameters before comparison (treat None and {} as equivalent)
        normalized_expected = self._normalize_optional_models(expected)
        normalized_actual = self._normalize_optional_models(actual)

        diff = DeepDiff(normalized_expected, normalized_actual, ignore_order=True)

        compatibility_issues = []
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
        """Normalize optional model parameters by treating None and {} as equivalent."""
        normalized = {}
        for key, value in params.items():
            if isinstance(value, dict) and len(value) == 0:
                normalized[key] = None
            elif isinstance(value, dict):
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
        create_model = expected.get("create_model") or actual.get("create_model")
        update_model = expected.get("update_model") or actual.get("update_model")
        return bool(
            (create_model and "alert_grouping_setting" in create_model)
            or (update_model and "alert_grouping_setting" in update_model)
        )

    def _validate_alert_grouping_params(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Specialized validation for Alert Grouping Settings parameters."""
        exp_setting = self._extract_alert_grouping_setting(expected)
        act_setting = self._extract_alert_grouping_setting(actual)
        if not exp_setting or not act_setting:
            return False
        if not self._validate_core_alert_grouping_fields(exp_setting, act_setting):
            return False
        return self._validate_alert_grouping_config(exp_setting, act_setting)

    def _extract_alert_grouping_setting(self, params: dict[str, Any]) -> dict[str, Any] | None:
        """Extract alert grouping setting from parameters."""
        for model_key in ["create_model", "update_model"]:
            if model_key in params and "alert_grouping_setting" in params[model_key]:
                return params[model_key]["alert_grouping_setting"]
        return None

    def _validate_core_alert_grouping_fields(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate core Alert Grouping Settings fields."""
        if expected.get("type") != actual.get("type"):
            return False
        exp_services = expected.get("services", [])
        act_services = actual.get("services", [])
        if not exp_services or not act_services:
            return False
        exp_service_ids = {s.get("id") for s in exp_services if s.get("id")}
        act_service_ids = {s.get("id") for s in act_services if s.get("id")}
        return exp_service_ids == act_service_ids

    def _validate_alert_grouping_config(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate Alert Grouping Settings configuration."""
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
        act_aggregate = actual.get("aggregate")
        if act_aggregate not in ["all", "any"]:
            return False
        act_fields = actual.get("fields", [])
        if not act_fields or not isinstance(act_fields, list):
            return False
        act_time_window = actual.get("time_window")
        return isinstance(act_time_window, int) and act_time_window >= 0

    def _validate_content_based_intelligent_config(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate content-based intelligent configuration."""
        return self._validate_content_based_config(expected, actual)

    def _validate_time_config(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate time-based configuration."""
        act_timeout = actual.get("timeout")
        return isinstance(act_timeout, int) and act_timeout >= 0

    def _validate_intelligent_config(self, expected: dict[str, Any], actual: dict[str, Any]) -> bool:
        """Validate intelligent configuration with flexible values."""
        act_time_window = actual.get("time_window")
        if not isinstance(act_time_window, int) or act_time_window < 0:
            return False
        act_iag_fields = actual.get("iag_fields")
        return act_iag_fields is None or bool(isinstance(act_iag_fields, list) and act_iag_fields)

    def test_competency(self, test_case: AgentCompetencyTest) -> TestResult | None:
        """Test a single competency question.

        Args:
            test_case: The competency test case to run

        Returns:
            TestResult object with query, expected tools, actual tools, and success
        """
        # Reset the tool tracer for this test, loading mock responses from the test case
        self.mocked_mcp = MockedMCPServer(mock_responses=test_case.mock_responses)

        try:
            query = test_case.query
            print("-" * 40)
            print(f"Testing query: {query}")

            # Make actual call to LLM with function calling
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a PagerDuty assistant. Use the available tools to help users "
                        "with incident management tasks. Call the appropriate functions based on user requests."
                    ),
                },
                {"role": "user", "content": query},
            ]

            conversation_turns = 0
            response = None
            while conversation_turns < test_case.max_conversation_turns:
                response = self.llm.chat_completion(
                    model=test_case.model,
                    messages=messages,
                    tools=self._get_available_tools(),
                    tool_choice="auto",
                )

                # Process the function calls the LLM wants to make
                if response.tool_calls:
                    tool_called = False
                    for tool_call in response.tool_calls:
                        function_name = tool_call.name
                        function_args = tool_call.arguments

                        print(f"LLM called: {function_name} with args: {function_args}")

                        # Execute the tool call directly using our MCP client
                        result = self._execute_tool_call(function_name, function_args)
                        print(f"Tool result: {result}")

                        # Add the tool call and its result to the conversation
                        assistant_msg = {
                            "role": "assistant",
                            "content": response.content,
                            "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {"name": function_name, "arguments": json.dumps(function_args)},
                                }
                            ],
                        }
                        messages.append(assistant_msg)
                        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
                        tool_called = True

                    if tool_called:
                        conversation_turns += 1
                        continue
                break

            # Verify the tool calls
            success = self._verify_tool_calls(test_case, self.mocked_mcp.tool_calls)

            # Convert expected_tool_calls to dict format for the result
            expected_tools = [
                {"tool_name": tc.name, "parameters": tc.parameters or {}}
                for tc in test_case.expected_tool_calls
            ]

            if response:
                return TestResult(
                    query=query,
                    description=test_case.description,
                    expected_tools=expected_tools,
                    actual_tools=self.mocked_mcp.tool_calls,
                    success=success,
                    gpt_response=response.content or "No text response",
                )

        except Exception as e:  # noqa: BLE001
            print(f"Error during test: {e!s}")
            expected_tools = [
                {"tool_name": tc.name, "parameters": tc.parameters or {}}
                for tc in test_case.expected_tool_calls
            ]

            return TestResult(
                query=test_case.query,
                description=test_case.description,
                expected_tools=expected_tools,
                actual_tools=self.mocked_mcp.tool_calls,
                success=False,
                error=str(e),
            )

    def run_tests(self, test_cases: Sequence[AgentCompetencyTest]) -> list[TestResult]:
        """Run all specified competency tests.

        Args:
            test_cases: List of test cases to run

        Returns:
            List of test results
        """
        import time

        results = []
        for i, test_case in enumerate(test_cases):
            result = self.test_competency(test_case)
            if result:
                results.append(result)

            # Add delay between tests if configured (except after last test)
            if self.delay_between_tests > 0 and i < len(test_cases) - 1:
                print(f"Waiting {self.delay_between_tests:.2f} seconds before next test...")
                time.sleep(self.delay_between_tests)

        self.results = results
        return results

    def generate_report(self, output_file: str | None = None) -> None:
        """Generate a report of test results.

        Args:
            output_file: Optional file path to write the report to
        """
        if not self.results:
            print("No test results available. Run tests first.")
            return

        total = len(self.results)
        successful = sum(r.success for r in self.results)

        report = TestReport(
            llm_type=self.llm_type,
            total_tests=total,
            successful_tests=successful,
            success_rate=successful / total if total > 0 else 0,
            results=self.results,
        )

        # Print summary
        print(f"LLM: {self.llm_type}")
        print(f"Tests: {successful}/{total} ({report.success_rate:.2%})")

        # Save report if requested
        if output_file:
            with open(output_file, "w") as f:
                f.write(report.model_dump_json(indent=2))
            print(f"Report saved to {output_file}")
