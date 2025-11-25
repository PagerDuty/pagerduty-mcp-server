# from pagerduty_mcp_evals.test_cases.test_alert_grouping_settings import (
#     ALERT_GROUPING_SETTINGS_COMPETENCY_TESTS,
# )
# from pagerduty_mcp_evals.test_cases.test_event_orchestrations import (
#     EVENT_ORCHESTRATIONS_COMPETENCY_TESTS,
# )
# from pagerduty_mcp_evals.test_cases.test_incident_workflows import (
#     INCIDENT_WORKFLOW_COMPETENCY_TESTS,
# )
from pagerduty_mcp_evals.test_cases.agent_competency_test import AgentCompetencyTest
from pagerduty_mcp_evals.test_cases.test_incidents import INCIDENT_COMPETENCY_TESTS

# from pagerduty_mcp_evals.test_cases.test_status_pages import (
#     STATUS_PAGES_COMPETENCY_TESTS,
# )
# from pagerduty_mcp_evals.test_cases.test_teams import TEAMS_COMPETENCY_TESTS

test_mapping = {
    # "alert-grouping-settings": ALERT_GROUPING_SETTINGS_COMPETENCY_TESTS,
    "incidents": INCIDENT_COMPETENCY_TESTS,
    # "incident-workflows": INCIDENT_WORKFLOW_COMPETENCY_TESTS,
    # "teams": TEAMS_COMPETENCY_TESTS,
    # "event-orchestrations": EVENT_ORCHESTRATIONS_COMPETENCY_TESTS,
    # "status-pages": STATUS_PAGES_COMPETENCY_TESTS,
    # "all": (
    #     INCIDENT_COMPETENCY_TESTS
    #     # + TEAMS_COMPETENCY_TESTS
    #     # # + ALERT_GROUPING_SETTINGS_COMPETENCY_TESTS
    #     # + EVENT_ORCHESTRATIONS_COMPETENCY_TESTS
    #     # + INCIDENT_WORKFLOW_COMPETENCY_TESTS
    #     # + STATUS_PAGES_COMPETENCY_TESTS
    # ),
}


class TestCasesBuilder:

    def create_test_cases(self) -> dict[str, list[AgentCompetencyTest]]:
        """Create and return a list of test cases for different agent competencies.

        Returns: dict[str, list[AgentCompetencyTest]]: A dictionary mapping domain names to lists of test cases.
        """
        return test_mapping
