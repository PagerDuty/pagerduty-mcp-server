from pydantic import BaseModel, Field


class ClientMetadata(BaseModel):
    """Client metadata for chatbot requests."""

    client_type: str = Field(description="Type of client making the request")


class ChatAssistantServiceRequest(BaseModel):
    """Request model for PD Advance AI agent chatbot interactions."""

    message: str | None = Field(default=None, description="The message to AI agent")
    session_id: str | None = Field(
        default=None, description="Session ID for the conversation"
    )
    incident_id: str | None = Field(
        default=None, description="The incident ID associated with the request"
    )
    timestamp: str | None = Field(default=None, description="Timestamp of the request")
    client_metadata: ClientMetadata | None = Field(
        default=None, description="Client metadata for the request"
    )


class ChatAssistantServiceResponse(BaseModel):
    """Response model from PD Advance AI agent chatbot interactions."""

    message: str | None = Field(
        default=None, description="The AI agent's response message"
    )
    incident_id: str | None = Field(
        default=None, description="The incident ID associated with the response"
    )
    session_id: str | None = Field(
        default=None, description="Session ID for the conversation"
    )
    timestamp: str | None = Field(default=None, description="Timestamp of the request")
    tasks_used: list[str] | None = Field(
        default=None,
        description="List of tasks that were used to generate this response",
    )
    user_id: str | None = Field(
        default=None, description="The user ID who made the request"
    )
