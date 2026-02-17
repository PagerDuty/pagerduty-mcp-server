
from typing import Optional
from abc import ABC, abstractmethod

from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.models.users import User


class ContextStrategy(ABC):
    """Abstract base class for context management strategies."""

    @abstractmethod
    def get_context(self) -> MCPContext:
        """Get the current context."""
        pass

    def get_client(self) -> RestApiV2Client:
        """Get the PagerDuty client from the current context."""
        client = self.get_context().client
        if not client:
            raise RuntimeError("A client is required to call the PagerDuty API.")
        return client

    def get_user(self) -> Optional[User]:
        """Get the user from the current context."""
        return self.get_context().user