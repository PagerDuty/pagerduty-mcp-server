from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    ListResponseModel,
    Team,
    TeamCreateRequest,
    TeamMemberAdd,
    TeamQuery,
    UserReference,
)
from pagerduty_mcp.tools.users import get_user_data
from pagerduty_mcp.utils import paginate


def list_teams(query_model: TeamQuery) -> ListResponseModel[Team]:
    """List teams based on the provided query model.

    Args:
        query_model: The model containing the query parameters
    Returns:
        List of teams.
    """
    if query_model.scope == "my":
        # get my team references from /users/me
        user_data = get_user_data()
        user_team_ids = [team.id for team in user_data.teams]
        # Now get all team resources. Paginate limits to 1000 results by default
        # TODO: Alternative approach. Fetch each team by ID.
        # TODO: No way to fetch multiple teams by ID in a single request - API improvement area
        results = paginate(client=get_client(), entity="teams", params={})
        teams = [Team(**team) for team in results if team["id"] in user_team_ids]
    else:
        response = paginate(client=get_client(), entity="teams", params=query_model.to_params())
        teams = [Team(**team) for team in response]
    return ListResponseModel[Team](response=teams)


def get_team(team_id: str) -> Team:
    """Get a specific team.

    Args:
        team_id: The ID or name of the team to retrieve
    Returns:
        Team details
    """
    response = get_client().rget(f"/teams/{team_id}")
    return Team.model_validate(response)


def create_team(create_model: TeamCreateRequest) -> Team:
    """Create a team.

    Returns:
        The created team.
    """
    response = get_client().rpost("/teams", json=create_model.model_dump())

    if type(response) is dict and "team" in response:
        return Team(**response["team"])

    return Team.model_validate(response)


def update_team(team_id: str, update_model: TeamCreateRequest) -> Team:
    """Update a team.

    Args:
        team_id: The ID of the team to update
        update_model: The model containing the updated team data
    Returns:
        The updated team
    """
    response = get_client().rput(f"/teams/{team_id}", json=update_model.model_dump())

    if type(response) is dict and "team" in response:
        return Team.model_validate(response["team"])

    return Team.model_validate(response)


def delete_team(team_id: str) -> None:
    """Delete a team.

    Args:
        team_id: The ID of the team to delete
    """
    get_client().rdelete(f"/teams/{team_id}")


def list_team_members(team_id: str) -> ListResponseModel[UserReference]:
    """List members of a team.

    Args:
        team_id: The ID of the team

    Returns:
        List of UserReference objects
    """
    response = paginate(client=get_client(), entity=f"/teams/{team_id}/members", params={})
    # The response is already a list, so we process it and wrap it
    users = [UserReference(**user.get("user")) for user in response]
    return ListResponseModel[UserReference](response=users)


def add_team_member(team_id: str, member_data: TeamMemberAdd) -> str:
    """Add a user to a team.

    Args:
        team_id: The ID of the team to add the user to
        member_data: Object containing the user ID and role to add to the team

    Returns:
        The API response confirming the addition
    """
    response = get_client().put(f"/teams/{team_id}/users/{member_data.user_id}", json=member_data.model_dump())
    if response:
        return "Successfully added user to team"
    return f"Failed to add user to team: {response.reason}"


def remove_team_member(team_id: str, user_id: str) -> None:
    """Remove a user from a team.

    Args:
        team_id: The ID of the team to remove the user from
        user_id: The ID of the user to remove
    """
    get_client().rdelete(f"/teams/{team_id}/users/{user_id}")
    # The API doesn't return any content for successful deletion
