"""Tests for incident-related competency questions."""

from pagerduty_mcp_evals.test_cases.agent_competency_test import (
    AgentCompetencyTest,
    MockMCPToolInvocationResponse,
    MockToolCall,
)


class IncidentCompetencyTest(AgentCompetencyTest):
    """Specialization of AgentCompetencyTest for incident-related queries."""

    def __init__(self, **kwargs) -> None:
        mock_responses = [
            MockMCPToolInvocationResponse(
                tool_name="list_teams",
                parameters=lambda params: True,
                response={"response": [{"id": "TEAM123", "name": "Dev Team"}]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_services",
                parameters=lambda params: True,
                response={"response": [{"id": "SVC123", "name": "Web Service"}]},
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_outlier_incident",
                parameters=lambda params: True,
                response={
                    "outlier_incident": {
                        "incident": {
                            "id": "OUT123",
                            "created_at": "2020-11-18T13:08:14Z",
                            "self": "https://api.pagerduty.com/incidents/OUT123",
                            "title": "Outlier Incident",
                            "occurrence": {
                                "count": 10,
                                "frequency": 0.04,
                                "category": "rare",
                                "since": "2020-09-23T13:08:14Z",
                                "until": "2021-01-18T13:08:14Z",
                            },
                        },
                        "incident_template": {
                            "id": "TEMPLATE123",
                            "cluster_id": "CLUSTER123",
                            "mined_text": "Test pattern <*>",
                        },
                    }
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_past_incidents",
                parameters=lambda params: True,
                response={
                    "past_incidents": [
                        {
                            "incident": {
                                "id": "PAST123",
                                "created_at": "2020-11-04T16:08:15Z",
                                "self": "https://api.pagerduty.com/incidents/PAST123",
                                "title": "Past Incident",
                            },
                            "score": 46.8249,
                        }
                    ],
                    "total": 1,
                    "limit": 5,
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_related_incidents",
                parameters=lambda params: True,
                response={
                    "related_incidents": [
                        {
                            "incident": {
                                "id": "REL123",
                                "created_at": "2020-11-18T13:08:14Z",
                                "self": "https://api.pagerduty.com/incidents/REL123",
                                "title": "Related incident",
                            },
                            "relationships": [
                                {
                                    "type": "machine_learning_inferred",
                                    "metadata": {
                                        "grouping_classification": "similar_contents"
                                    },
                                }
                            ],
                        }
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_incident_notes",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "id": "NOTE123",
                            "content": "First note about the incident",
                            "created_at": "2023-01-01T10:00:00Z",
                            "user": {"id": "USER123", "summary": "John Doe"},
                        },
                        {
                            "id": "NOTE456",
                            "content": "Second note with additional details",
                            "created_at": "2023-01-01T11:00:00Z",
                            "user": {"id": "USER456", "summary": "Jane Smith"},
                        },
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="list_alerts_from_incident",
                parameters=lambda params: True,
                response={
                    "response": [
                        {
                            "id": "PALERT123",
                            "type": "alert",
                            "summary": "The server is on fire.",
                            "self": "https://api.pagerduty.com/incidents/PINCIDENT123/alerts/PALERT123",
                            "html_url": "https://subdomain.pagerduty.com/alerts/PALERT123",
                            "created_at": "2015-10-06T21:30:42Z",
                            "status": "triggered",
                            "alert_key": "baf7cf21b1da41b4b0221008339ff357",
                            "severity": "critical",
                            "suppressed": False,
                        }
                    ]
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="get_alert_from_incident",
                parameters=lambda params: True,
                response={
                    "id": "PALERT123",
                    "type": "alert",
                    "summary": "The server is on fire.",
                    "self": "https://api.pagerduty.com/incidents/PINCIDENT123/alerts/PALERT123",
                    "html_url": "https://subdomain.pagerduty.com/alerts/PALERT123",
                    "created_at": "2015-10-06T21:30:42Z",
                    "status": "triggered",
                    "alert_key": "baf7cf21b1da41b4b0221008339ff357",
                    "severity": "critical",
                    "suppressed": False,
                },
            ),
            MockMCPToolInvocationResponse(
                tool_name="add_responders",
                parameters=lambda params: True,
                response={
                    "responder_request": {
                        "requester": {"id": "USER123", "type": "user_reference", "summary": "John Doe"},
                        "requested_at": "2023-01-01T12:00:00Z",
                        "message": "Need help with this incident",
                        "responder_request_targets": [
                            {
                                "responder_request_target": {
                                    "id": "USER456",
                                    "type": "user_reference",
                                    "incident_responders": {
                                        "state": "pending",
                                        "user": {
                                            "id": "USER456",
                                            "type": "user_reference",
                                            "summary": "Jane Smith",
                                        },
                                    },
                                }
                            }
                        ],
                    }
                },
            ),
        ]
        super().__init__(mock_responses=mock_responses, **kwargs)


# Define the competency test cases
INCIDENT_COMPETENCY_TESTS = [
    IncidentCompetencyTest(
        query="Show me all open and resolved incidents",
        expected_tool_calls=[
            MockToolCall(
                name="list_incidents",
                parameters={
                    "query_model": {"status": ["triggered", "acknowledged", "resolved"]}
                },
            )
        ],
        description="List incidents filtered by status",
    ),
    IncidentCompetencyTest(
        query="List open incidents",
        expected_tool_calls=[
            MockToolCall(
                name="list_incidents",
                parameters={"query_model": {"status": ["triggered", "acknowledged"]}},
            )
        ],
        description="List incidents filtered by status",
    ),
    IncidentCompetencyTest(
        query="Show me all incidents",
        expected_tool_calls=[MockToolCall(name="list_incidents", parameters={})],
        description="Basic incident listing",
    ),
    IncidentCompetencyTest(
        query="Show me all triggered incidents",
        expected_tool_calls=[
            MockToolCall(
                name="list_incidents",
                parameters={"query_model": {"status": ["triggered"]}},
            )
        ],
        description="List incidents filtered by status",
    ),
    IncidentCompetencyTest(
        query="Tell me about incident 123",
        expected_tool_calls=[
            MockToolCall(name="get_incident", parameters={"incident_id": "123"})
        ],
        description="Get specific incident by number",
    ),
    IncidentCompetencyTest(
        query="Get incident 123 with user details",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident",
                parameters={"incident_id": "123", "query_model": {"include": ["users"]}},
            )
        ],
        description="Get incident with users included",
    ),
    IncidentCompetencyTest(
        query="Show me incident ABC456 with teams and services",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident",
                parameters={
                    "incident_id": "ABC456",
                    "query_model": {"include": ["teams", "services"]},
                },
            )
        ],
        description="Get incident with multiple includes (teams and services)",
    ),
    IncidentCompetencyTest(
        query="Get incident 789 including escalation policies and log entries",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident",
                parameters={
                    "incident_id": "789",
                    "query_model": {"include": ["escalation_policies", "log_entries"]},
                },
            )
        ],
        description="Get incident with escalation policies and log entries",
    ),
    IncidentCompetencyTest(
        query="Show me all details for incident XYZ999 including users, teams, notes, and assignments",
        expected_tool_calls=[
            MockToolCall(
                name="get_incident",
                parameters={
                    "incident_id": "XYZ999",
                    "query_model": {"include": ["users", "teams", "notes", "assignments"]},
                },
            )
        ],
        description="Get incident with comprehensive includes (users, teams, notes, assignments)",
    ),
    IncidentCompetencyTest(
        query="Create an incident with title 'Testing MCP' for service with ID 1234 with high urgency",
        expected_tool_calls=[
            MockToolCall(
                name="create_incident",
                parameters={
                    "create_model": {
                        "incident": {
                            "title": "Testing MCP",
                            "service": {"id": "1234"},
                        }
                    }
                },
            )
        ],
        description="Create incident for team (allows team lookup)",
    ),
    IncidentCompetencyTest(
        query="Create a high urgency incident titled 'Server down' for the Website service",
        expected_tool_calls=[
            MockToolCall(
                name="create_incident",
                parameters={
                    "create_model": {
                        "incident": {"title": "Server down", "urgency": "high"}
                    }
                },
            )
        ],
        description="Create incident for service (allows service lookup)",
    ),
    IncidentCompetencyTest(
        query="Acknowledge incident 456",
        expected_tool_calls=[
            MockToolCall(
                name="manage_incidents",
                parameters={
                    "manage_request": {
                        "incident_ids": ["456"],
                        "status": "acknowledged",
                    }
                },
            )
        ],
        description="Acknowledge specific incident",
    ),
    IncidentCompetencyTest(
        query="Show me outlier analysis for incident 789",
        expected_tool_calls=[
            MockToolCall(
                name="get_outlier_incident",
                parameters={"incident_id": "789", "query_model": {}},
            )
        ],
        description="Get outlier incident information using specialized tool",
    ),
    IncidentCompetencyTest(
        query="Show me similar past incidents for incident ABC123",
        expected_tool_calls=[
            MockToolCall(
                name="get_past_incidents",
                parameters={"incident_id": "ABC123", "query_model": {}},
            )
        ],
        description="Get past incidents using specialized tool",
    ),
    IncidentCompetencyTest(
        query="Show me related incidents for incident DEF456",
        expected_tool_calls=[
            MockToolCall(
                name="get_related_incidents",
                parameters={"incident_id": "DEF456", "query_model": {}},
            )
        ],
        description="Get related incidents using specialized tool",
    ),
    IncidentCompetencyTest(
        query="Show me outlier analysis for incident 789 since September 2020",
        expected_tool_calls=[
            MockToolCall(
                name="get_outlier_incident",
                parameters={
                    "incident_id": "789",
                    "query_model": {"since": "2020-09-01T00:00:00Z"},
                },
            )
        ],
        description="Get outlier incident with since parameter for date filtering",
    ),
    IncidentCompetencyTest(
        query="Show me the top 10 past incidents similar to incident ABC123",
        expected_tool_calls=[
            MockToolCall(
                name="get_past_incidents",
                parameters={"incident_id": "ABC123", "query_model": {"limit": 10}},
            )
        ],
        description="Get past incidents with limit parameter to control result count",
    ),
    IncidentCompetencyTest(
        query="Show me past incidents for incident ABC123 and include the total count",
        expected_tool_calls=[
            MockToolCall(
                name="get_past_incidents",
                parameters={"incident_id": "ABC123", "query_model": {"total": True}},
            )
        ],
        description="Get past incidents with total parameter to include total count",
    ),
    IncidentCompetencyTest(
        query="Show me related incidents for incident DEF456 with full incident details",
        expected_tool_calls=[
            MockToolCall(
                name="get_related_incidents",
                parameters={
                    "incident_id": "DEF456",
                    "query_model": {"additional_details": ["incident"]},
                },
            )
        ],
        description="Get related incidents with additional_details parameter for enriched data",
    ),
    # Notes tests
    IncidentCompetencyTest(
        query="Show me all notes for incident 123",
        expected_tool_calls=[
            MockToolCall(
                name="list_incident_notes",
                parameters={"incident_id": "123"},
            )
        ],
        description="List all notes for a specific incident",
    ),
    IncidentCompetencyTest(
        query="What notes are on incident ABC123?",
        expected_tool_calls=[
            MockToolCall(
                name="list_incident_notes",
                parameters={"incident_id": "ABC123"},
            )
        ],
        description="List notes for incident using natural language query",
    ),
    IncidentCompetencyTest(
        query="List incident notes for Q3QCNPM78BXOAL",
        expected_tool_calls=[
            MockToolCall(
                name="list_incident_notes",
                parameters={"incident_id": "Q3QCNPM78BXOAL"},
            )
        ],
        description="List notes for incident with complex ID format",
    ),
    # Alert-related tests
    IncidentCompetencyTest(
        query="Show me all alerts for incident 123",
        expected_tool_calls=[
            MockToolCall(
                name="list_alerts_from_incident",
                parameters={"incident_id": "123", "query_model": {}},
            )
        ],
        description="List all alerts for a specific incident",
    ),
    IncidentCompetencyTest(
        query="What alerts are on incident PINCIDENT123?",
        expected_tool_calls=[
            MockToolCall(
                name="list_alerts_from_incident",
                parameters={"incident_id": "PINCIDENT123", "query_model": {}},
            )
        ],
        description="List alerts for incident using natural language query",
    ),
    IncidentCompetencyTest(
        query="Get the first 10 alerts for incident ABC123",
        expected_tool_calls=[
            MockToolCall(
                name="list_alerts_from_incident",
                parameters={"incident_id": "ABC123", "query_model": {"limit": 10}},
            )
        ],
        description="List alerts with limit parameter",
    ),
    IncidentCompetencyTest(
        query="Show me alert PALERT123 from incident PINCIDENT456",
        expected_tool_calls=[
            MockToolCall(
                name="get_alert_from_incident",
                parameters={"incident_id": "PINCIDENT456", "alert_id": "PALERT123"},
            )
        ],
        description="Get a specific alert from an incident",
    ),
    IncidentCompetencyTest(
        query="Get details of alert XYZ789 for incident 123",
        expected_tool_calls=[
            MockToolCall(
                name="get_alert_from_incident",
                parameters={"incident_id": "123", "alert_id": "XYZ789"},
            )
        ],
        description="Get specific alert using natural language query",
    ),
    # Issue #4: manage_incidents uses flat fields (incident_ids + status/urgency/etc)
    IncidentCompetencyTest(
        query="Resolve incidents 123 and 456",
        expected_tool_calls=[
            MockToolCall(
                name="manage_incidents",
                parameters={
                    "manage_request": {"incident_ids": ["123", "456"], "status": "resolved"}
                },
            )
        ],
        description="Resolve multiple incidents using flat field format",
    ),
    IncidentCompetencyTest(
        query="Change the urgency of incident ABC123 to low",
        expected_tool_calls=[
            MockToolCall(
                name="manage_incidents",
                parameters={
                    "manage_request": {"incident_ids": ["ABC123"], "urgency": "low"}
                },
            )
        ],
        description="Change incident urgency using flat field format",
    ),
    IncidentCompetencyTest(
        query="Reassign incident 789 to user USER456",
        expected_tool_calls=[
            MockToolCall(
                name="manage_incidents",
                parameters={
                    "manage_request": {
                        "incident_ids": ["789"],
                        "assignement": {"id": "USER456"},
                    }
                },
            )
        ],
        description="Reassign incident using flat field format with UserReference",
    ),
    # Issue #1: add_responders - requester_id is auto-populated, LLM should NOT provide it
    IncidentCompetencyTest(
        query="Add user USER456 as a responder to incident 123 with the message 'Need help with this incident'",
        expected_tool_calls=[
            MockToolCall(
                name="add_responders",
                parameters={
                    "incident_id": "123",
                    "request": {
                        "message": "Need help with this incident",
                        "responder_request_targets": [
                            {
                                "responder_request_target": {
                                    "id": "USER456",
                                    "type": "user_reference",
                                }
                            }
                        ],
                    },
                },
            )
        ],
        description="Add a user responder to an incident (requester_id auto-populated)",
    ),
    IncidentCompetencyTest(
        query="Request escalation policy EP123 as responder for incident ABC456",
        expected_tool_calls=[
            MockToolCall(
                name="add_responders",
                parameters={
                    "incident_id": "ABC456",
                    "request": {
                        "responder_request_targets": [
                            {
                                "responder_request_target": {
                                    "id": "EP123",
                                    "type": "escalation_policy_reference",
                                }
                            }
                        ],
                    },
                },
            )
        ],
        description="Add an escalation policy as responder to an incident",
    ),
    IncidentCompetencyTest(
        query="Add users USER111 and USER222 as responders to incident 999 with the message 'All hands on deck'",
        expected_tool_calls=[
            MockToolCall(
                name="add_responders",
                parameters={
                    "incident_id": "999",
                    "request": {
                        "message": "All hands on deck",
                        "responder_request_targets": [
                            {
                                "responder_request_target": {
                                    "id": "USER111",
                                    "type": "user_reference",
                                }
                            },
                            {
                                "responder_request_target": {
                                    "id": "USER222",
                                    "type": "user_reference",
                                }
                            },
                        ],
                    },
                },
            )
        ],
        description="Add multiple user responders to an incident",
    ),
]
