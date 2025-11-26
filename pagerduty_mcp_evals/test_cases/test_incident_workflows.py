"""Tests for incident workflow competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvokationResponse,
    MockToolCall,
)


class IncidentWorkflowCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for incident workflow queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvokationResponse(
                tool_name="list_incident_workflows",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "id": "PSFEVL7",
                            "name": "Example Incident Workflow",
                            "description": "This Incident Workflow is an example",
                            "type": "incident_workflow",
                            "created_at": "2022-12-13T19:55:01.171Z",
                            "is_enabled": True,
                        }
                    ]
                },
            ),
            MockMCPToolInvokationResponse(
                tool_name="get_incident_workflow",
                parameters=lambda params: True,
                response={
                    "id": "PSFEVL7",
                    "name": "Example Incident Workflow",
                    "description": "This Incident Workflow is an example",
                    "type": "incident_workflow",
                    "created_at": "2022-12-13T19:55:01.171Z",
                    "is_enabled": True,
                    "steps": [
                        {
                            "id": "P4RG7YW",
                            "type": "step",
                            "name": "Send Status Update",
                            "description": "Posts a status update to a given incident",
                            "action_configuration": {
                                "action_id": "pagerduty.com:incident-workflows:send-status-update:1",
                                "description": "Posts a status update to a given incident",
                                "inputs": [
                                    {
                                        "name": "Message",
                                        "parameter_type": "text",
                                        "value": "Example status message sent on {{current_date}}",
                                    }
                                ],
                            },
                        }
                    ],
                },
            ),
            MockMCPToolInvokationResponse(
                tool_name="start_incident_workflow",
                parameters=lambda params: True,
                response={
                    "id": "P3SNKQS",
                    "type": "incident_workflow_instance",
                    "incident": {
                        "id": "Q1R2DLCB21K7NP",
                        "type": "incident_reference",
                        "summary": "[#1234] The server is on fire.",
                    },
                },
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
INCIDENT_WORKFLOW_COMPETENCY_TESTS = [
    IncidentWorkflowCompetencyTest(
        query="List all incident workflows",
        expected_tool_calls=[
            MockToolCall(
                name="list_incident_workflows", parameters={"query_model": None}
            )
        ],
        description="Basic workflow listing",
    ),
    IncidentWorkflowCompetencyTest(
        query="Show me all incident workflows",
        expected_tool_calls=[
            MockToolCall(
                name="list_incident_workflows", parameters={"query_model": None}
            )
        ],
        description="Basic workflow listing with natural language",
    ),
    IncidentWorkflowCompetencyTest(
        query="List incident workflows with name containing 'example'",
        expected_tool_calls=[
            MockToolCall(
                name="list_incident_workflows",
                parameters={"query_model": {"query": "example"}},
            )
        ],
        description="List workflows with query filter",
    ),
    IncidentWorkflowCompetencyTest(
        query="Show me the first 5 incident workflows",
        expected_tool_calls=[
            MockToolCall(
                name="list_incident_workflows",
                parameters={"query_model": {"limit": 5}},
            )
        ],
        description="List workflows with limit parameter",
    ),
    IncidentWorkflowCompetencyTest(
        query="List incident workflows and include their steps",
        expected_tool_calls=[
            MockToolCall(
                name="list_incident_workflows",
                parameters={"query_model": {"include": ["steps"]}},
            )
        ],
        description="List workflows with include parameter for steps",
    ),
    IncidentWorkflowCompetencyTest(
        query="Show me incident workflows including team information",
        expected_tool_calls=[
            MockToolCall(
                name="list_incident_workflows",
                parameters={"query_model": {"include": ["team"]}},
            )
        ],
        description="List workflows with include parameter for team",
    ),
    IncidentWorkflowCompetencyTest(
        query="Get details for incident workflow PSFEVL7",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident_workflow", parameters={"workflow_id": "PSFEVL7"}
            )
        ],
        description="Get specific workflow by ID",
    ),
    IncidentWorkflowCompetencyTest(
        query="Show me the incident workflow with ID ABC123",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident_workflow", parameters={"workflow_id": "ABC123"}
            )
        ],
        description="Get specific workflow by ID with natural language",
    ),
    IncidentWorkflowCompetencyTest(
        query="Tell me about incident workflow PSFEVL7",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident_workflow", parameters={"workflow_id": "PSFEVL7"}
            )
        ],
        description="Get workflow details",
    ),
    IncidentWorkflowCompetencyTest(
        query="Start incident workflow PSFEVL7 for incident Q1R2DLCB21K7NP",
        expected_tool_calls=[
            MockToolCall(
                name="start_incident_workflow",
                parameters={
                    "workflow_id": "PSFEVL7",
                    "instance_request": {
                        "incident_workflow_instance": {
                            "incident": {"id": "Q1R2DLCB21K7NP"}
                        }
                    },
                },
            )
        ],
        description="Start workflow instance for an incident",
    ),
    IncidentWorkflowCompetencyTest(
        query="Trigger workflow ABC123 on incident XYZ789",
        expected_tool_calls=[
            MockToolCall(
                name="start_incident_workflow",
                parameters={
                    "workflow_id": "ABC123",
                    "instance_request": {
                        "incident_workflow_instance": {"incident": {"id": "XYZ789"}}
                    },
                },
            )
        ],
        description="Start workflow with different terminology (trigger)",
    ),
    IncidentWorkflowCompetencyTest(
        query="Run incident workflow PSFEVL7 for incident Q1R2DLCB21K7NP",
        expected_tool_calls=[
            MockToolCall(
                name="start_incident_workflow",
                parameters={
                    "workflow_id": "PSFEVL7",
                    "instance_request": {
                        "incident_workflow_instance": {
                            "incident": {"id": "Q1R2DLCB21K7NP"}
                        }
                    },
                },
            )
        ],
        description="Start workflow with different terminology (run)",
    ),
]
