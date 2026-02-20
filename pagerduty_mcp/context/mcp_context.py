from typing_extensions import Optional

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.models.users import User


class MCPContext:
    """Container for request-scoped context data."""

    client: RestApiV2Client
    user: Optional[User] = None

    def __init__(self, client: RestApiV2Client):
        self.client = client
        self.user = self._init_user()

    def _init_user(self) -> Optional[User]:
        """Set the user associated with the client credentials."""
        response = self.client.rget("/users/me")
        if type(response) is dict:
            user_email = response.get("email", "no-email-provided")
            self.client.headers["From"] = user_email
            return User.model_validate(response)
        return None
