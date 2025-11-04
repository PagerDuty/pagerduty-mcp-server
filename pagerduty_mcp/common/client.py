import logging
import os
from collections.abc import Callable
from contextvars import ContextVar
from functools import lru_cache
from importlib import metadata

from dotenv import load_dotenv
from pagerduty.rest_api_v2_client import RestApiV2Client

from pagerduty_mcp import DIST_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("PAGERDUTY_USER_API_KEY")
API_HOST = os.getenv("PAGERDUTY_API_HOST", "https://api.pagerduty.com")


class PagerdutyMCPClient(RestApiV2Client):
    @property
    def user_agent(self) -> str:
        return f"{DIST_NAME}/{metadata.version(DIST_NAME)} {super().user_agent}"


ClientFactory = Callable[[], RestApiV2Client]
pd_client_factory: ContextVar[ClientFactory | None] = ContextVar("pd_client_factory", default=None)


@lru_cache(maxsize=1)
def _get_cached_client(api_key: str, api_host: str) -> RestApiV2Client:
    """Get a cached PagerDuty client."""
    return create_pd_client(api_key, api_host)


def create_pd_client(api_key: str, api_host: str | None = None) -> RestApiV2Client:
    """Get the PagerDuty client."""
    pd_client = PagerdutyMCPClient(api_key)
    if api_host:
        pd_client.url = api_host

    return pd_client


def get_client() -> RestApiV2Client:
    """Get the PagerDuty client, using cached configuration if available.

    This function will check if client config information is stored in a context var.
    If it is, that means the package is being used in a remote MCP server context, and
    we need to update the client credentials for each request, since remote MCP servers
    need to support multi tenancy.
    """
    client_factory = pd_client_factory.get(None)
    if client_factory is not None:
        return client_factory()

    return _get_cached_client(API_KEY, API_HOST)
