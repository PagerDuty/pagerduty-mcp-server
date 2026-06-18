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
from .analytics import (
    get_incident_metrics_all,
    get_incident_metrics_by_service,
    get_incident_metrics_by_team,
    get_responder_load_metrics,
    get_responder_metrics,
)
from .business_services import (
    get_business_service_dependencies,
    list_business_services,
)
from .priorities import list_priorities
from .change_events import (
    get_change_event,
    list_change_events,
    list_incident_change_events,
    list_service_change_events,
)

from .escalation_policies import (
    create_escalation_policy,
    get_escalation_policy,
    list_escalation_policies,
    update_escalation_policy,
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
from .schedules_v3 import (
    create_schedule_v3_custom_shifts,
    create_schedule_v3_overrides,
    create_schedule_v3_rotation,
    create_schedule_v3_rotation_event,
    delete_schedule_v3,
    delete_schedule_v3_custom_shift,
    delete_schedule_v3_override,
    delete_schedule_v3_rotation,
    delete_schedule_v3_rotation_event,
    get_schedule_v3_custom_shift,
    get_schedule_v3_override,
    get_schedule_v3_rotation,
    get_schedule_v3_rotation_event,
    list_schedule_v3_custom_shifts,
    list_schedule_v3_overrides,
    list_schedule_v3_rotation_events,
    list_schedule_v3_rotations,
    update_schedule_v3_custom_shift,
    update_schedule_v3_override,
    update_schedule_v3_rotation_event,
)
from .services import (
    create_service,
    get_service,
    get_technical_service_dependencies,
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
from .users import create_user, get_user_data, list_users
from .webhooks import (
    create_webhook_subscription,
    delete_webhook_subscription,
    get_extension_schema,
    get_webhook_subscription,
    list_extension_schemas,
    list_webhook_subscriptions,
    update_webhook_subscription,
)

# Read-only tools (safe, non-destructive operations)
read_tools = [
    # Alert Grouping Settings
    list_alert_grouping_settings,
    get_alert_grouping_setting,
    # Alerts
    list_alerts_from_incident,
    get_alert_from_incident,
    # Change Events
    list_change_events,
    get_change_event,
    list_service_change_events,
    list_incident_change_events,
    # Incidents
    list_incidents,
    get_incident,
    get_outlier_incident,
    get_past_incidents,
    get_related_incidents,
    list_incident_notes,
    # Incident Workflows
    list_incident_workflows,
    get_incident_workflow,
    # Services
    list_services,
    get_service,
    get_technical_service_dependencies,
    # Teams
    list_teams,
    get_team,
    list_team_members,
    # Users
    get_user_data,
    list_users,
    # Schedules (unified across layer-based v2 and shift-based v3)
    list_schedules,
    get_schedule,
    list_schedule_users,
    # Schedules (v3 sub-resources)
    list_schedule_v3_rotations,
    get_schedule_v3_rotation,
    list_schedule_v3_rotation_events,
    get_schedule_v3_rotation_event,
    list_schedule_v3_custom_shifts,
    get_schedule_v3_custom_shift,
    list_schedule_v3_overrides,
    get_schedule_v3_override,
    # On-calls
    list_oncalls,
    # Log Entries
    list_log_entries,
    get_log_entry,
    # Escalation Policies
    list_escalation_policies,
    get_escalation_policy,
    # Event Orchestrations
    list_event_orchestrations,
    get_event_orchestration,
    get_event_orchestration_router,
    get_event_orchestration_service,
    get_event_orchestration_global,
    # Status Pages
    list_status_pages,
    list_status_page_severities,
    list_status_page_impacts,
    list_status_page_statuses,
    get_status_page_post,
    list_status_page_post_updates,
    # Analytics
    get_responder_metrics,
    get_incident_metrics_by_service,
    get_incident_metrics_by_team,
    get_responder_load_metrics,
    get_incident_metrics_all,
    # Business Services
    list_business_services,
    get_business_service_dependencies,
    # Priorities
    list_priorities,
    # Webhooks
    list_webhook_subscriptions,
    get_webhook_subscription,
    # Extension Schemas
    list_extension_schemas,
    get_extension_schema,
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
    # Incident Workflows
    start_incident_workflow,
    # Services
    create_service,
    update_service,
    # Teams
    create_team,
    update_team,
    delete_team,
    add_team_member,
    remove_team_member,
    # Schedules (unified): create/update target shift-based (v3); overrides are layer-based (v2)
    create_schedule,
    update_schedule,
    create_schedule_override,
    # Schedules (v3 sub-resources)
    delete_schedule_v3,
    create_schedule_v3_rotation,
    delete_schedule_v3_rotation,
    create_schedule_v3_rotation_event,
    update_schedule_v3_rotation_event,
    delete_schedule_v3_rotation_event,
    create_schedule_v3_custom_shifts,
    update_schedule_v3_custom_shift,
    delete_schedule_v3_custom_shift,
    create_schedule_v3_overrides,
    update_schedule_v3_override,
    delete_schedule_v3_override,
    # Event Orchestrations
    update_event_orchestration_router,
    append_event_orchestration_router_rule,
    # Status Pages
    create_status_page_post,
    create_status_page_post_update,
    # Users
    create_user,
    # Escalation Policies
    create_escalation_policy,
    update_escalation_policy,
    # Webhooks
    create_webhook_subscription,
    update_webhook_subscription,
    delete_webhook_subscription,
]

# All tools (combined list for backward compatibility)
all_tools = read_tools + write_tools
