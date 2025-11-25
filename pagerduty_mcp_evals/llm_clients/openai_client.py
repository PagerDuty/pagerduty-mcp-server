"""OpenAI client implementation for evaluation testing."""

import os
from typing import Any

from openai import OpenAI

from .base import ChatResponse, LLMClient, ToolCall


class OpenAIClient(LLMClient):
    """OpenAI client implementation using the OpenAI SDK."""

    def __init__(self, api_key: str | None = None):
        """Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable.

        Raises:
            ValueError: If no API key is provided or found in environment
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter is required")

        self.client = OpenAI(api_key=api_key)

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
        """Send a chat completion request to OpenAI.

        Args:
            messages: OpenAI-formatted conversation messages
            model: OpenAI model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
            tools: Available tools for function calling
            tool_choice: Tool selection strategy
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional OpenAI parameters

        Returns:
            Standardized ChatResponse object
        """
        # Build request parameters
        request_params = {
            "model": model,
            "messages": messages,
            **kwargs,
        }

        # Add optional parameters if provided
        if tools is not None:
            request_params["tools"] = tools
            request_params["tool_choice"] = tool_choice

        if max_tokens is not None:
            request_params["max_tokens"] = max_tokens

        if temperature is not None:
            request_params["temperature"] = temperature

        # Make the API call
        response = self.client.chat.completions.create(**request_params)

        # Extract response data
        message = response.choices[0].message
        content = message.content
        tool_calls = []

        # Convert OpenAI tool calls to our standard format
        if message.tool_calls:
            for tool_call in message.tool_calls:
                import json

                tool_calls.append(
                    ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments),
                    )
                )

        # Extract usage information if available
        usage = None
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return ChatResponse(
            content=content,
            tool_calls=tool_calls,
            stop_reason=response.choices[0].finish_reason,
            usage=usage,
        )

    def supports_model(self, model: str) -> bool:
        """Check if this is an OpenAI model.

        Args:
            model: Model identifier to check

        Returns:
            True if the model appears to be an OpenAI model
        """
        # OpenAI model patterns
        openai_patterns = ["gpt-", "text-", "davinci", "curie", "babbage", "ada"]
        model_lower = model.lower()

        return any(pattern in model_lower for pattern in openai_patterns)
