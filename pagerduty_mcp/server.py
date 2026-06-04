import logging
from collections.abc import Callable
from enum import Enum

import typer
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from pagerduty_mcp.tools import read_tools, write_tools
from pagerduty_mcp.context import ContextResolver
from pagerduty_mcp.context.application_context_strategy import ApplicationContextStrategy


class Transport(str, Enum):
    """MCP transport protocols supported by the server."""

    stdio = "stdio"
    sse = "sse"
    streamable_http = "streamable-http"


logging.basicConfig(level=logging.WARNING)


app = typer.Typer()

MCP_SERVER_INSTRUCTIONS = """
When the user asks for information about their resources, first get the user data and scope any
requests using the user id.

READ operations are safe to use, but be cautious with WRITE operations as they can modify the
live environment. Always confirm with the user before using any tool marked as destructive.
"""


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


mcp = FastMCP(
    "PagerDuty MCP Server",
    instructions=MCP_SERVER_INSTRUCTIONS,
)
for _tool in read_tools:
    add_read_only_tool(mcp, _tool)
for _tool in write_tools:
    add_write_tool(mcp, _tool)


@app.command()
def run(
    *,
    enable_write_tools: bool = False,
    transport: Transport = Transport.stdio,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """Run the MCP server with the specified configuration.

    Args:
        enable_write_tools: Flag to enable write tools
        transport: Transport protocol to use (stdio, sse, or streamable-http)
        host: Host to bind to for HTTP-based transports
        port: Port to bind to for HTTP-based transports
    """
    ContextResolver.set_strategy(ApplicationContextStrategy())

    mcp = FastMCP(
        "PagerDuty MCP Server",
        instructions=MCP_SERVER_INSTRUCTIONS,
        host=host,
        port=port,
    )
    for tool in read_tools:
        add_read_only_tool(mcp, tool)

    if enable_write_tools:
        for tool in write_tools:
            add_write_tool(mcp, tool)

    mcp.run(transport=transport.value)
