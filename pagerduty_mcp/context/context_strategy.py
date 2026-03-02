from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Protocol

from pagerduty.rest_api_v2_client import RestApiV2Client

from pagerduty_mcp.models.users import User
from pydantic import BaseModel, Field, computed_field



class ContextUser(BaseModel):
    """Protocol for user objects used in context strategies."""

    id: str
    email: str


class ContextData(Protocol):
    """Protocol for context objects used by context strategies."""

    client: RestApiV2Client
    user: ContextUser | None


class ContextStrategy(Protocol):
    """Protocol for context management strategies."""

    @property
    def context(self) -> ContextData: ...

    def use_context(self, context: ContextData) -> AbstractContextManager[ContextData]: ...
