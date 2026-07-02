---
sidebar_position: 18
---

# Business Services

Business services represent high-level business capabilities that map to one or more technical services. They are useful for understanding service dependencies and the blast radius of incidents.

## Tools

### `list_business_services`

List all business services in the account.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| (none) | | | This tool takes no parameters |

**Example prompt:**

> "List all business services in our PagerDuty account"

---

### `get_business_service_dependencies`

Get the technical service dependencies for a business service. Returns the `relationships` array showing which technical services support this business service.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `business_service_id` | `string` | Yes | The ID of the business service |

**Example prompt:**

> "What technical services does the 'Checkout' business service depend on?"

---

> "Show me the dependency graph for business service PXXXXXX"
