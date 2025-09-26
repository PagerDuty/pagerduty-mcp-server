from typing import ClassVar

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


class IntegrationReference(ReferenceBase):
    _type: ClassVar[str] = "integration_reference"
