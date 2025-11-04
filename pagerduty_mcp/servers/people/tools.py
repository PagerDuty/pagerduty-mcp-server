"""Tools for PagerDuty People MCP Server.

This module consolidates tools from multiple domains:
- Users (2 tools)
- Teams (8 tools)
- Schedules (4 tools)
- On-calls (1 tool)
- Escalation Policies (2 tools)
"""

from pagerduty_mcp.common import get_client, paginate
from pagerduty_mcp.models.base import ListResponseModel

from .models import (
    EscalationPolicy,
    EscalationPolicyQuery,
    Oncall,
    OncallQuery,
    Schedule,
    ScheduleOverrideCreate,
    ScheduleQuery,
    Team,
    TeamCreateRequest,
    TeamMemberAdd,
    TeamQuery,
    User,
    UserQuery,
    UserReference,
)

# =============================================================================
# USER TOOLS
# =============================================================================


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


# =============================================================================
# TEAM TOOLS
# =============================================================================


def list_teams(query_model: TeamQuery) -> ListResponseModel[Team]:
    """List teams based on the provided query model.

    Args:
        query_model: The model containing the query parameters
    Returns:
        List of teams.
    """
    if query_model.scope == "my":
        user_data = get_user_data()
        user_team_ids = [team.id for team in user_data.teams]
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


# =============================================================================
# SCHEDULE TOOLS
# =============================================================================


def list_schedules(query_model: ScheduleQuery) -> ListResponseModel[Schedule]:
    """List schedules with optional filtering.

    Returns:
        List of schedules matching the query parameters
    """
    response = paginate(client=get_client(), entity="schedules", params=query_model.to_params())
    schedules = [Schedule(**schedule) for schedule in response]
    return ListResponseModel[Schedule](response=schedules)


def get_schedule(schedule_id: str) -> Schedule:
    """Get a specific schedule by ID.

    Args:
        schedule_id: The ID of the schedule to retrieve

    Returns:
        Schedule details
    """
    response = get_client().rget(f"/schedules/{schedule_id}")
    return Schedule.model_validate(response)


def create_schedule_override(schedule_id: str, override_request: ScheduleOverrideCreate) -> dict | list:
    """Create an override for a schedule.

    Args:
        schedule_id: The ID of the schedule to override
        override_request: Data for the schedule override

    Returns:
        The created schedule override
    """
    json_data = override_request.model_dump()

    for i, override in enumerate(json_data["overrides"]):
        original_override = override_request.overrides[i]
        override["start"] = original_override.start.isoformat()
        override["end"] = original_override.end.isoformat()

    return get_client().rpost(f"/schedules/{schedule_id}/overrides", json=json_data)


def list_schedule_users(schedule_id: str) -> ListResponseModel[User]:
    """List users in a schedule.

    Args:
        schedule_id: The ID of the schedule

    Returns:
        List of users in the schedule
    """
    response = get_client().rget(f"/schedules/{schedule_id}/users")
    users = [User(**user) for user in response]
    return ListResponseModel[User](response=users)


# =============================================================================
# ON-CALL TOOLS
# =============================================================================


def list_oncalls(query_model: OncallQuery) -> ListResponseModel[Oncall]:
    """List on-call schedules with optional filtering.

    Returns:
        List of on-call schedules matching the query parameters
    """
    response = paginate(client=get_client(), entity="oncalls", params=query_model.to_params())
    oncalls = [Oncall(**oncall) for oncall in response]
    return ListResponseModel[Oncall](response=oncalls)


# =============================================================================
# ESCALATION POLICY TOOLS
# =============================================================================


def list_escalation_policies(
    query_model: EscalationPolicyQuery,
) -> ListResponseModel[EscalationPolicy]:
    """List escalation policies with optional filtering.

    Returns:
        List of escalation policies matching the query parameters
    """
    response = paginate(client=get_client(), entity="escalation_policies", params=query_model.to_params())
    policies = [EscalationPolicy(**policy) for policy in response]
    return ListResponseModel[EscalationPolicy](response=policies)


def get_escalation_policy(policy_id: str) -> EscalationPolicy:
    """Get a specific escalation policy.

    Args:
        policy_id: The ID of the escalation policy to retrieve

    Returns:
        Escalation policy details
    """
    response = get_client().rget(f"/escalation_policies/{policy_id}")
    return EscalationPolicy.model_validate(response)


# =============================================================================
# TOOL LISTS
# =============================================================================

READ_TOOLS = [
    # Users (2)
    get_user_data,
    list_users,
    # Teams (3)
    list_teams,
    get_team,
    list_team_members,
    # Schedules (3)
    list_schedules,
    get_schedule,
    list_schedule_users,
    # On-calls (1)
    list_oncalls,
    # Escalation policies (2)
    list_escalation_policies,
    get_escalation_policy,
]

WRITE_TOOLS = [
    # Schedules (1)
    create_schedule_override,
    # Teams (5)
    create_team,
    update_team,
    delete_team,
    add_team_member,
    remove_team_member,
]
