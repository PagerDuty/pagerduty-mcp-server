
from abc import ABC, abstractmethod

from pagerduty_mcp.context.mcp_context import MCPContext
from contextlib import contextmanager

class ContextStrategy(ABC):
    """Abstract base class for context management strategies."""

    @property
    @abstractmethod
    def context(self) -> MCPContext:
        """Get the current context."""
        pass