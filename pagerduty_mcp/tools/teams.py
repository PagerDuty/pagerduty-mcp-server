from pagerduty_mcp.models import (
    ListResponseModel,
    Team,
    TeamCreateRequest,
    TeamMemberAdd,
    TeamQuery,
    UserReference,
    MCPContext,
)
from pagerduty_mcp.utils import inject_context, paginate


@inject_context
def list_teams(query_model: TeamQuery, context: MCPContext) -> ListResponseModel[Team]:
    """List teams based on the provided query model.

    Args:
        query_model: The model containing the query parameters
        context: The MCP context with client and user info (injected)
    Returns:
        List of teams.
    """
    if query_model.scope == "my":
        # get my team references from /users/me
        user_data = context.user

        if not user_data:
            raise ValueError("A user context is required for this scope.")

        user_team_ids = [team.id for team in user_data.teams]
        # Now get all team resources. Paginate limits to 1000 results by default
        # TODO: Alternative approach. Fetch each team by ID.
        # TODO: No way to fetch multiple teams by ID in a single request - API improvement area
        results = paginate(client=context.client, entity="teams", params={})
        teams = [Team(**team) for team in results if team["id"] in user_team_ids]
    else:
        results = paginate(client=context.client, entity="teams", params=query_model.to_params())
        teams = [Team(**team) for team in results]
    return ListResponseModel[Team](response=teams)


@inject_context
def get_team(team_id: str, context: MCPContext) -> Team:
    """Get a specific team.

    Args:
        team_id: The ID or name of the team to retrieve
        context: The MCP context with client and user info (injected)
    Returns:
        Team details
    """
    response = context.client.rget(f"/teams/{team_id}")
    return Team.model_validate(response)


@inject_context
def create_team(create_model: TeamCreateRequest, context: MCPContext) -> Team:
    """Create a team.

    Args:
        create_model: The team creation request data
        context: The MCP context with client and user info (injected)

    Returns:
        The created team.
    """
    response = context.client.rpost("/teams", json=create_model.model_dump())

    if type(response) is dict and "team" in response:
        return Team(**response["team"])

    return Team.model_validate(response)


@inject_context
def update_team(team_id: str, update_model: TeamCreateRequest, context: MCPContext) -> Team:
    """Update a team.

    Args:
        team_id: The ID of the team to update
        update_model: The model containing the updated team data
        context: The MCP context with client and user info (injected)
    Returns:
        The updated team
    """
    response = context.client.rput(f"/teams/{team_id}", json=update_model.model_dump())

    if type(response) is dict and "team" in response:
        return Team.model_validate(response["team"])

    return Team.model_validate(response)


@inject_context
def delete_team(team_id: str, context: MCPContext) -> None:
    """Delete a team.

    Args:
        team_id: The ID of the team to delete
        context: The MCP context with client and user info (injected)
    """
    context.client.rdelete(f"/teams/{team_id}")


@inject_context
def list_team_members(team_id: str, context: MCPContext) -> ListResponseModel[UserReference]:
    """List members of a team.

    Args:
        team_id: The ID of the team
        context: The MCP context with client and user info (injected)

    Returns:
        List of UserReference objects
    """
    response = paginate(client=context.client, entity=f"/teams/{team_id}/members", params={})
    # The response is already a list, so we process it and wrap it
    users = [UserReference(**user.get("user")) for user in response]
    return ListResponseModel[UserReference](response=users)


@inject_context
def add_team_member(team_id: str, member_data: TeamMemberAdd, context: MCPContext) -> str:
    """Add a user to a team.

    Args:
        team_id: The ID of the team to add the user to
        member_data: Object containing the user ID and role to add to the team
        context: The MCP context with client and user info (injected)

    Returns:
        The API response confirming the addition
    """
    response = context.client.put(f"/teams/{team_id}/users/{member_data.user_id}", json=member_data.model_dump())
    if response:
        return "Successfully added user to team"
    return f"Failed to add user to team: {response.reason}"


@inject_context
def remove_team_member(team_id: str, user_id: str, context: MCPContext) -> None:
    """Remove a user from a team.

    Args:
        team_id: The ID of the team to remove the user from
        user_id: The ID of the user to remove
        context: The MCP context with client and user info (injected)
    """
    context.client.rdelete(f"/teams/{team_id}/users/{user_id}")
    # The API doesn't return any content for successful deletion
