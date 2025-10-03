"""Prompt Gateway Tool - Ensures prompts are consulted before tool execution."""

from typing import Any


def get_available_prompts() -> dict[str, str]:
    """Get a list of all available prompts and their descriptions.

    This tool should be called FIRST before executing any other tools
    to understand the proper context and approach for the user's request.

    Returns:
        Dict containing prompt names and their descriptions
    """
    return {
        "pd_advance_ai_help": """
        PagerDuty AI Agent Help - Provides guidance on using the AI agent for:
        - Generating runbooks for incidents
        - Suggesting incident resolution steps
        - Best practices for incident management
        - Incident trends and pattern analysis
        - Response effectiveness analysis

        Always use this prompt when dealing with incident-related AI assistance.
        """
    }


def validate_prompt_consultation(user_request: str, intended_tools: list[str]) -> dict[str, Any]:
    """Validate that appropriate prompts have been consulted for the user request.

    Args:
        user_request: The user's original request
        intended_tools: List of tools you plan to use

    Returns:
        Dict with validation results and recommendations
    """
    recommendations = []

    # Check if AI/chatbot tools are intended
    if any("chatbot" in tool.lower() or "ai" in tool.lower() for tool in intended_tools):
        recommendations.append(
            "REQUIRED: Consult 'pd_advance_ai_help' prompt first for AI agent guidance"
        )

    # Check for incident-related requests
    incident_keywords = ["incident", "runbook", "resolution", "troubleshoot"]
    if any(keyword in user_request.lower() for keyword in incident_keywords):
        recommendations.append(
            "RECOMMENDED: Review 'pd_advance_ai_help' prompt for incident management guidance"
        )

    return {
        "validation_status": "required_prompts_identified" if recommendations else "no_specific_prompts_required",
        "recommendations": recommendations,
        "next_steps": [
            "1. Review recommended prompts above",
            "2. Apply prompt guidance to your approach",
            "3. Proceed with tool execution following prompt instructions"
        ]
    }
