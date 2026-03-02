from typing import Protocol, ContextManager
from pagerduty_mcp.context.mcp_context import MCPContext

class ContextStrategy(Protocol):
    """Protocol for context management strategies."""

    @property
    def context(self) -> MCPContext:
        ...

    def use_context(self, context: MCPContext) -> ContextManager:
        ...