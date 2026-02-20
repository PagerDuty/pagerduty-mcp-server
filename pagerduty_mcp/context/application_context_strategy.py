import os

from importlib import metadata
from pagerduty.rest_api_v2_client import RestApiV2Client

from pagerduty_mcp import DIST_NAME
from pagerduty_mcp.context.mcp_context import MCPContext
from pagerduty_mcp.context.context_strategy import ContextStrategy

class PagerdutyMCPClient(RestApiV2Client):
    @property
    def user_agent(self) -> str:
        return f"{DIST_NAME}/{metadata.version(DIST_NAME)} {super().user_agent}"

def create_pd_client() -> RestApiV2Client:
    """Create a PagerDuty client."""
    api_key = os.getenv("PAGERDUTY_USER_API_KEY")
    api_host = os.getenv("PAGERDUTY_API_HOST", "https://api.pagerduty.com")

    if not api_key:
        raise RuntimeError("An API key is required to call the PagerDuty API.")

    pd_client = PagerdutyMCPClient(api_key)
    if api_host:
        pd_client.url = api_host
    return pd_client


class ApplicationContextStrategy(ContextStrategy):
    """Application-scoped context using instance variables."""

    def __init__(self):
        client = create_pd_client()
        self._context = MCPContext(client)

    @property
    def context(self) -> MCPContext:
        """Get the current context."""
        return self._context
