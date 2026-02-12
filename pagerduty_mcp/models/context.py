from pydantic import BaseModel, ConfigDict
from pagerduty.rest_api_v2_client import RestApiV2Client

from pagerduty_mcp.models.users import User


class MCPContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: RestApiV2Client
    user: User | None
