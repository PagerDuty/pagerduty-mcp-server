"""Base utilities for creating PagerDuty MCP servers."""

from typing import Callable, List

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .context import create_server_lifespan


def create_pagerduty_server(name: str, instructions: str) -> FastMCP:
    """
    Create a PagerDuty MCP server instance with common configuration.

    All PagerDuty MCP servers use this factory function to ensure
    consistent configuration and behavior.

    Args:
        name: Server name (e.g., "PagerDuty Incidents MCP Server")
        instructions: Server-specific instructions for LLM

    Returns:
        Configured FastMCP server instance

    Example:
        >>> mcp = create_pagerduty_server(
        ...     name="PagerDuty Incidents MCP Server",
        ...     instructions="Instructions for incidents server..."
        ... )
    """
    return FastMCP(
        name=name,
        lifespan=create_server_lifespan,
        instructions=instructions,
    )


def register_read_tools(server: FastMCP, tools: List[Callable]) -> None:
    """
    Register read-only tools with appropriate MCP hints.

    Read tools are marked as:
    - readOnlyHint=True
    - destructiveHint=False
    - idempotentHint=True

    Args:
        server: FastMCP server instance
        tools: List of tool functions to register

    Example:
        >>> READ_TOOLS = [list_incidents, get_incident]
        >>> register_read_tools(mcp, READ_TOOLS)
    """
    for tool in tools:
        server.add_tool(
            tool,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True),
        )


def register_write_tools(server: FastMCP, tools: List[Callable]) -> None:
    """
    Register write tools with appropriate MCP hints.

    Write tools are marked as:
    - readOnlyHint=False
    - destructiveHint=True
    - idempotentHint=False

    Args:
        server: FastMCP server instance
        tools: List of tool functions to register

    Example:
        >>> WRITE_TOOLS = [create_incident, manage_incidents]
        >>> if enable_write_tools:
        ...     register_write_tools(mcp, WRITE_TOOLS)
    """
    for tool in tools:
        server.add_tool(
            tool,
            annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False),
        )
