"""Tests for service dependency competency questions."""

from .competency_test import CompetencyTest, MockedMCPServer


class ServiceDependencyCompetencyTest(CompetencyTest):
    """Competency tests for business and technical service dependency tools."""

    def register_mock_responses(self, mcp: MockedMCPServer) -> None:
        """Register minimal realistic responses to support multi-turn conversations."""
        mcp.register_mock_response(
            "list_business_services",
            lambda params: True,
            {
                "response": [
                    {"id": "BS123", "name": "Payment Processing", "type": "business_service"},
                    {"id": "BS456", "name": "Customer Portal", "type": "business_service"},
                    {"id": "BS789", "name": "Order Management", "type": "business_service"},
                ]
            },
        )
        mcp.register_mock_response(
            "get_business_service_dependencies",
            lambda params: True,
            {
                "relationships": [
                    {
                        "id": "DEP001",
                        "type": "service_dependency",
                        "supporting_service": {"id": "BS123", "type": "business_service_reference"},
                        "dependent_service": {"id": "BS789", "type": "business_service_reference"},
                    },
                    {
                        "id": "DEP002",
                        "type": "service_dependency",
                        "supporting_service": {"id": "SVC001", "type": "technical_service_reference"},
                        "dependent_service": {"id": "BS123", "type": "business_service_reference"},
                    },
                ]
            },
        )
        mcp.register_mock_response(
            "list_services",
            lambda params: True,
            {
                "response": [
                    {"id": "SVC001", "name": "Payments API", "status": "active"},
                    {"id": "SVC002", "name": "Auth Service", "status": "active"},
                    {"id": "SVC003", "name": "Database Service", "status": "active"},
                ]
            },
        )
        mcp.register_mock_response(
            "get_technical_service_dependencies",
            lambda params: True,
            {
                "relationships": [
                    {
                        "id": "DEP003",
                        "type": "service_dependency",
                        "supporting_service": {"id": "SVC001", "type": "technical_service_reference"},
                        "dependent_service": {"id": "BS123", "type": "business_service_reference"},
                    },
                    {
                        "id": "DEP004",
                        "type": "service_dependency",
                        "supporting_service": {"id": "SVC002", "type": "technical_service_reference"},
                        "dependent_service": {"id": "SVC001", "type": "technical_service_reference"},
                    },
                ]
            },
        )


SERVICES_COMPETENCY_TESTS = [
    # -------------------------------------------------------------------------
    # list_business_services
    # -------------------------------------------------------------------------
    ServiceDependencyCompetencyTest(
        query="Show me all business services",
        expected_tools=[{"tool_name": "list_business_services", "parameters": {}}],
        description="List all business services",
    ),
    ServiceDependencyCompetencyTest(
        query="List business services",
        expected_tools=[{"tool_name": "list_business_services", "parameters": {}}],
        description="List business services with simple query",
    ),
    ServiceDependencyCompetencyTest(
        query="What business services do we have configured in PagerDuty?",
        expected_tools=[{"tool_name": "list_business_services", "parameters": {}}],
        description="List business services using natural language",
    ),
    # -------------------------------------------------------------------------
    # get_business_service_dependencies
    # -------------------------------------------------------------------------
    ServiceDependencyCompetencyTest(
        query="Show me the dependencies for business service BS123",
        expected_tools=[
            {"tool_name": "get_business_service_dependencies", "parameters": {"business_service_id": "BS123"}}
        ],
        description="Get business service dependencies by ID",
    ),
    ServiceDependencyCompetencyTest(
        query="What services does business service BS456 depend on?",
        expected_tools=[
            {"tool_name": "get_business_service_dependencies", "parameters": {"business_service_id": "BS456"}}
        ],
        description="Get business service dependencies using natural language",
    ),
    ServiceDependencyCompetencyTest(
        query="Show me all service relationships for business service BS789",
        expected_tools=[
            {"tool_name": "get_business_service_dependencies", "parameters": {"business_service_id": "BS789"}}
        ],
        description="Get business service relationships",
    ),
    ServiceDependencyCompetencyTest(
        query="What is the blast radius if business service BS123 goes down?",
        expected_tools=[
            {"tool_name": "get_business_service_dependencies", "parameters": {"business_service_id": "BS123"}}
        ],
        allowed_helper_tools=["list_business_services"],
        description="Understand impact of business service outage using dependency lookup",
    ),
    ServiceDependencyCompetencyTest(
        query="What supports the Payment Processing business service?",
        expected_tools=[
            {"tool_name": "get_business_service_dependencies", "parameters": {}}
        ],
        allowed_helper_tools=["list_business_services"],
        description="Find supporting services for a named business service (requires lookup)",
    ),
    # -------------------------------------------------------------------------
    # get_technical_service_dependencies
    # -------------------------------------------------------------------------
    ServiceDependencyCompetencyTest(
        query="Show me the dependencies for technical service SVC001",
        expected_tools=[
            {"tool_name": "get_technical_service_dependencies", "parameters": {"service_id": "SVC001"}}
        ],
        description="Get technical service dependencies by ID",
    ),
    ServiceDependencyCompetencyTest(
        query="What does technical service SVC002 depend on?",
        expected_tools=[
            {"tool_name": "get_technical_service_dependencies", "parameters": {"service_id": "SVC002"}}
        ],
        description="Get technical service dependencies using natural language",
    ),
    ServiceDependencyCompetencyTest(
        query="Show me all service relationships for technical service SVC003",
        expected_tools=[
            {"tool_name": "get_technical_service_dependencies", "parameters": {"service_id": "SVC003"}}
        ],
        description="Get technical service relationships",
    ),
    ServiceDependencyCompetencyTest(
        query="Which services depend on technical service SVC001?",
        expected_tools=[
            {"tool_name": "get_technical_service_dependencies", "parameters": {"service_id": "SVC001"}}
        ],
        description="Find dependents of a technical service",
    ),
    ServiceDependencyCompetencyTest(
        query="What is the impact if the Payments API goes down?",
        expected_tools=[
            {"tool_name": "get_technical_service_dependencies", "parameters": {}}
        ],
        allowed_helper_tools=["list_services"],
        description="Understand impact of technical service outage (requires service lookup)",
    ),
]
