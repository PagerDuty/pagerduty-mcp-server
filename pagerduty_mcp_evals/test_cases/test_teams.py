"""Tests for teams-related competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class TeamsCompetencyTest(CompetencyTest):
    """Specialization of CompetencyTest for teams-related queries."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to enable multi-turn conversations."""
        mcp.register_mock_response(
            "list_teams", lambda params: True, {"response": [{"id": "TEAM123", "name": "Dev Team"}]}
        )
        mcp.register_mock_response(
            "list_services", lambda params: True, {"response": [{"id": "SVC123", "name": "Web Service"}]}
        )
        mcp.register_mock_response(
            "list_users",
            lambda params: params.get("query") == "Sara Connor",
            {
                "response": [
                    {"id": "USER123", "name": "Sara Connor", "teams": [{"id": "TEAM456", "summary": "QA Team"}]}
                ]
            },
        )
        mcp.register_mock_response(
            "list_users",
            lambda params: params.get("query") == "Kyle Reese",
            {"response": [{"id": "USER456", "name": "Kyle Reese"}]},
        )


# Define the competency test cases
TEAMS_COMPETENCY_TESTS = [
    TeamsCompetencyTest(
        query="Show all teams in PagerDuty.",
        expected_tools=[{"tool_name": "list_teams", "parameters": {}}],
        description="Basic teams listing",
    ),
    TeamsCompetencyTest(
        query="Get the list of users in the “Dev Team” team.",
        expected_tools=[
            {"tool_name": "list_teams", "parameters": {"query_model": {"query": "Dev Team"}}},
            {"tool_name": "list_team_members", "parameters": {"team_id": "TEAM123"}},
        ],
        description="List incidents filtered by status",
    ),
    TeamsCompetencyTest(
        query="Create a new team called 'QA Team' with description 'Team for QA'",
        expected_tools=[
            {
                "tool_name": "create_team",
                "parameters": {"create_model": {"team": {"name": "QA Team", "description": "Team for QA"}}},
            }
        ],
        description="Creating a new team",
    ),
    TeamsCompetencyTest(
        query="Rename the team “Dev Team” to “Archival Support.”",
        expected_tools=[
            {"tool_name": "list_teams", "parameters": {"query_model": {"query": "Dev Team"}}},
            {
                "tool_name": "update_team",
                "parameters": {"team_id": "TEAM123", "update_model": {"team": {"name": "Archival Support"}}},
            },
        ],
        description="Renaming a team",
    ),
    TeamsCompetencyTest(
        query='Delete the team "Dev Team."',
        expected_tools=[
            {"tool_name": "list_teams", "parameters": {"query_model": {"query": "Dev Team"}}},
            {"tool_name": "delete_team", "parameters": {"team_id": "TEAM123"}},
        ],
        description="Deleting a team",
    ),
    TeamsCompetencyTest(
        query='Add user Sara Connor to the "Dev Team" team.',
        expected_tools=[
            {"tool_name": "list_teams", "parameters": {"query_model": {"query": "Dev Team"}}},
            {"tool_name": "list_users", "parameters": {"query": "Sara Connor"}},
            {
                "tool_name": "add_team_member",
                "parameters": {"team_id": "TEAM123", "member_data": {"user_id": "USER123"}},
            },
        ],
        description="Adding a user to a team",
    ),
    TeamsCompetencyTest(
        query="Remove user Kyle Reese from the “Dev Team” team.",
        expected_tools=[
            {"tool_name": "list_teams", "parameters": {"query_model": {"query": "Dev Team"}}},
            {"tool_name": "list_users", "parameters": {"query": "Kyle Reese"}},
            {"tool_name": "remove_team_member", "parameters": {"team_id": "TEAM123", "user_id": "USER456"}},
        ],
        description="Removing a user from a team",
    ),
    TeamsCompetencyTest(
        query="Which teams is Sara Connor a member of?",
        expected_tools=[{"tool_name": "list_users", "parameters": {"query": "Sara Connor"}}],
        description="Find teams for a user",
    ),
    TeamsCompetencyTest(
        query="How many teams are in our PagerDuty account?",
        expected_tools=[{"tool_name": "list_teams", "parameters": {}}],
        description="Count all teams in the account",
    ),
    TeamsCompetencyTest(
        query="Show me my teams",
        expected_tools=[{"tool_name": "list_teams", "parameters": {"query_model": {"scope": "my"}}}],
        description="List teams for the current user",
    ),
]
