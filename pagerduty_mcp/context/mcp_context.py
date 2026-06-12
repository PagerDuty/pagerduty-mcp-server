import logging

from pagerduty.rest_api_v2_client import RestApiV2Client

from pagerduty_mcp.models.users import User


class MCPContext:
    """Container for request-scoped context data."""

    client: RestApiV2Client
    user: User | None = None

    def __init__(self, client: RestApiV2Client):
        self.client = client
        self.user = self._init_user()

    def _init_user(self) -> User | None:
        """Set the user associated with the client credentials."""
        try:
            response = self.client.rget("/users/me")
            if type(response) is not dict:
                logging.warning(f"Unexpected response type when initializing user: {type(response)}")
                return None

            user = User.model_validate(response)
            self.client.headers["From"] = user.email

            return user

        except Exception as e:  # noqa: BLE001
            logging.warning(f"Failed to initialize user: {e}")

        return None
