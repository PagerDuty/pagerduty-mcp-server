"""Tests for escalation policies-related competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)


class EscalationPoliciesCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for escalation policies-related queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="list_escalation_policies",
                parameters=lambda params: True,
                response={
                    "response": [
                        {"id": "EP123", "name": "Default EP", "summary": "Default escalation policy"},
                        {"id": "EP456", "name": "Engineering EP", "summary": "Engineering escalation policy"},
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_escalation_policy",
                parameters=lambda params: params.get("policy_id") == "EP123",
                response={"id": "EP123", "name": "Default EP", "summary": "Default escalation policy"},
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_user_data",
                parameters=lambda params: True,
                response={"id": "USER123", "name": "Test User", "email": "user@example.com"},
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


ESCALATION_POLICIES_COMPETENCY_TESTS = [
    EscalationPoliciesCompetencyTest(
        query="Show me all escalation policies",
        expected_tool_calls=[MockToolCall(name="list_escalation_policies", parameters={})],
        description="Basic escalation policies listing",
    ),
    EscalationPoliciesCompetencyTest(
        query="Get details for escalation policy EP123",
        expected_tool_calls=[
            MockToolCall(name="get_escalation_policy", parameters={"policy_id": "EP123"})
        ],
        description="Get specific escalation policy by ID",
    ),
    EscalationPoliciesCompetencyTest(
        query="Create an escalation policy named 'On-Call Policy' with a 30 minute delay targeting user USER123",
        expected_tool_calls=[
            MockToolCall(
                name="create_escalation_policy",
                parameters={
                    "escalation_policy_data": {
                        "escalation_policy": {
                            "name": "On-Call Policy",
                            "escalation_rules": [
                                {
                                    "escalation_delay_in_minutes": 30,
                                    "targets": [{"id": "USER123", "type": "user_reference"}],
                                }
                            ],
                        }
                    }
                },
            )
        ],
        description="Create escalation policy with one rule targeting a user",
    ),
    EscalationPoliciesCompetencyTest(
        query="Update escalation policy EP123 to change its name to 'Updated Policy'",
        expected_tool_calls=[
            MockToolCall(
                name="update_escalation_policy",
                parameters={
                    "policy_id": "EP123",
                    "escalation_policy_data": {
                        "escalation_policy": {
                            "name": "Updated Policy",
                        }
                    },
                },
            )
        ],
        description="Update escalation policy name",
    ),
]
