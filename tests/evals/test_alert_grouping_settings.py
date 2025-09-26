"""Tests for alert grouping settings-related competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class AlertGroupingSettingsCompetencyTest(CompetencyTest):
    """Specialization of CompetencyTest for alert grouping settings-related queries."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to enable multi-turn conversations."""
        # Mock services for service lookup scenarios
        mcp.register_mock_response(
            "list_services", lambda params: True, {
                "response": [
                    {"id": "SVC123", "name": "Web Service", "summary": "Main web application service"},
                    {"id": "SVC456", "name": "Database Service", "summary": "Primary database service"},
                    {"id": "SVC789", "name": "API Gateway", "summary": "API gateway service"}
                ]
            }
        )

        # Mock service lookup by name
        mcp.register_mock_response(
            "list_services",
            lambda params: params.get("query_model", {}).get("query") == "Web Service",
            {"response": [{"id": "SVC123", "name": "Web Service", "summary": "Main web application service"}]}
        )

        mcp.register_mock_response(
            "list_services",
            lambda params: params.get("query_model", {}).get("query") == "Database Service",
            {"response": [{"id": "SVC456", "name": "Database Service", "summary": "Primary database service"}]}
        )

        # Mock existing alert grouping settings for lookup scenarios
        mcp.register_mock_response(
            "list_alert_grouping_settings",
            lambda params: True,
            {
                "response": [
                    {
                        "id": "PAGS123",
                        "name": "Web Service Grouping",
                        "type": "content_based",
                        "description": "Groups alerts by summary for web service",
                        "services": [{"id": "SVC123", "summary": "Web Service"}]
                    },
                    {
                        "id": "PAGS456",
                        "name": "Database Alert Grouping",
                        "type": "intelligent",
                        "description": "Intelligent grouping for database alerts",
                        "services": [{"id": "SVC456", "summary": "Database Service"}]
                    }
                ]
            }
        )

        # Mock specific alert grouping setting lookup
        mcp.register_mock_response(
            "get_alert_grouping_setting",
            lambda params: params.get("setting_id") == "PAGS123",
            {
                "id": "PAGS123",
                "name": "Web Service Grouping",
                "type": "content_based",
                "description": "Groups alerts by summary for web service",
                "services": [{"id": "SVC123", "summary": "Web Service"}],
                "config": {
                    "aggregate": "any",
                    "fields": ["summary"],
                    "time_window": 3600
                }
            }
        )

        # Mock alert grouping settings filtered by service
        mcp.register_mock_response(
            "list_alert_grouping_settings",
            lambda params: params.get("query_model", {}).get("service_ids") == ["SVC123"],
            {
                "response": [
                    {
                        "id": "PAGS123",
                        "name": "Web Service Grouping",
                        "type": "content_based",
                        "services": [{"id": "SVC123", "summary": "Web Service"}]
                    }
                ]
            }
        )


