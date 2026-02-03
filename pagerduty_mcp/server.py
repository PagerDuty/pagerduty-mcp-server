import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import typer
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import MCPContext
from pagerduty_mcp.tools import read_tools, write_tools
from pagerduty_mcp.utils import get_mcp_context

logging.basicConfig(level=logging.WARNING)


app = typer.Typer()

MCP_SERVER_INSTRUCTIONS = """
When the user asks for information about their resources, first get the user data and scope any
requests using the user id.

READ operations are safe to use, but be cautious with WRITE operations as they can modify the
live environment. Always confirm with the user before using any tool marked as destructive.
"""


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[MCPContext]:
    """Lifespan context manager for the MCP server.

    Args:
        server: The MCP server instance
    Returns:
        An asynchronous iterator yielding the MCP context.
    """
    try:
        yield get_mcp_context(client=get_client())
    finally:
        pass


def add_read_only_tool(mcp_instance: FastMCP, tool: Callable) -> None:
    """Add a read-only tool with appropriate safety annotations.

    Args:
        mcp_instance: The MCP server instance
        tool: The tool function to add
    """
    mcp_instance.add_tool(
        tool,
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True),
    )


def add_write_tool(mcp_instance: FastMCP, tool: Callable) -> None:
    """Add a write tool with appropriate safety annotations that indicate it's dangerous.

    Args:
        mcp_instance: The MCP server instance
        tool: The tool function to add
    """
    mcp_instance.add_tool(
        tool,
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False),
    )


@app.command()
def run(
    *,
    enable_write_tools: bool = False,
    transport: str = typer.Option(
        "stdio",
        help="Transport protocol: stdio, sse, or streamable-http",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        help="Host for HTTP server (sse/streamable-http only)",
    ),
    port: int = typer.Option(
        8000,
        help="Port for HTTP server (sse/streamable-http only)",
    ),
) -> None:
    """Run the MCP server with the specified configuration.

    Args:
        enable_write_tools: Flag to enable write tools
        transport: Transport protocol (stdio, sse, or streamable-http)
        host: Host for HTTP server
        port: Port for HTTP server
    """
    mcp = FastMCP(
        "PagerDuty MCP Server",
        lifespan=app_lifespan,
        instructions=MCP_SERVER_INSTRUCTIONS,
        host=host,
        port=port,
    )
    for tool in read_tools:
        add_read_only_tool(mcp, tool)

    if enable_write_tools:
        for tool in write_tools:
            add_write_tool(mcp, tool)

    mcp.run(transport=transport)
