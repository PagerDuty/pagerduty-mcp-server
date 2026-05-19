# Currently disabled to prevent issues with the escalation policies domain
from .escalation_policies import (
    # create_escalation_policy,
    get_escalation_policy,
    # get_escalation_policy_on_call,
    # get_escalation_policy_services,
    list_escalation_policies,
)
from .incidents import (
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
from .schedules_v3 import (
    create_schedule_v3,
    get_schedule_v3,
    list_schedules_v3,
    update_schedule_v3,
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

# Read-only tools (safe, non-destructive operations)
read_tools = [
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
    # Users
    get_user_data,
    list_users,
    # Schedules (v2)
    list_schedules,
    get_schedule,
    list_schedule_users,
    # Schedules (v3)
    list_schedules_v3,
    get_schedule_v3,
    # On-calls
    list_oncalls,
    # Escalation Policies
    list_escalation_policies,
    get_escalation_policy,
]

# Write tools (potentially dangerous operations that modify state)
write_tools = [
    # Incidents
    create_incident,
    manage_incidents,
    add_responders,
    # Services
    create_service,
    update_service,
    # Teams
    create_team,
    update_team,
    delete_team,
    add_team_member,
    remove_team_member,
    # Schedules (v2)
    create_schedule_override,
    # Schedules (v3)
    create_schedule_v3,
    update_schedule_v3,
    # Escalation Policies - currently disabled
    # create_escalation_policy,
]

# All tools (combined list for backward compatibility)
all_tools = read_tools + write_tools
