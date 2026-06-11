"""Abstract base classes for LLM client implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    """Represents a tool call made by an LLM."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ChatResponse:
    """Standardized response format for LLM completions."""

    content: str | None
    tool_calls: list[ToolCall]
    stop_reason: str | None = None
    usage: dict[str, Any] | None = None


class LLMClient(ABC):
    """Abstract base class for LLM client implementations.

    This provides a standardized interface for interacting with different
    LLM providers (OpenAI, Bedrock, etc.) in evaluation tests.
    """

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "auto",
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send a chat completion request to the LLM.

        Args:
            messages: List of conversation messages
            model: Model identifier to use
            tools: Available tools for function calling
            tool_choice: Tool selection strategy ("auto", "none", etc.)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            Standardized ChatResponse object

        Raises:
            Exception: If the API call fails
        """

    @abstractmethod
    def supports_model(self, model: str) -> bool:
        """Check if this client supports the given model.

        Args:
            model: Model identifier to check

        Returns:
            True if the model is supported by this client
        """
