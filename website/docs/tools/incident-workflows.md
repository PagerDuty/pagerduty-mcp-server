---
sidebar_position: 6
---

# Incident Workflows

Incident Workflows are automated sequences of actions that can be triggered during an incident. They help standardize response procedures and reduce manual steps.

## Tools

### `list_incident_workflows`

List incident workflows with optional filtering.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `IncidentWorkflowQuery` | No | Optional filtering parameters. If omitted, returns the first page with a default limit of 100 |

**Example prompt:**

> "What incident workflows are available in my account?"

---

### `get_incident_workflow`

Get a specific incident workflow.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | `string` | Yes | The ID of the incident workflow to retrieve |

---

### `start_incident_workflow` *(write)*

Start an incident workflow instance for a given incident.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | `string` | Yes | The ID of the workflow to start |
| `instance_request` | `IncidentWorkflowInstanceRequest` | Yes | The workflow instance request containing incident reference |

:::note
Requires `--enable-write-tools` flag.
:::

**Example prompt:**

> "Start the major incident response workflow for incident P123456"