# Define the competency test cases
ALERT_GROUPING_SETTINGS_COMPETENCY_TESTS = [
    # Basic listing operations
    AlertGroupingSettingsCompetencyTest(
        query="Show me all alert grouping settings",
        expected_tools=[
            {"tool_name": "list_alert_grouping_settings", "parameters": {"query_model": {}}}
        ],
        description="Basic alert grouping settings listing",
    ),

    AlertGroupingSettingsCompetencyTest(
        query="List alert grouping settings for service SVC123",
        expected_tools=[
            {
                "tool_name": "list_alert_grouping_settings",
                "parameters": {"query_model": {"service_ids": ["SVC123"]}}
            }
        ],
        description="List alert grouping settings filtered by service ID",
    ),

    # Get specific setting
    AlertGroupingSettingsCompetencyTest(
        query="Get details for alert grouping setting PAGS123",
        expected_tools=[
            {"tool_name": "get_alert_grouping_setting", "parameters": {"setting_id": "PAGS123"}}
        ],
        description="Get specific alert grouping setting by ID",
    ),

    # Create content-based alert grouping setting
    AlertGroupingSettingsCompetencyTest(
        query="Create a content-based alert grouping setting named 'API Alerts' that groups by summary and source fields with a 30-minute time window for service SVC789",
        expected_tools=[
            {
                "tool_name": "create_alert_grouping_setting",
                "parameters": {
                    "create_model": {
                        "alert_grouping_setting": {
                            "name": "API Alerts",
                            "type": "content_based",
                            "config": {
                                "aggregate": "any",
                                "fields": ["summary", "source"],
                                "time_window": 1800
                            },
                            "services": [{"id": "SVC789"}]
                        }
                    }
                }
            }
        ],
        description="Create content-based alert grouping setting with specific parameters",
    ),

    # Create time-based alert grouping setting
    AlertGroupingSettingsCompetencyTest(
        query="Create a time-based alert grouping setting with 10-minute timeout for service SVC456",
        expected_tools=[
            {
                "tool_name": "create_alert_grouping_setting",
                "parameters": {
                    "create_model": {
                        "alert_grouping_setting": {
                            "type": "time",
                            "config": {"timeout": 600},
                            "services": [{"id": "SVC456"}]
                        }
                    }
                }
            }
        ],
        description="Create time-based alert grouping setting",
    ),

    # Create intelligent alert grouping setting
    AlertGroupingSettingsCompetencyTest(
        query="Create an intelligent alert grouping setting with 20-minute time window for service SVC123",
        expected_tools=[
            {
                "tool_name": "create_alert_grouping_setting",
                "parameters": {
                    "create_model": {
                        "alert_grouping_setting": {
                            "type": "intelligent",
                            "config": {"time_window": 1200},
                            "services": [{"id": "SVC123"}]
                        }
                    }
                }
            }
        ],
        description="Create intelligent alert grouping setting",
    ),

    # Create content-based intelligent setting (single service only)
    AlertGroupingSettingsCompetencyTest(
        query="Create a content-based intelligent alert grouping setting that groups by summary field with 15-minute window for service SVC456",
        expected_tools=[
            {
                "tool_name": "create_alert_grouping_setting",
                "parameters": {
                    "create_model": {
                        "alert_grouping_setting": {
                            "type": "content_based_intelligent",
                            "config": {
                                "aggregate": "any",
                                "fields": ["summary"],
                                "time_window": 900
                            },
                            "services": [{"id": "SVC456"}]
                        }
                    }
                }
            }
        ],
        description="Create content-based intelligent alert grouping setting",
    ),

    # Update alert grouping setting
    AlertGroupingSettingsCompetencyTest(
        query="Update alert grouping setting PAGS123 to use a 2-hour time window",
        expected_tools=[
            {
                "tool_name": "update_alert_grouping_setting",
                "parameters": {
                    "setting_id": "PAGS123",
                    "update_model": {
                        "alert_grouping_setting": {
                            "type": "content_based",
                            "config": {"time_window": 7200},
                            "services": [{"id": "SVC123"}]
                        }
                    }
                }
            }
        ],
        description="Update existing alert grouping setting configuration",
    ),

    # Delete alert grouping setting
    AlertGroupingSettingsCompetencyTest(
        query="Delete alert grouping setting PAGS456",
        expected_tools=[
            {"tool_name": "delete_alert_grouping_setting", "parameters": {"setting_id": "PAGS456"}}
        ],
        description="Delete alert grouping setting by ID",
    ),

    # Multi-turn scenario: Create setting for named service (requires lookup)
    AlertGroupingSettingsCompetencyTest(
        query="Create a content-based alert grouping setting for the 'Web Service' that groups alerts by summary",
        expected_tools=[
            {
                "tool_name": "list_services",
                "parameters": {"query_model": {"query": "Web Service"}}
            },
            {
                "tool_name": "create_alert_grouping_setting",
                "parameters": {
                    "create_model": {
                        "alert_grouping_setting": {
                            "type": "content_based",
                            "config": {
                                "aggregate": "any",
                                "fields": ["summary"],
                                "time_window": 3600
                            },
                            "services": [{"id": "SVC123"}]
                        }
                    }
                }
            }
        ],
        description="Create alert grouping setting for named service (requires service lookup)",
    ),

    # Multi-turn scenario: List settings for named service
    AlertGroupingSettingsCompetencyTest(
        query="Show me all alert grouping settings for the 'Database Service'",
        expected_tools=[
            {
                "tool_name": "list_services",
                "parameters": {"query_model": {"query": "Database Service"}}
            },
            {
                "tool_name": "list_alert_grouping_settings",
                "parameters": {"query_model": {"service_ids": ["SVC456"]}}
            }
        ],
        description="List alert grouping settings for named service (requires service lookup)",
    ),

    # Pagination scenario
    AlertGroupingSettingsCompetencyTest(
        query="List the first 5 alert grouping settings",
        expected_tools=[
            {
                "tool_name": "list_alert_grouping_settings",
                "parameters": {"query_model": {"limit": 5}}
            }
        ],
        description="List alert grouping settings with pagination limit",
    ),

    # Complex content-based setting with all fields aggregation
    AlertGroupingSettingsCompetencyTest(
        query="Create a content-based alert grouping setting that requires ALL fields (summary, source, class) to match with 1-hour window for service SVC123",
        expected_tools=[
            {
                "tool_name": "create_alert_grouping_setting",
                "parameters": {
                    "create_model": {
                        "alert_grouping_setting": {
                            "type": "content_based",
                            "config": {
                                "aggregate": "all",
                                "fields": ["summary", "source", "class"],
                                "time_window": 3600
                            },
                            "services": [{"id": "SVC123"}]
                        }
                    }
                }
            }
        ],
        description="Create content-based setting with 'all' aggregation and multiple fields",
    ),

    # Create setting with name and description
    AlertGroupingSettingsCompetencyTest(
        query="Create an intelligent alert grouping setting named 'Smart DB Grouping' with description 'Intelligent grouping for database alerts' for service SVC456",
        expected_tools=[
            {
                "tool_name": "create_alert_grouping_setting",
                "parameters": {
                    "create_model": {
                        "alert_grouping_setting": {
                            "name": "Smart DB Grouping",
                            "description": "Intelligent grouping for database alerts",
                            "type": "intelligent",
                            "config": {"time_window": 3600},
                            "services": [{"id": "SVC456"}]
                        }
                    }
                }
            }
        ],
        description="Create intelligent alert grouping setting with name and description",
    ),
]