from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from pagerduty_mcp.models.references import IncidentReference, TeamReference


class IncidentWorkflowQuery(BaseModel):
    """Query parameters for listing incident workflows."""

    model_config = ConfigDict(extra="forbid")

    limit: int | None = Field(
        ge=1,
        le=100,
        default=100,
        description="Maximum number of results to return. The maximum is 100",
    )
    query: str | None = Field(
        description="Filters the result, showing only the records whose name matches the query",
        default=None,
    )
    include: list[Literal["steps", "team"]] | None = Field(
        description="Array of additional details to include",
        default=None,
    )

    def to_params(self) -> dict[str, Any]:
        """Convert to API query parameters."""
        params = {}
        if self.limit:
            params["limit"] = self.limit
        if self.query:
            params["query"] = self.query
        if self.include:
            params["include[]"] = self.include
        return params


class ActionInput(BaseModel):
    """Input configuration for an action."""

    name: str = Field(description="The name for this Input")
    parameter_type: str | None = Field(
        description="The data type of this Input",
        default=None,
    )
    value: str = Field(description="The configured value of the Input")


class ActionOutput(BaseModel):
    """Output configuration for an action."""

    name: str = Field(description="The name for this Output")
    reference_name: str = Field(description="The reference name of the Output")
    parameter_type: str = Field(description="The data type produced by this Output")


class InlineStepInput(BaseModel):
    """Inline step input for workflow-within-a-workflow."""

    name: str = Field(description="The name for this Input")
    value: dict[str, Any] = Field(description="The configured value of the Inline Steps Input")


class ActionConfiguration(BaseModel):
    """Configuration of automated action executed by a Step."""

    action_id: str = Field(description="The identifier of the Action to execute")
    description: str | None = Field(
        description="Description of the Action",
        default=None,
    )
    inputs: list[ActionInput] | None = Field(
        description="An unordered list of standard inputs used to configure the Action to execute",
        default=None,
    )
    inline_steps_inputs: list[InlineStepInput] | None = Field(
        description="An unordered list of specialized inputs used to configure a workflow-within-a-workflow",
        default=None,
    )
    outputs: list[ActionOutput] | None = Field(
        description="An unordered list of outputs this action produces",
        default=None,
    )


class Step(BaseModel):
    """A step in an incident workflow."""

    id: str | None = Field(description="Unique identifier for the step", default=None)
    name: str = Field(description="A descriptive name for the Step")
    description: str | None = Field(
        description="A description of the action performed by the Step",
        default=None,
    )
    action_configuration: ActionConfiguration = Field(
        description="Configuration of automated action executed by this Step"
    )
    summary: str | None = Field(
        description="A short-form, server-generated string",
        default=None,
    )
    self_: str | None = Field(
        alias="self",
        description="The API show URL at which the object is accessible",
        default=None,
    )
    html_url: str | None = Field(
        description="A URL at which the entity is uniquely displayed in the Web app",
        default=None,
    )

    @computed_field
    @property
    def type(self) -> Literal["step"]:
        return "step"


class IncidentWorkflow(BaseModel):
    """An incident workflow configuration."""

    id: str = Field(description="Unique identifier for the incident workflow")
    name: str = Field(description="A descriptive name for the Incident Workflow")
    description: str | None = Field(
        description="A description of what the Incident Workflow does",
        default=None,
    )
    created_at: datetime | None = Field(
        description="The timestamp this Incident Workflow was created",
        default=None,
    )
    team: TeamReference | None = Field(
        description="If specified then workflow edit permissions will be scoped to members of this team",
        default=None,
    )
    is_enabled: bool = Field(
        description="Indicates whether the Incident Workflow is enabled or not",
        default=True,
    )
    steps: list[Step] | None = Field(
        description="The ordered list of steps that execute sequentially as part of the workflow",
        default=None,
    )
    summary: str | None = Field(
        description="A short-form, server-generated string",
        default=None,
    )
    self_: str | None = Field(
        alias="self",
        description="The API show URL at which the object is accessible",
        default=None,
    )
    html_url: str | None = Field(
        description="A URL at which the entity is uniquely displayed in the Web app",
        default=None,
    )

    @computed_field
    @property
    def type(self) -> Literal["incident_workflow"]:
        return "incident_workflow"

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any]) -> "IncidentWorkflow":
        """Handle both wrapped and unwrapped API responses."""
        if "incident_workflow" in response_data:
            return cls.model_validate(response_data["incident_workflow"])
        return cls.model_validate(response_data)


class IncidentWorkflowInstanceCreate(BaseModel):
    """Request to start an incident workflow instance."""

    id: str | None = Field(
        description="An identifier to help differentiate between workflow executions",
        default=None,
    )
    incident: IncidentReference = Field(description="Reference to the incident")


class IncidentWorkflowInstanceRequest(BaseModel):
    """Wrapper for incident workflow instance creation request."""

    incident_workflow_instance: IncidentWorkflowInstanceCreate = Field(
        description="The incident workflow instance to create"
    )


class IncidentWorkflowInstance(BaseModel):
    """An incident workflow instance."""

    id: str = Field(description="Unique identifier for the incident workflow instance")
    incident: IncidentReference = Field(description="Reference to the incident")

    @computed_field
    @property
    def type(self) -> Literal["incident_workflow_instance"]:
        return "incident_workflow_instance"

    @classmethod
    def from_api_response(cls, response_data: dict[str, Any]) -> "IncidentWorkflowInstance":
        """Handle both wrapped and unwrapped API responses."""
        if "incident_workflow_instance" in response_data:
            return cls.model_validate(response_data["incident_workflow_instance"])
        return cls.model_validate(response_data)
