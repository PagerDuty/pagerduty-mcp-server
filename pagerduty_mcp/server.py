import ipaddress
import logging
from collections.abc import Callable
from enum import Enum

import typer
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

from pagerduty_mcp.context import ContextResolver
from pagerduty_mcp.context.application_context_strategy import ApplicationContextStrategy
from pagerduty_mcp.tools import read_tools, write_tools


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
    transport: Transport = typer.Option(default=Transport.stdio, help="Transport protocol to use (stdio, sse, or streamable-http)"),
    host: str = typer.Option(default="127.0.0.1", envvar="MCP_HOST", help="Host to bind to for HTTP-based transports"),
    port: int = typer.Option(default=8000, envvar="MCP_PORT", help="Port to bind to for HTTP-based transports"),
) -> None:
    """Run the MCP server with the specified configuration.

    Args:
        enable_write_tools: Flag to enable write tools
        transport: Transport protocol to use (stdio, sse, or streamable-http)
        host: Host to bind to for HTTP-based transports (env: MCP_HOST)
        port: Port to bind to for HTTP-based transports (env: MCP_PORT)
    """
    ContextResolver.set_strategy(ApplicationContextStrategy())

    fastmcp_kwargs: dict = {"instructions": MCP_SERVER_INSTRUCTIONS}

    if transport == Transport.stdio:
        _http_env_vars = {k: v for k, v in {"MCP_HOST": host, "MCP_PORT": str(port)}.items()
                         if v not in ("127.0.0.1", "8000")}
        if _http_env_vars:
            logging.getLogger(__name__).warning(
                "Environment variable(s) %s have no effect when --transport stdio is used.",
                ", ".join(_http_env_vars),
            )
    else:
        if not (1 <= port <= 65535):
            raise typer.BadParameter(f"Port must be between 1 and 65535, got {port}", param_hint="--port")

        if port < 1024:
            logging.getLogger(__name__).warning(
                "Port %d is a privileged port — binding may fail on non-root processes.", port
            )

        if any(c in host for c in ("\n", "\r", "\x00")):
            raise typer.BadParameter("Host must not contain control characters", param_hint="--host")

        normalized_host = host.strip()
        try:
            is_loopback = ipaddress.ip_address(normalized_host).is_loopback
        except ValueError:
            is_loopback = normalized_host.lower() == "localhost"

        if not is_loopback:
            logging.getLogger(__name__).warning(
                "HTTP transport '%s' bound to '%s' with no built-in authentication — "
                "ensure this endpoint is protected by an authenticating proxy.",
                transport.value,
                normalized_host,
            )

        fastmcp_kwargs["host"] = normalized_host
        fastmcp_kwargs["port"] = port
        fastmcp_kwargs["transport_security"] = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[f"{normalized_host}:{port}", "localhost"],
        )

    mcp = FastMCP("PagerDuty MCP Server", **fastmcp_kwargs)
    for tool in read_tools:
        add_read_only_tool(mcp, tool)

    if enable_write_tools:
        for tool in write_tools:
            add_write_tool(mcp, tool)

    mcp.run(transport=transport.value)
