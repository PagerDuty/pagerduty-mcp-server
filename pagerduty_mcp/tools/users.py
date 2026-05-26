from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel, User
from pagerduty_mcp.models.users import CreateUserRequest


def get_user_data() -> User:
    """Get the current user's data.

    Returns:
        User: User name, role, id, and summary and teams
    """
    response = get_client().rget("/users/me")
    return User.model_validate(response)


def list_users(
    query: str | None = None,
    teams_ids: list[str] | None = None,
    limit: int | None = 100,
) -> ListResponseModel[User]:
    """List users, optionally filtering by name (query) and team IDs.

    Args:
        query: Filters the result, showing only the records whose name matches the query.
        teams_ids: Filter users by team IDs.
        limit: Pagination limit. Default 100.

    Returns:
        List of users matching the criteria.
    """
    params: dict[str, Any] = {}
    if query:
        params["query"] = query
    if teams_ids:
        params["team_ids[]"] = teams_ids
    if limit:
        params["limit"] = limit

    response = get_client().rget("/users", params=params)
    users = [User(**user) for user in response]
    return ListResponseModel[User](response=users)


def create_user(request: CreateUserRequest) -> User:
    """Create a new PagerDuty user account. No invitation email is sent.

    Args:
        request: User creation parameters (name, email, role, time_zone)

    Returns:
        The created User object.
    """
    response = get_client().rpost("/users", json=request.model_dump())
    if isinstance(response, dict) and "user" in response:
        return User(**response["user"])
    return User.model_validate(response)
