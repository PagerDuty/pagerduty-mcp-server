---
name: terraform-orchestration
description: "Convert PagerDuty AI Orchestration recommendations into Terraform HCL that fits the customer's existing code. Use when someone asks to add orchestration rules to their Terraform, or wants to export PagerDuty config as IaC."
user-invocable: true
argument-hint: "[service-name-or-id]"
---

# Terraform Orchestration Skill

Convert PagerDuty AI Orchestration recommendations into Terraform HCL that matches the customer's existing Terraform code structure.

## Prerequisites

Two MCP servers must be configured:

1. **PagerDuty MCP** — for reading current orchestration rules and services
```json
{
  "pagerduty-mcp": {
    "type": "http",
    "url": "https://mcp.pagerduty.com/mcp",
    "headers": {
      "Authorization": "Token token=<PD_API_KEY>"
    }
  }
}
```

2. **HashiCorp Terraform MCP** — for looking up PagerDuty provider resource schemas
```json
{
  "terraform-mcp": {
    "command": "npx",
    "args": ["-y", "@hashicorp/terraform-mcp-server"]
  }
}
```

## Workflow

### Step 1: Get the Orchestration Recommendation

1. Parse `$ARGUMENTS` for a service name or ID. If not provided, ask the user.
2. Use the PagerDuty MCP `list_services` tool to find the service if a name was given.
3. Use the PagerDuty MCP `get_event_orchestration_service` tool to read the current orchestration rules for that service.
4. Present the current rules to the user and ask: "What rule would you like to add or change?"
   - If the user says "show me recommendations" or "what does AI Orchestrations suggest", use the PagerDuty MCP to fetch any available AI-generated recommendations for the service.

### Step 2: Understand the Customer's Terraform Structure

1. Search for existing PagerDuty Terraform files:
   - Glob for `**/*.tf` files
   - Grep for `pagerduty_event_orchestration` in those files
   - Also check for `pagerduty_service`, `pagerduty_escalation_policy` to understand their naming conventions
2. Read the relevant `.tf` files to understand:
   - How they name resources (e.g., `pagerduty_event_orchestration_service.checkout_api`)
   - Whether they use variables, locals, or hardcoded values
   - Their formatting style (indentation, comment patterns)
   - Whether orchestration rules are in a dedicated file or mixed with service definitions
   - Whether they use `dynamic` blocks or static `rule` blocks

### Step 3: Look Up the Terraform Schema

1. Use the HashiCorp Terraform MCP `resolveResourceSchema` tool (or equivalent) to get the exact schema for the relevant resource:
   - `pagerduty_event_orchestration_service` — for service-level rules
   - `pagerduty_event_orchestration_router` — for routing rules
   - `pagerduty_event_orchestration_global` — for global rules
2. This ensures the generated HCL uses correct attribute names and nesting.

### Step 4: Generate the Terraform HCL

1. Convert the PagerDuty recommendation into a Terraform `rule` block that:
   - Matches the customer's existing code conventions
   - Uses the correct resource type and attribute names from the schema
   - References existing Terraform resources/variables where appropriate (e.g., `pagerduty_service.checkout_api.id` instead of hardcoded IDs)
   - Includes comments explaining what the rule does
2. Present the generated HCL to the user as a diff against their existing file.
3. Ask for confirmation before writing.

### Step 5: Write and Validate

1. After user approval, write the HCL to the appropriate `.tf` file using Edit.
2. Run `terraform fmt` to ensure consistent formatting.
3. Run `terraform validate` to check for syntax errors.
4. Suggest the user run `terraform plan` to review the full change before applying.

## Example Interaction

```
User: /terraform-orchestration checkout-api

Claude: Reading event orchestration rules for "Checkout API" service...
        Found 3 existing rules. AI Orchestrations suggests adding a noise
        reduction rule for database timeout alerts.

        Here is the Terraform HCL to add to orchestration.tf:

        + resource "pagerduty_event_orchestration_service" "checkout_api" {
        +   # ... existing rules ...
        +   rule {
        +     label = "Suppress DB timeout noise (AI recommendation)"
        +     condition {
        +       expression = "event.summary matches 'database timeout'"
        +     }
        +     actions {
        +       suppress = true
        +     }
        +   }
        + }

        Shall I write this to orchestration.tf?
```
