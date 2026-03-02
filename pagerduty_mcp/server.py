import logging
from collections.abc import Callable

import typer
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from pagerduty_mcp.context import ContextResolver
from pagerduty_mcp.context.application_context_strategy import ApplicationContextStrategy
from pagerduty_mcp.tools import TOOL_CATEGORIES, VALID_CATEGORIES

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


def _parse_disabled_categories(raw: str | None) -> set[str]:
    """Parse and validate the comma-separated disabled categories string.

    Args:
        raw: Comma-separated category names, or None.

    Returns:
        A set of validated category names to disable.

    Raises:
        typer.BadParameter: If any category name is invalid.
    """
    if not raw:
        return set()

    categories = {c.strip() for c in raw.split(",") if c.strip()}
    invalid = categories - VALID_CATEGORIES
    if invalid:
        sorted_valid = ", ".join(sorted(VALID_CATEGORIES))
        sorted_invalid = ", ".join(sorted(invalid))
        raise typer.BadParameter(
            f"Invalid tool categories: {sorted_invalid}. Valid categories are: {sorted_valid}"
        )
    return categories


@app.command()
def run(
    *,
    enable_write_tools: bool = False,
    disabled_tool_categories: str | None = typer.Option(
        None,
        "--disabled-tool-categories",
        help=(
            "Comma-separated list of tool categories to disable. "
            f"Valid categories: {', '.join(sorted(VALID_CATEGORIES))}"
        ),
    ),
) -> None:
    """Run the MCP server with the specified configuration.

    Args:
        enable_write_tools: Flag to enable write tools
        disabled_tool_categories: Comma-separated list of tool categories to disable
    """
    disabled = _parse_disabled_categories(disabled_tool_categories)
    ContextResolver.set_strategy(ApplicationContextStrategy())

    mcp = FastMCP(
        "PagerDuty MCP Server",
        instructions=MCP_SERVER_INSTRUCTIONS,
    )

    for category_name, tools in TOOL_CATEGORIES.items():
        if category_name in disabled:
            continue

        for tool in tools["read"]:
            add_read_only_tool(mcp, tool)

        if enable_write_tools:
            for tool in tools["write"]:
                add_write_tool(mcp, tool)

    mcp.run()
