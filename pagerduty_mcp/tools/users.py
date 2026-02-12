
from pagerduty_mcp.models import ListResponseModel, User, UserQuery, MCPContext
from pagerduty_mcp.utils import inject_context


@inject_context
def get_user_data(context: MCPContext) -> User:
    """Get the current user's data.

    Args:
        context: The MCP context with client and user info (injected)

    Returns:
        User: User name, role, id, and summary and teams
    """
    response = context.client.rget("/users/me")
    return User.model_validate(response)


@inject_context
def list_users(query_model: UserQuery, context: MCPContext) -> ListResponseModel[User]:
    """List users, optionally filtering by name (query) and team IDs.

    Args:
        query_model: Optional filtering parameters
        context: The MCP context with client and user info (injected)

    Returns:
        List of users matching the criteria.
    """
    response = context.client.rget("/users", params=query_model.to_params())
    users = [User(**user) for user in response]
    return ListResponseModel[User](response=users)
