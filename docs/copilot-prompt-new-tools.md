# GitHub Copilot Prompt — New Tools Validation

Paste the block below into GitHub Copilot Chat (Agent mode, with the `pagerduty-mcp` MCP server connected).

---

```
Using the PagerDuty MCP tools, please do all of the following in order. For each step, show the tool name you called and a brief summary of what was returned.

## Analytics

1. Get responder metrics for the last 30 days (from 2025-05-01T00:00:00Z to 2025-05-31T23:59:59Z).
2. Get responder load metrics for the same date range.
3. Get incident metrics grouped by service from 2025-05-01T00:00:00Z to 2025-05-31T23:59:59Z.
4. Get incident metrics grouped by team for the same date range.
5. Get a full rollup of all incident metrics (get_incident_metrics_all) for 2025-05-01T00:00:00Z to 2025-05-31T23:59:59Z with aggregate_unit set to week.

## On-Call Compensation

6. Generate an on-call compensation report for 2025-05-01T00:00:00Z to 2025-05-31T23:59:59Z.

## Priorities

7. List all incident priorities defined in this PagerDuty account.

## Business Services

8. List all business services.
9. Pick the first business service from the list and get its business service dependencies.

## Services

10. List all services, pick the first one, and get its technical service dependencies.

## Log Entries

11. Pick any incident from the account and list its log entries using list_incident_log_entries.

## Schedules

12. List all schedules, pick the first one, and list its schedule overrides for 2025-05-01T00:00:00Z to 2025-05-31T23:59:59Z.

## Status Pages

13. List all status pages, pick the first one, and list its posts using list_status_page_posts.

---

For the write tools below, **do not execute them** — just describe what parameters you would pass based on what you found above.

14. create_incident_status_update — what incident and message would you use?
15. create_status_page_post_postmortem — what status page, post, and message would you use?
16. create_escalation_policy — what name, description, and escalation rules would you propose?
17. update_escalation_policy — which policy would you update and what would you change?
18. delete_escalation_policy — which policy (if any) looks safe to delete, and why?
19. delete_schedule_override — if there are overrides, which would be safe to delete?
20. create_user — what name, email, and role would you use for a test user?
```
