import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import typer
from mcp.server.fastmcp import FastMCP
from mcp.types import Prompt, ToolAnnotations

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import MCPContext
from pagerduty_mcp.prompts import prompts
from pagerduty_mcp.tools import read_tools, write_tools
from pagerduty_mcp.utils import get_mcp_context

logging.basicConfig(level=logging.WARNING)


app = typer.Typer()

MCP_SERVER_INSTRUCTIONS = """
CRITICAL: Always read and follow the available prompts BEFORE executing any tools.
Use the available prompts to understand the proper context and approach for each task.

Workflow:
1. FIRST: Check available prompts for guidance on the user's request
2. THEN: Get user data and scope any requests using the user id
3. FINALLY: Execute appropriate tools based on prompt guidance

When the user asks for information about their resources, first get the user data and scope any
requests using the user id.

READ operations are safe to use, but be cautious with WRITE operations as they can modify the
live environment. Always confirm with the user before using any tool marked as destructive.

Available prompts contain essential context and examples - always consult them first.
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
        annotations=ToolAnnotations(
            readOnlyHint=True, destructiveHint=False, idempotentHint=True
        ),
    )


def add_write_tool(mcp_instance: FastMCP, tool: Callable) -> None:
    """Add a write tool with appropriate safety annotations that indicate it's dangerous.

    Args:
        mcp_instance: The MCP server instance
        tool: The tool function to add
    """
    mcp_instance.add_tool(
        tool,
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=True, idempotentHint=False
        ),
    )


def add_prompt(mcp_instance: FastMCP, prompt: Prompt) -> None:
    """Add a prompt to the MCP instance.

    Args:
        mcp_instance: The MCP server instance
        prompt: The prompt to add
    """
    mcp_instance.add_prompt(prompt)  # type: ignore


@app.command()
def run(*, enable_write_tools: bool = False) -> None:
    """Run the MCP server with the specified configuration.

    Args:
        enable_write_tools: Flag to enable write tools
    """
    mcp = FastMCP(
        "PagerDuty MCP Server",
        lifespan=app_lifespan,
        instructions=MCP_SERVER_INSTRUCTIONS,
    )
    for tool in read_tools:
        add_read_only_tool(mcp, tool)

    if enable_write_tools:
        for tool in write_tools:
            add_write_tool(mcp, tool)

    # Add all prompts
    for prompt in prompts:
        add_prompt(mcp, prompt)

    mcp.run()
