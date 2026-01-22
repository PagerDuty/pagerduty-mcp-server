"""Bedrock client implementation for evaluation testing."""

import json
import os
import time
import uuid
from typing import Any
from urllib.parse import unquote

import boto3
import httpx
from botocore.exceptions import ClientError, NoCredentialsError

from .base import ChatResponse, LLMClient, ToolCall


class BedrockClient(LLMClient):
    """Bedrock client implementation supporting both bearer token and boto3 SDK."""

    def __init__(
        self,
        region_name: str = "us-west-2",
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        **kwargs: Any,
    ):
        """Initialize the Bedrock client.

        Args:
            region_name: AWS region for Bedrock service
            max_retries: Maximum number of retry attempts for throttled requests (default: 3)
            initial_retry_delay: Initial delay in seconds for exponential backoff (default: 1.0)
            max_retry_delay: Maximum delay in seconds for exponential backoff (default: 60.0)
            **kwargs: Additional boto3 session parameters

        Raises:
            NoCredentialsError: If AWS credentials are not available
            ClientError: If Bedrock service is not available in the region
        """
        self.region_name = region_name
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay

        # Check for bearer token first
        bearer_token = os.environ.get('AWS_BEARER_TOKEN_BEDROCK', '')

        if bearer_token:
            print(f"[DEBUG] Using bearer token authentication from AWS_BEARER_TOKEN_BEDROCK")
            self.use_bearer_token = True
            # Extract URL from bearer token (format: "bedrock-api-key-{base64_url}")
            if bearer_token.startswith('bedrock-api-key-'):
                import base64
                encoded_url = bearer_token.replace('bedrock-api-key-', '')
                decoded_url = base64.b64decode(encoded_url).decode('utf-8')
                # Add https:// if not present
                self.bearer_url = decoded_url if decoded_url.startswith('http') else f'https://{decoded_url}'
                print(f"[DEBUG] Bearer URL endpoint: {self.bearer_url[:60]}...")
            else:
                self.bearer_url = bearer_token if bearer_token.startswith('http') else f'https://{bearer_token}'
            self.client = None
        else:
            print(f"[DEBUG] Using boto3 IAM authentication")
            self.use_bearer_token = False
            self.bearer_url = None

            try:
                # Debug: Check credentials before creating client
                print(f"[DEBUG] AWS_PROFILE env var: {os.environ.get('AWS_PROFILE', 'NOT SET')}")
                print(f"[DEBUG] Creating client for region: {region_name}")

                self.client = boto3.client("bedrock-runtime", region_name=region_name, **kwargs)

                # Debug: Verify credentials using same region
                sts = boto3.client('sts', region_name=region_name)
                identity = sts.get_caller_identity()
                print(f"[DEBUG] Authenticated as: {identity['Arn']}")
                print(f"[DEBUG] Account ID: {identity['Account']}")

                # Check the actual credentials being used
                session = boto3.Session()
                credentials = session.get_credentials()
                print(f"[DEBUG] Credentials type: {type(credentials).__name__}")
                print(f"[DEBUG] Access Key ID (first 10 chars): {credentials.access_key[:10] if credentials.access_key else 'None'}")

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
        # Use bearer token authentication if available
        if self.use_bearer_token:
            return self._chat_completion_with_bearer_token(
                messages, model, tools, tool_choice, max_tokens, temperature, **kwargs
            )

        # Otherwise use boto3
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

        # Implement retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                # Debug logging
                print(f"[DEBUG] Invoking Bedrock model: {model}")
                print(f"[DEBUG] Region: {self.region_name}")

                # Make the API call to Bedrock
                response = self.client.converse(modelId=model, **request_payload)

                # Convert response back to our standard format
                return self._convert_response_from_bedrock(response)

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")
                error_message = e.response.get("Error", {}).get("Message", str(e))
                print(f"[DEBUG] Boto3 ClientError - Code: {error_code}, Message: {error_message}")
                print(f"[DEBUG] Full error response: {e.response}")
                last_exception = e

                # Check if this is a throttling error
                if error_code in ["ThrottlingException", "TooManyRequestsException"]:
                    if attempt < self.max_retries:
                        # Calculate exponential backoff delay
                        delay = min(
                            self.initial_retry_delay * (2**attempt),
                            self.max_retry_delay,
                        )
                        print(
                            f"Bedrock throttled request (attempt {attempt + 1}/{self.max_retries + 1}). "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        time.sleep(delay)
                        continue
                    # Max retries exhausted
                    print(f"Bedrock throttled request after {self.max_retries + 1} attempts. Giving up.")
                    raise Exception(f"Bedrock API error ({error_code}): {error_message}") from e

                # Not a throttling error, raise immediately
                raise Exception(f"Bedrock API error ({error_code}): {error_message}") from e

        # Should never reach here, but just in case
        if last_exception:
            error_code = last_exception.response.get("Error", {}).get("Code", "Unknown")
            error_message = last_exception.response.get("Error", {}).get("Message", str(last_exception))
            raise Exception(f"Bedrock API error ({error_code}): {error_message}") from last_exception
        raise Exception("Bedrock API call failed after retries")

    def _chat_completion_with_bearer_token(
        self,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "auto",
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send chat completion using bearer token authentication."""
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

        request_payload.update(kwargs)

        # Implement retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                print(f"[DEBUG] Making HTTP POST to bearer URL with model: {model}")

                # Make HTTP request to pre-signed bearer URL
                # The bearer URL already contains authentication, just POST the converse request
                with httpx.Client(timeout=120.0) as http_client:
                    response = http_client.post(
                        self.bearer_url,
                        json={"modelId": model, **request_payload},
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                        },
                    )

                    if response.status_code == 200:
                        bedrock_response = response.json()
                        return self._convert_response_from_bedrock(bedrock_response)
                    else:
                        error_data = response.json() if response.text else {}
                        error_message = error_data.get("message", response.text)
                        raise Exception(f"Bedrock HTTP error ({response.status_code}): {error_message}")

            except httpx.HTTPStatusError as e:
                error_message = str(e)
                last_exception = e

                # Check for throttling (429 status)
                if e.response.status_code == 429:
                    if attempt < self.max_retries:
                        delay = min(self.initial_retry_delay * (2**attempt), self.max_retry_delay)
                        print(f"Throttled (attempt {attempt + 1}/{self.max_retries + 1}). Retrying in {delay:.2f}s...")
                        time.sleep(delay)
                        continue
                    raise Exception(f"Bedrock throttled after {self.max_retries + 1} attempts") from e

                raise Exception(f"Bedrock HTTP error: {error_message}") from e

            except Exception as e:
                raise Exception(f"Bedrock request failed: {str(e)}") from e

        if last_exception:
            raise Exception(f"Bedrock API call failed after retries: {last_exception}") from last_exception
        raise Exception("Bedrock API call failed")

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
