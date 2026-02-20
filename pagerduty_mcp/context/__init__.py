from contextvars import Context
import logging
import os
from typing import Optional

from dotenv import load_dotenv

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.models.users import User
from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty_mcp.context.application_context_strategy import ApplicationContextStrategy
from pagerduty_mcp.context.request_context_strategy import RequestContextStrategy
from pagerduty_mcp.context.context_strategy import ContextStrategy

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextManager:
    """Provides an abstraction for managing the context of the request, like the
    PagerDuty user and the client used to make backend requests.

    This allows the library to be used for both single and multi-tenant applications,
    defaulting to a single-tenant application.

    For a single-tenant application, you should set the PAGERDUTY_USER_API_KEY environment
    variable, and optionally the PAGERDUTY_API_HOST.

    For a multi-tenant application, set MCP_CONTEXT_STRATEGY to "RequestContextStrategy",
    and use `use_context` helper:

        strategy = ContextManager.get_strategy()

        client = ... build your PagerDuty API client ...
        # MCPContext will use this client to pre-populate the user, if available
        context = MCPContext(client=client)

        with strategy.use_context(context):
            ... yield to your request handler here ...
            ... any tools that call ContextManager.get_client() ...
    """

    STRATEGY_REGISTRY = {
        "ApplicationContextStrategy": ApplicationContextStrategy,
        "RequestContextStrategy": RequestContextStrategy,
    }

    _context_strategy: Optional[ContextStrategy] = None

    @staticmethod
    def get_strategy() -> ContextStrategy:
        """Get the current context strategy, initializing it if necessary."""
        strategy_name = os.getenv("MCP_CONTEXT_STRATEGY", "ApplicationContextStrategy")
        if ContextManager._context_strategy is None:
            strategy_class = ContextManager.STRATEGY_REGISTRY.get(strategy_name)
            if strategy_class is None or not issubclass(strategy_class, ContextStrategy):
                raise ValueError(f"Invalid MCP_CONTEXT_STRATEGY: {strategy_name}")
            ContextManager._context_strategy = strategy_class()

        return ContextManager._context_strategy

    @staticmethod
    def get_client() -> RestApiV2Client:
        """Get the PagerDuty client from the current context."""
        return ContextManager.get_strategy().context.client

    @staticmethod
    def get_user() -> Optional[User]:
        """Get the user from the current context."""
        return ContextManager.get_strategy().context.user

    @staticmethod
    def set_strategy(strategy: ContextStrategy) -> None:
        """Set the context strategy directly (primarily for testing)."""
        ContextManager._context_strategy = strategy


def get_client():
    """Backwards-compatible helper to get the PagerDuty client from the current context."""
    return ContextManager.get_client()
