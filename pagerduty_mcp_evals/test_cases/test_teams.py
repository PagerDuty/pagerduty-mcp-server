"""Tests for teams-related competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvokationResponse,
    MockToolCall,
)


class TeamsCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for teams-related queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvokationResponse(
                tool_name="list_teams",
                parameters=lambda params: True,
                response={"response": [{"id": "TEAM123", "name": "Dev Team"}]},
            ),
            MockMCPToolInvokationResponse(
                tool_name="list_services",
                parameters=lambda params: True,
                response={"response": [{"id": "SVC123", "name": "Web Service"}]},
            ),
            MockMCPToolInvokationResponse(
                tool_name="list_users",
                parameters=lambda params: params.get("query") == "Sara Connor",
                response={
                    "response": [
                        {
                            "id": "USER123",
                            "name": "Sara Connor",
                            "teams": [{"id": "TEAM456", "summary": "QA Team"}],
                        }
                    ]
                },
            ),
            MockMCPToolInvokationResponse(
                tool_name="list_users",
                parameters=lambda params: params.get("query") == "Kyle Reese",
                response={"response": [{"id": "USER456", "name": "Kyle Reese"}]},
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
TEAMS_COMPETENCY_TESTS = [
    TeamsCompetencyTest(
        query="Show all teams in PagerDuty.",
        expected_tool_calls=[MockToolCall(name="list_teams", parameters={})],
        description="Basic teams listing",
    ),
    TeamsCompetencyTest(
        query='Get the list of users in the "Dev Team" team.',
        expected_tool_calls=[
            MockToolCall(
                name="list_teams", parameters={"query_model": {"query": "Dev Team"}}
            ),
            MockToolCall(name="list_team_members", parameters={"team_id": "TEAM123"}),
        ],
        description="List incidents filtered by status",
    ),
    TeamsCompetencyTest(
        query="Create a new team called 'QA Team' with description 'Team for QA'",
        expected_tool_calls=[
            MockToolCall(
                name="create_team",
                parameters={
                    "create_model": {
                        "team": {"name": "QA Team", "description": "Team for QA"}
                    }
                },
            )
        ],
        description="Creating a new team",
    ),
    TeamsCompetencyTest(
        query='Rename the team "Dev Team" to "Archival Support."',
        expected_tool_calls=[
            MockToolCall(
                name="list_teams", parameters={"query_model": {"query": "Dev Team"}}
            ),
            MockToolCall(
                name="update_team",
                parameters={
                    "team_id": "TEAM123",
                    "update_model": {"team": {"name": "Archival Support"}},
                },
            ),
        ],
        description="Renaming a team",
    ),
    TeamsCompetencyTest(
        query='Delete the team "Dev Team."',
        expected_tool_calls=[
            MockToolCall(
                name="list_teams", parameters={"query_model": {"query": "Dev Team"}}
            ),
            MockToolCall(name="delete_team", parameters={"team_id": "TEAM123"}),
        ],
        description="Deleting a team",
    ),
    TeamsCompetencyTest(
        query='Add user Sara Connor to the "Dev Team" team.',
        expected_tool_calls=[
            MockToolCall(
                name="list_teams", parameters={"query_model": {"query": "Dev Team"}}
            ),
            MockToolCall(name="list_users", parameters={"query": "Sara Connor"}),
            MockToolCall(
                name="add_team_member",
                parameters={
                    "team_id": "TEAM123",
                    "member_data": {"user_id": "USER123"},
                },
            ),
        ],
        description="Adding a user to a team",
    ),
    TeamsCompetencyTest(
        query='Remove user Kyle Reese from the "Dev Team" team.',
        expected_tool_calls=[
            MockToolCall(
                name="list_teams", parameters={"query_model": {"query": "Dev Team"}}
            ),
            MockToolCall(name="list_users", parameters={"query": "Kyle Reese"}),
            MockToolCall(
                name="remove_team_member",
                parameters={"team_id": "TEAM123", "user_id": "USER456"},
            ),
        ],
        description="Removing a user from a team",
    ),
    TeamsCompetencyTest(
        query="Which teams is Sara Connor a member of?",
        expected_tool_calls=[
            MockToolCall(name="list_users", parameters={"query": "Sara Connor"})
        ],
        description="Find teams for a user",
    ),
    TeamsCompetencyTest(
        query="How many teams are in our PagerDuty account?",
        expected_tool_calls=[MockToolCall(name="list_teams", parameters={})],
        description="Count all teams in the account",
    ),
    TeamsCompetencyTest(
        query="Show me my teams",
        expected_tool_calls=[
            MockToolCall(name="list_teams", parameters={"query_model": {"scope": "my"}})
        ],
        description="List teams for the current user",
    ),
]
