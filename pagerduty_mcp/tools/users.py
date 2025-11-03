from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import ListResponseModel, User, UserQuery


def get_user_data(*, include: list[str] | None = None) -> User:
    """Get the current user's data.

    Args:
        include: Optional list of additional details to include (e.g., ['contact_methods'])

    Returns:
        User: User name, role, id, summary, teams, and optionally contact methods
    """
    params = {}
    if include:
        params["include[]"] = include

    response = get_client().rget("/users/me", params=params if params else None)

    # If contact_methods wasn't explicitly requested, remove reference-only data
    # PagerDuty API returns contact_method_reference types without include parameter
    if not include or "contact_methods" not in include:
        if "contact_methods" in response:
            contact_methods = response.get("contact_methods", [])
            if contact_methods and "_reference" in contact_methods[0].get("type", ""):
                response.pop("contact_methods")

    return User.model_validate(response)


def list_users(query_model: UserQuery) -> ListResponseModel[User]:
    """List users, optionally filtering by name (query) and team IDs.

    Args:
        query_model: Optional filtering parameters

    Returns:
        List of users matching the criteria.
    """
    # Use .get() instead of .rget() to avoid entity wrapping that converts nested objects to references
    response = get_client().get("/users", params=query_model.to_params())
    users_data = response.json()["users"]

    # If contact_methods wasn't explicitly requested, remove reference-only data
    # PagerDuty API returns contact_method_reference types without include parameter
    if not query_model.include or "contact_methods" not in query_model.include:
        for user_data in users_data:
            if "contact_methods" in user_data:
                # Check if these are references (not full objects)
                contact_methods = user_data.get("contact_methods", [])
                if contact_methods and "_reference" in contact_methods[0].get("type", ""):
                    # Remove reference-only contact methods
                    user_data.pop("contact_methods")

    users = [User.model_validate(user) for user in users_data]
    return ListResponseModel[User](response=users)
