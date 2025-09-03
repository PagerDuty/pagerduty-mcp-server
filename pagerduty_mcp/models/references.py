from typing import Any, ClassVar

from pydantic import BaseModel, Field, computed_field


class ReferenceBase(BaseModel):
    id: str = Field(description="The ID of the referenced object")
    summary: str | None = Field(
        default=None,
        description="A short-form, server-generated string that provides succinct information about the"
        " referenced object",
    )

    _type: ClassVar[str]

    @computed_field
    @property
    def type(self) -> str:
        return self._type


class UserReference(ReferenceBase):
    _type: ClassVar[str] = "user_reference"


class ScheduleReference(ReferenceBase):
    _type: ClassVar[str] = "schedule_reference"


class TeamReference(ReferenceBase):
    _type: ClassVar[str] = "team_reference"


class IncidentReference(ReferenceBase):
    _type: ClassVar[str] = "incident_reference"


class ServiceReference(ReferenceBase):
    _type: ClassVar[str] = "service_reference"

class ChannelReference(BaseModel):
    type: str | None = Field(
        default=None,
        description="The type of the channel (e.g., email, sms, push)"
    )
    summary: str | None = Field(
        default=None,
        description="Summary of the log entry."
    )
    body: str | None = Field(
        default=None,
        description="The raw body of the log entry",
    )
    body_content_type: str | None = Field(
        default=None,
        description="The content type of the body (e.g., text/plain, text/html)"
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional details about the log entry",
    )
    html_url: str | None = Field(
        default=None,
        description="The URL of the log entry in the PagerDuty web UI",
    )
