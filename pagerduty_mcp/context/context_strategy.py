from contextlib import AbstractContextManager
from typing import Protocol

from pagerduty_mcp.context.mcp_context import MCPContext


class ContextStrategy(Protocol):
    """Protocol for context management strategies."""

    @property
    def context(self) -> MCPContext: ...

    def use_context(self, context: MCPContext) -> AbstractContextManager: ...
