"""Bedrock client implementation for evaluation testing."""

import json
import time
import uuid
from typing import Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .base import ChatResponse, LLMClient, ToolCall


class BedrockClient(LLMClient):
    """Bedrock client implementation using the boto3 SDK."""

    def __init__(self, region_name: str = "us-west-2", **kwargs: Any):
        """Initialize the Bedrock client.

        Args:
            region_name: AWS region for Bedrock service
            **kwargs: Additional boto3 session parameters

        Raises:
            NoCredentialsError: If AWS credentials are not available
            ClientError: If Bedrock service is not available in the region
        """
        try:
            self.client = boto3.client("bedrock-runtime", region_name=region_name, **kwargs)
            # Test the connection by listing available models (if permission allows)
            # This is optional as some roles may not have bedrock:ListFoundationModels permission
        except NoCredentialsError as e:
            raise NoCredentialsError(
                "AWS credentials not found. Please configure AWS credentials "
                "via environment variables, AWS credentials file, or IAM role."
            ) from e
        except Exception as e:
            raise ClientError(
                error_response={"Error": {"Code": "ServiceUnavailable", "Message": str(e)}},
                operation_name="bedrock_client_init",
            ) from e

        self.region_name = region_name

    def _retry_with_exponential_backoff(
        self,
        func,
        *args,
        max_retries: int = 5,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        **kwargs,
    ):
        """Retry a function with exponential backoff on ThrottlingException.

        Args:
            func: The function to retry
            *args: Positional arguments to pass to the function
            max_retries: Maximum number of retry attempts (default: 5)
            initial_delay: Initial delay in seconds before first retry (default: 1.0)
            backoff_factor: Multiplier for delay between retries (default: 2.0)
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call

        Raises:
            Exception: If all retries are exhausted or a non-throttling error occurs
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")

                # Only retry on ThrottlingException
                if error_code == "ThrottlingException":
                    last_exception = e

                    if attempt < max_retries:
                        print(
                            f"ThrottlingException encountered (attempt {attempt + 1}/{max_retries + 1}). "
                            f"Retrying in {delay:.1f} seconds..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                        continue

                    # Max retries exhausted
                    print(f"Max retries ({max_retries}) exhausted for ThrottlingException.")
                    error_message = e.response.get("Error", {}).get("Message", str(e))
                    raise Exception(
                        f"Bedrock API error ({error_code}): {error_message} "
                        f"(Failed after {max_retries} retries)"
                    ) from e

                # Non-throttling error - raise immediately
                error_message = e.response.get("Error", {}).get("Message", str(e))
                raise Exception(f"Bedrock API error ({error_code}): {error_message}") from e

        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise Exception("Retry logic failed unexpectedly")

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
        """Send a chat completion request to Bedrock.

        Args:
            messages: OpenAI-formatted conversation messages
            model: Bedrock model identifier (e.g., "anthropic.claude-3-sonnet-20240229-v1:0")
            tools: Available tools for function calling (OpenAI format)
            tool_choice: Tool selection strategy
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional Bedrock parameters

        Returns:
            Standardized ChatResponse object
        """
        # Convert messages to Bedrock format
        bedrock_messages = self._convert_messages_to_bedrock(messages)

        # Build inference configuration
        inference_config = {}
        if max_tokens is not None:
            inference_config["maxTokens"] = max_tokens
        if temperature is not None:
            inference_config["temperature"] = temperature

        # Build request payload
        request_payload = {"messages": bedrock_messages}

        if inference_config:
            request_payload["inferenceConfig"] = inference_config

        # Handle tool configuration if provided
        if tools is not None and len(tools) > 0:
            tool_config = self._convert_tools_to_bedrock(tools, tool_choice)
            request_payload["toolConfig"] = tool_config

        # Add any additional parameters from kwargs
        request_payload.update(kwargs)

        # Wrap the API call with retry logic for ThrottlingException
        def _make_api_call():
            return self.client.converse(modelId=model, **request_payload)

        try:
            # Make the API call to Bedrock with retry logic
            response = self._retry_with_exponential_backoff(_make_api_call)

            # Convert response back to our standard format
            return self._convert_response_from_bedrock(response)

        except Exception:
            # Re-raise exceptions that have already been wrapped by retry logic
            raise

    def supports_model(self, model: str) -> bool:
        """Check if this is a Bedrock model.

        Args:
            model: Model identifier to check

        Returns:
            True if the model appears to be a Bedrock model
        """
        # Bedrock model patterns
        bedrock_patterns = [
            "anthropic.",
            "amazon.",
            "ai21.",
            "cohere.",
            "meta.",
            "mistral.",
            "stability.",
        ]
        model_lower = model.lower()

        return any(pattern in model_lower for pattern in bedrock_patterns)

    def _convert_messages_to_bedrock(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert OpenAI message format to Bedrock Converse format.

        Args:
            messages: List of OpenAI-formatted messages

        Returns:
            List of Bedrock-formatted messages
        """
        bedrock_messages = []

        for message in messages:
            role = message.get("role")
            content = message.get("content")

            # Skip system messages - they should be handled separately in Bedrock
            if role == "system":
                continue

            # Handle tool messages differently
            if role == "tool":
                # Tool response format for Bedrock
                tool_call_id = message.get("tool_call_id")
                tool_content = message.get("content", "")

                bedrock_message = {
                    "role": "user",  # Tool responses come back as user messages in Bedrock
                    "content": [
                        {
                            "toolResult": {
                                "toolUseId": tool_call_id,
                                "content": [{"text": tool_content}],
                            }
                        }
                    ],
                }
                bedrock_messages.append(bedrock_message)
                continue

            # Handle regular user/assistant messages
            if isinstance(content, str):
                # Simple text content
                bedrock_message = {"role": role, "content": [{"text": content}]}
            elif isinstance(content, list):
                # Multi-part content
                bedrock_content = []
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        bedrock_content.append({"text": part["text"]})
                    elif isinstance(part, str):
                        bedrock_content.append({"text": part})

                bedrock_message = {"role": role, "content": bedrock_content}
            else:
                # Fallback for unexpected content format
                bedrock_message = {"role": role, "content": [{"text": str(content)}]}

            # Handle tool calls in assistant messages
            if role == "assistant" and message.get("tool_calls"):
                tool_calls = message["tool_calls"]
                content_parts = bedrock_message.get("content", [])

                for tool_call in tool_calls:
                    tool_use = {
                        "toolUse": {
                            "toolUseId": tool_call.get("id", str(uuid.uuid4())),
                            "name": tool_call["function"]["name"],
                            "input": json.loads(tool_call["function"]["arguments"]),
                        }
                    }
                    content_parts.append(tool_use)

                bedrock_message["content"] = content_parts

            bedrock_messages.append(bedrock_message)

        return bedrock_messages

    def _convert_tools_to_bedrock(self, tools: list[dict[str, Any]], tool_choice: str) -> dict[str, Any]:
        """Convert OpenAI tools format to Bedrock toolConfig format.

        Args:
            tools: List of OpenAI-formatted tool definitions
            tool_choice: Tool selection strategy

        Returns:
            Bedrock toolConfig object
        """
        bedrock_tools = []

        for tool in tools:
            if tool.get("type") == "function":
                function_def = tool.get("function", {})
                bedrock_tool = {
                    "toolSpec": {
                        "name": function_def.get("name"),
                        "description": function_def.get("description", ""),
                        "inputSchema": {"json": function_def.get("parameters", {})},
                    }
                }
                bedrock_tools.append(bedrock_tool)

        tool_config = {"tools": bedrock_tools}

        # Map tool choice to Bedrock format
        if tool_choice == "none":
            # Bedrock doesn't have explicit "none" - just don't include toolChoice
            pass
        elif tool_choice == "auto":
            tool_config["toolChoice"] = {"auto": {}}
        elif isinstance(tool_choice, dict) and "function" in tool_choice:
            # Specific tool choice
            function_name = tool_choice["function"]["name"]
            tool_config["toolChoice"] = {"tool": {"name": function_name}}

        return tool_config

    def _convert_response_from_bedrock(self, response: dict[str, Any]) -> ChatResponse:
        """Convert Bedrock response to our standard format.

        Args:
            response: Raw Bedrock Converse API response

        Returns:
            Standardized ChatResponse object
        """
        output = response.get("output", {})
        message = output.get("message", {})
        content_parts = message.get("content", [])

        # Extract text content and tool calls
        text_content = []
        tool_calls = []

        for part in content_parts:
            if "text" in part:
                text_content.append(part["text"])
            elif "toolUse" in part:
                tool_use = part["toolUse"]
                tool_calls.append(
                    ToolCall(
                        id=tool_use.get("toolUseId", str(uuid.uuid4())),
                        name=tool_use.get("name", ""),
                        arguments=tool_use.get("input", {}),
                    )
                )

        # Combine text content
        combined_text = "\n".join(text_content) if text_content else None

        # Extract usage information
        usage = None
        if "usage" in response:
            usage_data = response["usage"]
            usage = {
                "prompt_tokens": usage_data.get("inputTokens", 0),
                "completion_tokens": usage_data.get("outputTokens", 0),
                "total_tokens": usage_data.get("totalTokens", 0),
            }

        # Extract stop reason
        stop_reason = response.get("stopReason")

        return ChatResponse(
            content=combined_text,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            usage=usage,
        )
