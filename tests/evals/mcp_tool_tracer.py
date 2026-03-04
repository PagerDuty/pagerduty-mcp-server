"""MCP tool call recorder and mock response server."""

from typing import Any

from pagerduty_mcp_evals.test_cases.agent_competency_test import MockMCPToolInvocationResponse


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
