from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel, User, UserQuery


def get_user_data() -> User:
    """Get the current user's data.

    Returns:
        User: User name, role, id, and summary and teams
    """
    response = get_client().rget("/users/me")
    return User.model_validate(response)


def list_users(query_model: UserQuery) -> ListResponseModel[User]:
    """List users, optionally filtering by name (query) and team IDs.

    Args:
        query_model: Optional filtering parameters

    Returns:
        List of users matching the criteria.
    """
    response = get_client().rget("/users", params=query_model.to_params())
    users = [User(**user) for user in response]
    return ListResponseModel[User](response=users)
