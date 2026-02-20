"""Base class for agent competency tests."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from openai import BaseModel


@dataclass
class MockMCPToolInvokationResponse:
    tool_name: str
    parameters: dict[str, Any] | Callable
    response: Any


class MockToolCall(BaseModel):
    name: str
    parameters: dict[str, Any] | None = None
    message_intent: str | None = None


class AgentCompetencyTest:
    """A base class for agent competency tests.

    This class helps define and verify that the correct agents are called
    with semantically correct messages.
    """

    def __init__(
        self,
        query: str,
        expected_tool_calls: list[MockToolCall],
        description: str | None = None,
        max_conversation_turns: int = 5,
        model: str = "gpt-4o",
        mock_responses: list[MockMCPToolInvokationResponse] | None = None,
    ):
        """Initialize an agent competency test case.

        Args:
            query: The user query to test
            expected_tool_calls: Expected tool calls with message intents
                Example: [{"name": "sre_agent_tool", "message_intent": "Check SRE status"}]
            description: Optional description of the test case
            max_conversation_turns: Maximum number of conversation turns allowed
            model: The model to use for the test (default: "gpt-4o")
            mock_responses: Optional list of mock responses for tool calls
        """
        self.query = query
        self.expected_tool_calls = expected_tool_calls
        self.description = description or query
        self.max_conversation_turns = max_conversation_turns
        self.model = model
        self.mock_responses = mock_responses or []
