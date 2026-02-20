
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
    """Module-level context management for MCP."""

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
