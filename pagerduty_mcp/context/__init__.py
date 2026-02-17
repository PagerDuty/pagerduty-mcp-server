
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

# Strategy registry for built-in strategies
STRATEGY_REGISTRY = {
    "ApplicationContextStrategy": ApplicationContextStrategy,
    "RequestContextStrategy": RequestContextStrategy,
}

def _load_strategy_class(strategy_name: str) -> Type[ContextStrategy]:
    """Load a strategy class by name."""
    # First check the built-in registry
    if strategy_name in STRATEGY_REGISTRY:
        return STRATEGY_REGISTRY[strategy_name]

    # Try to import as a fully qualified module path
    try:
        module_path, class_name = strategy_name.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ValueError, ImportError, AttributeError) as e:
        raise ValueError(f"Could not load strategy class '{strategy_name}': {e}")

# Lazy initialization - only create strategy when first accessed
_context_strategy: Optional[ContextStrategy] = None

def _get_strategy() -> ContextStrategy:
    """Get or create the context strategy instance."""
    global _context_strategy
    if _context_strategy is None:
        strategy_name = os.getenv("PAGERDUTY_MCP_CONTEXT_STRATEGY", "ApplicationContextStrategy")
        strategy_class = _load_strategy_class(strategy_name)
        _context_strategy = strategy_class()
    return _context_strategy


def get_context() -> MCPContext:
    """Get the current MCP request context."""
    return _get_strategy().get_context()


def get_client() -> RestApiV2Client:
    """Get the PagerDuty client using current strategy."""
    return _get_strategy().get_client()


def get_user() -> Optional[User]:
    """Get the user from the current context."""
    return _get_strategy().get_user()


def set_strategy(strategy: ContextStrategy) -> None:
    """Set the context strategy (primarily for testing)."""
    global _context_strategy
    _context_strategy = strategy


def reset_strategy() -> None:
    """Reset the context strategy to None (forces reload from environment)."""
    global _context_strategy
    _context_strategy = None
