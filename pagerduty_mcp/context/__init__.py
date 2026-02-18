
import logging
import os
from typing import Optional, Type
from importlib import import_module

from dotenv import load_dotenv

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.models.users import User
from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty_mcp.context.app_context_strategy import ApplicationContextStrategy
from pagerduty_mcp.context.request_context_strategy import RequestContextStrategy
from pagerduty_mcp.context.context_strategy import ContextStrategy

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STRATEGY_REGISTRY = {
    "ApplicationContextStrategy": ApplicationContextStrategy,
    "RequestContextStrategy": RequestContextStrategy,
}

_context_strategy: Optional[ContextStrategy] = None

def get_context() -> MCPContext:
    """Get the current MCP request context."""
    if _context_strategy is None:
        # Try to initialize strategy based on environment variable
        strategy_name = os.getenv("MCP_CONTEXT_STRATEGY", "ApplicationContextStrategy")
        strategy_class = STRATEGY_REGISTRY.get(strategy_name)
        if strategy_class is None:
            raise ValueError(f"Invalid MCP_CONTEXT_STRATEGY: {strategy_name}")
        set_strategy(strategy_class())

    return _context_strategy.get_context()


def get_client() -> RestApiV2Client:
    """Get the PagerDuty client using current strategy."""
    return get_context().client


def get_user() -> Optional[User]:
    """Get the user from the current context."""
    return get_context().client


def set_strategy(strategy: ContextStrategy) -> ContextStrategy | None:
    """Set the context strategy (primarily for testing)."""
    global _context_strategy
    _context_strategy = strategy
    return strategy
