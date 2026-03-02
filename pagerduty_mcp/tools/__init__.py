from .alert_grouping_settings import (
    create_alert_grouping_setting,
    delete_alert_grouping_setting,
    get_alert_grouping_setting,
    list_alert_grouping_settings,
    update_alert_grouping_setting,
)
from .alerts import (
    get_alert_from_incident,
    list_alerts_from_incident,
)
from .change_events import (
    get_change_event,
    list_change_events,
    list_incident_change_events,
    list_service_change_events,
)

# Currently disabled to prevent issues with the escalation policies domain
from .escalation_policies import (
    # create_escalation_policy,
    get_escalation_policy,
    # get_escalation_policy_on_call,
    # get_escalation_policy_services,
    list_escalation_policies,
)
from .event_orchestrations import (
    append_event_orchestration_router_rule,
    get_event_orchestration,
    get_event_orchestration_global,
    get_event_orchestration_router,
    get_event_orchestration_service,
    list_event_orchestrations,
    update_event_orchestration_router,
)
from .incident_workflows import (
    get_incident_workflow,
    list_incident_workflows,
    start_incident_workflow,
)
from .incidents import (
    add_note_to_incident,
    add_responders,
    create_incident,
    get_incident,
    get_outlier_incident,
    get_past_incidents,
    get_related_incidents,
    list_incident_notes,
    list_incidents,
    manage_incidents,
)
from .log_entries import (
    get_log_entry,
    list_log_entries,
)
from .oncalls import list_oncalls
from .schedules import (
    create_schedule,
    create_schedule_override,
    get_schedule,
    list_schedule_users,
    list_schedules,
    update_schedule,
)
from .services import (
    create_service,
    get_service,
    list_services,
    update_service,
)
from .status_pages import (
    create_status_page_post,
    create_status_page_post_update,
    get_status_page_post,
    list_status_page_impacts,
    list_status_page_post_updates,
    list_status_page_severities,
    list_status_page_statuses,
    list_status_pages,
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

# Tool categories mapping category name -> {"read": [...], "write": [...]}
TOOL_CATEGORIES: dict[str, dict[str, list]] = {
    "alert_grouping": {
        "read": [
            list_alert_grouping_settings,
            get_alert_grouping_setting,
        ],
        "write": [
            create_alert_grouping_setting,
            update_alert_grouping_setting,
            delete_alert_grouping_setting,
        ],
    },
    "alerts": {
        "read": [
            list_alerts_from_incident,
            get_alert_from_incident,
        ],
        "write": [],
    },
    "change_events": {
        "read": [
            list_change_events,
            get_change_event,
            list_service_change_events,
            list_incident_change_events,
        ],
        "write": [],
    },
    "escalation_policies": {
        "read": [
            list_escalation_policies,
            get_escalation_policy,
        ],
        "write": [
            # Escalation Policies - currently disabled
            # create_escalation_policy,
        ],
    },
    "event_orchestrations": {
        "read": [
            list_event_orchestrations,
            get_event_orchestration,
            get_event_orchestration_router,
            get_event_orchestration_service,
            get_event_orchestration_global,
        ],
        "write": [
            update_event_orchestration_router,
            append_event_orchestration_router_rule,
        ],
    },
    "incident_workflows": {
        "read": [
            list_incident_workflows,
            get_incident_workflow,
        ],
        "write": [
            start_incident_workflow,
        ],
    },
    "incidents": {
        "read": [
            list_incidents,
            get_incident,
            get_outlier_incident,
            get_past_incidents,
            get_related_incidents,
            list_incident_notes,
        ],
        "write": [
            create_incident,
            manage_incidents,
            add_responders,
            add_note_to_incident,
        ],
    },
    "log_entries": {
        "read": [
            list_log_entries,
            get_log_entry,
        ],
        "write": [],
    },
    "oncalls": {
        "read": [
            list_oncalls,
        ],
        "write": [],
    },
    "schedules": {
        "read": [
            list_schedules,
            get_schedule,
            list_schedule_users,
        ],
        "write": [
            create_schedule,
            create_schedule_override,
            update_schedule,
        ],
    },
    "services": {
        "read": [
            list_services,
            get_service,
        ],
        "write": [
            create_service,
            update_service,
        ],
    },
    "status_pages": {
        "read": [
            list_status_pages,
            list_status_page_severities,
            list_status_page_impacts,
            list_status_page_statuses,
            get_status_page_post,
            list_status_page_post_updates,
        ],
        "write": [
            create_status_page_post,
            create_status_page_post_update,
        ],
    },
    "teams": {
        "read": [
            list_teams,
            get_team,
            list_team_members,
        ],
        "write": [
            create_team,
            update_team,
            delete_team,
            add_team_member,
            remove_team_member,
        ],
    },
    "users": {
        "read": [
            get_user_data,
            list_users,
        ],
        "write": [],
    },
}

VALID_CATEGORIES: frozenset[str] = frozenset(TOOL_CATEGORIES.keys())

# Derive flat lists for backward compatibility
read_tools = [tool for cat in TOOL_CATEGORIES.values() for tool in cat["read"]]
write_tools = [tool for cat in TOOL_CATEGORIES.values() for tool in cat["write"]]
all_tools = read_tools + write_tools
