from mcp.types import Prompt

pd_advance_ai_help = Prompt(
    name="pd_advance_ai_help",
    title="PagerDuty AI Agent Help",
    description="""Provide information about the PagerDuty AI Agent and its capabilities.

This prompt is designed to help users understand how to interact with the AI agent
and what kind of tasks it can assist with regarding incident management and resolution.
The AI agent can help with tasks such as generating runbooks, suggesting next steps for incident resolution,
recommending best practices for incident management, providing insights on incident trends and patterns,
and analyzing incident response effectiveness.

You are connected to the PagerDuty AI Agent.

You can use the `chatbot` tool to ask questions about incident resolution, incident management,
generating runbooks to aid incident in any way, including but not limited to:

- Generating a runbook for a specific incident
- Suggesting next steps for incident resolution
- Recommending best practices for incident management
- Providing insights on incident trends and patterns
- Analyzing incident response effectiveness

Examples:
- chatbot(message="Generate a runbook for incident ID <incident_id>", incident_id="<incident_id>")
- chatbot(message="What are the next steps to resolve incident ID <incident_id>?", incident_id="<incident_id>")
- chatbot(message="Provide best practices for managing incidents", incident_id="<incident_id>")
- chatbot(message="Analyze the incident response effectiveness for incident ID <incident_id>",
  incident_id="<incident_id>")

Make sure to always extract the incident ID from the user's request or ask the user to provide it if missing.""",
)
