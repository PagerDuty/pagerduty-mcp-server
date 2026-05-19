---
sidebar_position: 16
---

# Business Services

Business services represent the customer-facing capabilities your technical services support. These tools let you list business services and explore their dependencies on technical services.

## Tools

### `list_business_services`

List all business services in the account with optional pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query_model` | `BusinessServiceQuery` | No | Optional query parameters: `limit` (default 25, max 100) |

**Example prompts:**

> "List all business services"

> "Show me all the business services in PagerDuty"

---

### `get_business_service_dependencies`

Get the technical service dependencies for a specific business service. Returns all service relationships where this business service is either the dependent or supporting service.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `business_service_id` | `string` | Yes | The ID of the business service |

**Example prompts:**

> "What technical services support the Payments business service?"

> "Show dependencies for business service PXXXXXX"
