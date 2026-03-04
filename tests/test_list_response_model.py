"""Tests for ListResponseModel empty list type resolution (Issue #6)."""

import unittest

from pagerduty_mcp.models.base import MAX_RESULTS, ListResponseModel
from pagerduty_mcp.models.incidents import Incident
from pagerduty_mcp.models.services import Service
from pagerduty_mcp.models.teams import Team
from pagerduty_mcp.models.users import User


class TestListResponseModelEmptyList(unittest.TestCase):
    """Test that ListResponseModel resolves the correct type name when the list is empty."""

    def test_empty_incident_list_shows_incident_type(self):
        """Empty ListResponseModel[Incident] should show 'Incident', not 'Unknown'."""
        model = ListResponseModel[Incident](response=[])
        self.assertIn("Incident", model.response_summary)
        self.assertNotIn("Unknown", model.response_summary)
        self.assertIn("0 record(s)", model.response_summary)

    def test_empty_user_list_shows_user_type(self):
        """Empty ListResponseModel[User] should show 'User', not 'Unknown'."""
        model = ListResponseModel[User](response=[])
        self.assertIn("User", model.response_summary)
        self.assertNotIn("Unknown", model.response_summary)

    def test_empty_team_list_shows_team_type(self):
        """Empty ListResponseModel[Team] should show 'Team', not 'Unknown'."""
        model = ListResponseModel[Team](response=[])
        self.assertIn("Team", model.response_summary)
        self.assertNotIn("Unknown", model.response_summary)

    def test_empty_service_list_shows_service_type(self):
        """Empty ListResponseModel[Service] should show 'Service', not 'Unknown'."""
        model = ListResponseModel[Service](response=[])
        self.assertIn("Service", model.response_summary)
        self.assertNotIn("Unknown", model.response_summary)

    def test_non_empty_list_shows_correct_type(self):
        """Non-empty list should still resolve type from first element."""
        model = ListResponseModel[Team](response=[Team(name="Eng Team")])
        self.assertIn("Team", model.response_summary)
        self.assertIn("1 record(s)", model.response_summary)

    def test_max_results_warning(self):
        """When count equals MAX_RESULTS, a warning should be included."""
        teams = [Team(name=f"Team {i}") for i in range(MAX_RESULTS)]
        model = ListResponseModel[Team](response=teams)
        self.assertIn("WARNING", model.response_summary)
        self.assertIn("more records", model.response_summary)

    def test_below_max_results_no_warning(self):
        """When count is below MAX_RESULTS, no warning should appear."""
        model = ListResponseModel[Team](response=[Team(name="Eng")])
        self.assertNotIn("WARNING", model.response_summary)


if __name__ == "__main__":
    unittest.main()
