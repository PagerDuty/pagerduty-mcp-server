---
sidebar_position: 17
---

# Priorities

Priority tools let you retrieve the priority levels configured in your PagerDuty account. Priorities are used to classify incident severity.

## Tools

### `list_priorities`

List all priorities configured in the account. Returns the full set of priority levels including their names, descriptions, and IDs — useful for resolving a priority name to an ID before creating or updating incidents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| *(none)* | — | — | No parameters required |

**Example prompts:**

> "List all available incident priorities"

> "What priority levels are configured in PagerDuty?"
