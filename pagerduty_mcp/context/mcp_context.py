import logging

from typing_extensions import Optional

from pagerduty.rest_api_v2_client import RestApiV2Client
from pagerduty_mcp.context.context_strategy import ContextData, ContextUser
from pagerduty_mcp.models.users import User


class MCPContext(ContextData):
    """Container for request-scoped context data."""

    client: RestApiV2Client
    user: Optional[ContextUser] = None

    @staticmethod
    def build_from_client(client: RestApiV2Client) -> "MCPContext":
        """Factory method to create an MCPContext from a RestApiV2Client."""
        user = MCPContext._init_user(client)
        if user:
            client.headers["From"] = user.email

        return MCPContext(client, user)

    @staticmethod
    def _init_user(client: RestApiV2Client) -> Optional[ContextUser]:
        """Set the user associated with the client credentials."""
        try:
            response = client.rget("/users/me")
            if type(response) is not dict:
                logging.warning(f"Unexpected response type when initializing user: {type(response)}")
                return None

            user = ContextUser.model_validate(response)
            return user

        except Exception as e:
            logging.warning(f"Failed to initialize user: {e}")

        return None

    def __init__(self, client: RestApiV2Client, user: Optional[ContextUser] = None):
        self.client = client
        self.user = user
