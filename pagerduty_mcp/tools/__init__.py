from .alert_grouping_settings import (
    create_alert_grouping_setting,
    delete_alert_grouping_setting,
    get_alert_grouping_setting,
    list_alert_grouping_settings,
    update_alert_grouping_setting,
)
from .chat_assistant_service_request import chat_assistant_service_request

# Currently disabled to prevent issues with the escalation policies domain
from .escalation_policies import (
    # create_escalation_policy,
    get_escalation_policy,
    # get_escalation_policy_on_call,
    # get_escalation_policy_services,
    list_escalation_policies,
)
from .incidents import (
    add_note_to_incident,
    add_responders,
    create_incident,
    get_incident,
    list_incidents,
    manage_incidents,
)
from .oncalls import list_oncalls
from .schedules import (
    create_schedule_override,
    get_schedule,
    list_schedule_users,
    list_schedules,
)
from .services import (
    create_service,
    get_service,
    list_services,
    update_service,
)
from .teams import (
    add_team_member,
    create_team,
    delete_team,
    get_team,
    list_team_members,
    list_teams,
    remove_team_member,
    update_team,
)
from .users import get_user_data, list_users

# Read tools (safe operations that only retrieve data)
read_tools = [
    # Prompt Gateway Tools (should be used first)
    # get_available_prompts,
    # validate_prompt_consultation,
    # User and basic info
    get_user_data,
    list_users,
    # Alert Grouping Settings
    list_alert_grouping_settings,
    get_alert_grouping_setting,
    # Incidents
    list_incidents,
    get_incident,
    # Services
    list_services,
    get_service,
    # Teams
    list_teams,
    get_team,
    list_team_members,
    # Schedules
    list_schedules,
    get_schedule,
    list_schedule_users,
    # On-calls
    list_oncalls,
    # Escalation Policies
    list_escalation_policies,
    get_escalation_policy,
]

# Write tools (potentially dangerous operations that modify state)
write_tools = [
    # Alert Grouping Settings
    create_alert_grouping_setting,
    update_alert_grouping_setting,
    delete_alert_grouping_setting,
    # Incidents
    create_incident,
    manage_incidents,
    add_responders,
    add_note_to_incident,
    # Services
    create_service,
    update_service,
    # Teams
    create_team,
    update_team,
    delete_team,
    add_team_member,
    remove_team_member,
    # Schedules
    create_schedule_override,
    # AI Chat
    chat_assistant_service_request,
    # Escalation Policies - currently disabled
    # create_escalation_policy,
]


# All tools (combined list for backward compatibility)
all_tools = read_tools + write_tools
