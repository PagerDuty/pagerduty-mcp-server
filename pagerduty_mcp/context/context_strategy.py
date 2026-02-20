
from typing import Optional
from abc import ABC, abstractmethod

from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.models.users import User


class ContextStrategy(ABC):
    """Abstract base class for context management strategies."""

    context: MCPContext
