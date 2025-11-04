"""Common utilities shared across all PagerDuty MCP servers."""

from .base import (
    create_pagerduty_server,
    register_read_tools,
    register_write_tools,
)
from .client import get_client
from .context import create_server_lifespan, get_mcp_context
from .utils import MAX_RESULTS, paginate

__all__ = [
    # Server creation
    "create_pagerduty_server",
    "register_read_tools",
    "register_write_tools",
    # Client
    "get_client",
    # Context
    "create_server_lifespan",
    "get_mcp_context",
    # Utils
    "MAX_RESULTS",
    "paginate",
]
