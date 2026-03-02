import logging
from contextlib import AbstractContextManager

from dotenv import load_dotenv
from pagerduty.rest_api_v2_client import RestApiV2Client

from pagerduty_mcp.context.context_strategy import ContextData, ContextStrategy, ContextUser

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextResolver:
    """Creates a common interface for resolving the context of a request.

    This allows the application to determine things (like whether there is a user currently
    associated with the context) without needing to know the underlying strategy for how
    that context is created or accessed.

    Currently, two strategies are provided:
    - ApplicationContextStrategy: for single-tenant applications, where the same context is shared
      across the entire application lifecycle.
    - RequestContextStrategy: for multi-tenant applications, where a new context is created for
      each request (e.g. in middleware or an auth provider) and used for the duration of that request.

    But conceptually, you could also build other strategies (e.g a cache to avoid repeated API calls,
    or mocking for tests) and the rest of the application code would not need to be changed.

    A single-tenant application should set the PAGERDUTY_USER_API_KEY environment
    variable (and perhaps, PAGERDUTY_API_HOST), then initialize the strategy at application startup:

        ContextResolver.set_strategy(ApplicationContextStrategy())

    A multi-tenant application should also use the `use_context` helper at request time:

        # at application startup
        ContextResolver.set_strategy(RequestContextStrategy())

        # in the request handler (perhaps in middleware or an auth provider)
        client = ... build your PagerDuty API client ...
        context = MCPContext(client=client)

        with ContextResolver.use_context(context):
            ... yield to your request handler here ...
            ... ContextResolver.get_client() and .get_user() can now be used the same
                way as a single-tenant application ...
    """

    _context_strategy: ContextStrategy | None

    @staticmethod
    def set_strategy(strategy: ContextStrategy) -> None:
        ContextResolver._context_strategy = strategy

    @staticmethod
    def get_strategy() -> ContextStrategy:
        if ContextResolver._context_strategy is None:
            raise RuntimeError("No context strategy is available")
        return ContextResolver._context_strategy

    @staticmethod
    def use_context(context: ContextData) -> AbstractContextManager[ContextData]:
        return ContextResolver.get_strategy().use_context(context)

    @staticmethod
    def get_client() -> RestApiV2Client:
        """A shortcut to a PagerDuty client instance for API calls."""
        return ContextResolver.get_strategy().context.client

    @staticmethod
    def get_user() -> ContextUser | None:
        """A shortcut to the current PagerDuty user (if available)."""
        return ContextResolver.get_strategy().context.user
