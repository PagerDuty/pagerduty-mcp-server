import json
import logging
import pathlib
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import datetime

import typer
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations, TextContent

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import MCPContext
from pagerduty_mcp.tools import read_tools, write_tools
from pagerduty_mcp.utils import get_mcp_context

logging.basicConfig(level=logging.WARNING)


app = typer.Typer()

# MCP App URIs
SERVICE_HEALTH_MATRIX_VIEW_URI = "ui://service-health-matrix/grid.html"
INCIDENT_COMMAND_CENTER_URI = "ui://incident-command-center/dashboard.html"
ONCALL_SCHEDULE_VISUALIZER_URI = "ui://oncall-schedule-visualizer/calendar.html"

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


def add_service_health_matrix(mcp_instance: FastMCP) -> None:
    """Add Service Health Matrix MCP App tool and resource.

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": SERVICE_HEALTH_MATRIX_VIEW_URI},
            "ui/resourceUri": SERVICE_HEALTH_MATRIX_VIEW_URI,  # legacy support
        }
    )
    def service_health_matrix() -> list[TextContent]:
        """PagerDuty Health Check Matrix - Comprehensive health check analysis organized by object type.

        The UI will call list_services, list_users, list_teams, list_escalation_policies,
        list_schedules, and list_incidents tools to fetch real data.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Health Check Matrix UI initialized. Fetching data from PagerDuty..."
            )
        ]

    @mcp_instance.resource(
        SERVICE_HEALTH_MATRIX_VIEW_URI,
        mime_type="text/html",
        description="Service Health Matrix interactive UI"
    )
    def service_health_matrix_view() -> str:
        """Service Health Matrix UI resource."""
        html_path = pathlib.Path(__file__).parent / "service_health_matrix_view.html"
        return html_path.read_text(encoding="utf-8")


def add_incident_command_center(mcp_instance: FastMCP) -> None:
    """Add Incident Command Center MCP App resource.

    The UI directly calls existing MCP tools:
    - list_incidents, get_incident, list_incident_notes
    - list_alerts_from_incident, list_incident_change_events
    - manage_incidents, add_note_to_incident
    - get_past_incidents, get_related_incidents
    - list_escalation_policies

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": INCIDENT_COMMAND_CENTER_URI},
            "ui/resourceUri": INCIDENT_COMMAND_CENTER_URI,
        }
    )
    def incident_command_center() -> list[TextContent]:
        """Incident Command Center - Interactive incident management dashboard.

        Full incident lifecycle management from your IDE. The UI calls existing
        MCP tools (list_incidents, manage_incidents, etc.) to fetch and manipulate data.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Incident Command Center UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        INCIDENT_COMMAND_CENTER_URI,
        mime_type="text/html",
        description="Incident Command Center - Interactive incident management UI"
    )
    def incident_command_center_view() -> str:
        """Incident Command Center UI resource."""
        html_path = pathlib.Path(__file__).parent / "incident_command_center_view.html"
        return html_path.read_text(encoding="utf-8")


def add_oncall_schedule_visualizer(mcp_instance: FastMCP) -> None:
    """Add On-Call Schedule Visualizer MCP App resource.

    The UI directly calls existing MCP tools:
    - list_schedules, get_schedule
    - list_oncalls, list_schedule_users
    - list_teams, list_users

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": ONCALL_SCHEDULE_VISUALIZER_URI},
            "ui/resourceUri": ONCALL_SCHEDULE_VISUALIZER_URI,
        }
    )
    def oncall_schedule_visualizer() -> list[TextContent]:
        """On-Call Schedule Visualizer - Interactive calendar view.

        Shows who's on-call across teams and schedules. The UI calls existing
        MCP tools (list_schedules, list_oncalls, etc.) to fetch data.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="On-Call Schedule Visualizer UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        ONCALL_SCHEDULE_VISUALIZER_URI,
        mime_type="text/html",
        description="On-Call Schedule Visualizer - Interactive calendar view of on-call schedules"
    )
    def oncall_schedule_visualizer_view() -> str:
        """On-Call Schedule Visualizer UI resource."""
        html_path = pathlib.Path(__file__).parent / "oncall_schedule_visualizer_view.html"
        return html_path.read_text(encoding="utf-8")


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

    # Add MCP Apps
    add_service_health_matrix(mcp)
    add_incident_command_center(mcp)
    add_oncall_schedule_visualizer(mcp)

    mcp.run()
