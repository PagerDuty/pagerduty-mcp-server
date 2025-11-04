"""Shared context management for all PagerDuty MCP servers."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

from pagerduty_mcp.models import MCPContext
from .client import get_client
from .utils import get_mcp_context as get_context_from_client


def get_mcp_context(client) -> MCPContext:
    """
    Create MCP context with user information.

    Args:
        client: PagerDuty API client

    Returns:
        MCPContext with current user information
    """
    return get_context_from_client(client)


@asynccontextmanager
async def create_server_lifespan(server: FastMCP) -> AsyncIterator[MCPContext]:
    """
    Lifespan context manager for PagerDuty MCP servers.

    This is used by all servers to initialize the PagerDuty client
    and provide context to all tool invocations.

    Args:
        server: FastMCP server instance

    Yields:
        MCPContext with user information

    Example:
        >>> mcp = FastMCP(
        ...     "Server Name",
        ...     lifespan=create_server_lifespan
        ... )
    """
    try:
        yield get_mcp_context(client=get_client())
    finally:
        pass
