from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty.errors import HttpError
from functools import wraps
from typing import TypeVar, Callable

from mcp.server.fastmcp import Context
from pagerduty_mcp.models import MAX_RESULTS, MCPContext, User

R = TypeVar('R')


def inject_context(func: Callable[..., R]) -> Callable[..., R]:
    """Decorator that injects the full MCP context.

    Callers pass `ctx` (type: Context), decorator transforms it to MCPContext
    and passes it as `context` to the decorated function.

    Usage:
        @inject_context
        def my_func(arg1: str, context: MCPContext) -> Result:
            # context is MCPContext here
            return context.client.rget(...)

        # Callers use 'ctx' parameter name:
        my_func("value", ctx=mcp_context_object)

    Args:
        func: Function with `context: MCPContext` parameter

    Returns:
        Wrapper that accepts `ctx: Context` and transforms it to `context: MCPContext`
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'ctx' in kwargs:
            ctx_arg = kwargs.pop('ctx')
            # If it's a Context object, extract MCPContext from it
            if hasattr(ctx_arg, 'request_context'):
                mcp_ctx: MCPContext = ctx_arg.request_context.lifespan_context
            else:
                # Already MCPContext (e.g., in tests)
                mcp_ctx = ctx_arg
            kwargs['context'] = mcp_ctx
            return func(*args, **kwargs)
        
        # If no 'ctx' parameter, call function as-is (context might be passed directly)
        return func(*args, **kwargs)

    return wrapper


def get_mcp_context(client: RestApiV2Client) -> MCPContext:
    """Get MCP Context.

    This function takes the user credentials and determines if this is an account or user level
    auth mode.

    If the credentials are bound to a user, it will return the user Schema. Otherwise None.
    The client is always included in the context for dependency injection.
    """
    try:
        response = client.rget("/users/me")
        # add the from header so all requests are made from the user
        if type(response) is dict:
            user_email = response.get("email", "no-email-provided")
            client.headers["From"] = user_email
        return MCPContext(client=client, user=User.model_validate(response))

    except HttpError:
        return MCPContext(client=client, user=None)


def paginate(*, client: RestApiV2Client, entity: str, params: dict, maximum_records: int = MAX_RESULTS):
    """Paginate results.

    Paginate through the results of a request to the PagerDuty API, while allowing for early termination
    if the maximum number of records is reached.

    Args:
        client: The RestApiV2Client instance to use for API requests
        entity: The entity to paginate through (e.g., "incidents")
        params: The parameters to pass to the API request
        maximum_records: The maximum number of records to return
    Returns:
        A list of results
    """
    results = []
    count = 0
    for incident in client.iter_all(entity, params=params):
        results.append(incident)
        count += 1  # noqa: SIM113
        if count >= maximum_records:
            break
    return results
