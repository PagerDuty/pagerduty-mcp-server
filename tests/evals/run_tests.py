"""Test agent for evaluating LLM MCP tool call competency."""

import argparse
import asyncio
import json
import logging
import time
from collections.abc import Sequence
from contextlib import suppress
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from pagerduty_mcp.server import add_read_only_tool, add_write_tool
from pagerduty_mcp.tools import read_tools, write_tools
from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
)
from pagerduty_mcp_evals.test_cases.test_cases_builder import TestCasesBuilder
from tests.evals.llm_clients import BedrockClient, LLMClient, OpenAIClient


class MockedMCPServer:
    """Records MCP tool calls and returns configured mock responses."""

    def __init__(self, mock_responses: list[MockMCPToolInvocationResponse] | None = None):
        self.tool_calls: list[dict[str, Any]] = []
        self.current_call_index = 0
        self._mock_responses = mock_responses or []

    def invoke_tool(self, tool_name: str, **parameters) -> Any:
        self.tool_calls.append(
            {"tool_name": tool_name, "parameters": parameters, "call_index": self.current_call_index}
        )
        self.current_call_index += 1
        for mock in self._mock_responses:
            if mock.tool_name != tool_name:
                continue
            matcher = mock.parameters
            if callable(matcher):
                if matcher(parameters):
                    return mock.response
            elif isinstance(matcher, dict):
                if all(k in parameters and parameters[k] == v for k, v in matcher.items()):
                    return mock.response
        return {"status": "success", "message": f"Default mock response for {tool_name}"}


load_dotenv()

logging.getLogger().setLevel(logging.WARNING)


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
        """Verify that all expected tool calls were made."""
        actual_names = {call["tool_name"] for call in actual_tool_calls}
        for expected in test_case.expected_tool_calls:
            if expected.name not in actual_names:
                print(f"Expected tool {expected.name} was not called")
                return False
        return True

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


def main():
    """Main entry point for running the tests."""
    parser = argparse.ArgumentParser(description="Test LLM competency with MCP tools")
    parser.add_argument("--llm", choices=["gpt", "bedrock"], default="gpt", help="LLM provider to use for testing")
    parser.add_argument(
        "--domain",
        choices=[
            "all",
            "alert-grouping-settings",
            "change-events",
            "event-orchestrations",
            "incident-workflows",
            "incidents",
            "log-entries",
            "services",
            "status-pages",
            "teams",
        ],
        default="all",
        help="Domain to test",
    )
    parser.add_argument("--output", type=str, help="Output file for test report")
    parser.add_argument("--model", type=str, default="gpt-4.1", help="LLM model to use for tests")
    parser.add_argument(
        "--aws-region",
        type=str,
        default="us-west-2",
        help="AWS region for Bedrock (only used when --llm=bedrock)",
    )
    parser.add_argument(
        "--delay-between-tests",
        type=float,
        default=0.0,
        help="Delay in seconds between test executions to avoid rate limiting (default: 0.0)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for throttled requests (default: 3)",
    )
    parser.add_argument(
        "--initial-retry-delay",
        type=float,
        default=1.0,
        help="Initial delay in seconds for exponential backoff (default: 1.0)",
    )

    args = parser.parse_args()

    # Select test cases based on domain
    test_cases = TestCasesBuilder().create_test_cases().get(args.domain, [])

    if not test_cases:
        print(f"No test cases available for domain: {args.domain}")
        return

    # Override model on each test case if provided via flag
    for tc in test_cases:
        # Some test case objects may be immutable or restrict attribute setting
        with suppress(AttributeError, TypeError):
            tc.model = args.model

    # Create and run the test agent
    agent = TestAgent(
        llm_type=args.llm,
        aws_region=args.aws_region,
        delay_between_tests=args.delay_between_tests,
        max_retries=args.max_retries,
        initial_retry_delay=args.initial_retry_delay,
    )
    agent.run_tests(test_cases)

    # Generate report
    output_file = args.output or f"test_results_{args.llm}_{args.domain}.json"
    agent.generate_report(output_file)


if __name__ == "__main__":
    main()
