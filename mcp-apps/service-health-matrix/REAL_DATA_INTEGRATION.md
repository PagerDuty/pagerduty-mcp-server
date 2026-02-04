# Integrating Real PagerDuty API Data

The Service Health Matrix currently uses **configurable mock data** for development and demonstration. Follow this guide to connect it to your real PagerDuty instance.

## Current Status: Mock Data

The app generates realistic mock data with configurable counts:
- **Services**: 20 (configurable via `MOCK_SERVICE_COUNT`)
- **Teams**: 10 (configurable via `MOCK_TEAM_COUNT`)
- **Users**: 15 (configurable via `MOCK_USER_COUNT`)
- **Escalation Policies**: 12 (configurable via `MOCK_EP_COUNT`)
- **Schedules**: 8 (configurable via `MOCK_SCHEDULE_COUNT`)

### Adjusting Mock Data

```bash
# Set environment variables before starting
MOCK_SERVICE_COUNT=50 \
MOCK_USER_COUNT=30 \
MOCK_TEAM_COUNT=15 \
node dist/main.js
```

## Option 1: HTTP API Integration (Recommended)

Add PagerDuty API client to fetch real data directly from the MCP app server.

### Steps:

1. **Install PagerDuty Client**
```bash
npm install @pagerduty/pdjs
```

2. **Update server.ts** to use real API calls:

```typescript
import { api } from '@pagerduty/pdjs';

// Initialize PagerDuty client
const pd = api({
  token: process.env.PAGERDUTY_USER_API_KEY,
  tokenType: 'bearer',
});

// Replace mock data with real API calls
async (_args: any): Promise<CallToolResult> => {
  try {
    // Fetch real data from PagerDuty API
    const [servicesResp, teamsResp, usersResp, epsResp, schedulesResp, incidentsResp] =
      await Promise.all([
        pd.get('/services', { params: { limit: 100 } }),
        pd.get('/teams', { params: { limit: 100 } }),
        pd.get('/users', { params: { limit: 100 } }),
        pd.get('/escalation_policies', { params: { limit: 100 } }),
        pd.get('/schedules', { params: { limit: 100 } }),
        pd.get('/incidents', { params: { statuses: ['triggered', 'acknowledged'], limit: 100 } }),
      ]);

    // Process real data and evaluate health checks
    const data = {
      services: processServices(servicesResp.data.services, incidentsResp.data.incidents),
      teams: processTeams(teamsResp.data.teams),
      escalation_policies: processEscalationPolicies(epsResp.data.escalation_policies),
      users: processUsers(usersResp.data.users),
      schedules: processSchedules(schedulesResp.data.schedules),
      metadata: calculateMetadata(),
    };

    return { content: [{ type: "text", text: JSON.stringify(data) }] };
  } catch (error) {
    console.error("Error fetching PagerDuty data:", error);
    throw error;
  }
}
```

3. **Implement Health Check Evaluation Functions**:

```typescript
function evaluateServiceHealthChecks(service: any, incidents: any[]): HealthCheck[] {
  const serviceIncidents = incidents.filter(inc => inc.service.id === service.id);
  const triggeredCount = serviceIncidents.filter(inc => inc.status === 'triggered').length;
  const acknowledgedCount = serviceIncidents.filter(inc => inc.status === 'acknowledged').length;

  return [
    {
      id: 'service-triggered-count',
      status: triggeredCount <= 1 ? 'pass' : triggeredCount <= 5 ? 'warning' : 'fail',
      severity: triggeredCount > 5 ? 'critical' : 'high',
      current_value: triggeredCount.toString(),
      expected_value: '<= 1',
    },
    {
      id: 'service-acknowledged-count',
      status: acknowledgedCount <= 1 ? 'pass' : acknowledgedCount <= 5 ? 'warning' : 'fail',
      severity: acknowledgedCount > 5 ? 'major' : 'high',
      current_value: acknowledgedCount.toString(),
      expected_value: '<= 1',
    },
    // Add more health checks...
  ];
}

function evaluateUserHealthChecks(user: any): HealthCheck[] {
  const contactMethods = user.contact_methods?.length || 0;
  const notificationRules = user.notification_rules?.filter((r: any) => r.urgency === 'high').length || 0;

  return [
    {
      id: 'user-contact-methods',
      status: contactMethods >= 3 ? 'pass' : contactMethods >= 2 ? 'warning' : 'fail',
      severity: contactMethods < 2 ? 'critical' : 'major',
      current_value: contactMethods.toString(),
      expected_value: '>= 3 contact methods',
    },
    {
      id: 'user-notification-rules',
      status: notificationRules >= 3 ? 'pass' : notificationRules >= 2 ? 'warning' : 'fail',
      severity: notificationRules < 2 ? 'major' : 'high',
      current_value: notificationRules.toString(),
      expected_value: '>= 3 notification rules',
    },
  ];
}
```

## Option 2: Use Parent MCP Server Tools

Since the MCP app runs inside the PagerDuty MCP server, another approach is to have the parent server provide pre-processed health check data.

### Steps:

1. **Create a new tool in the parent Python MCP server** (`pagerduty_mcp/tools/health_checks.py`):

```python
from pagerduty_mcp.models import MCPContext

def evaluate_health_checks(context: MCPContext) -> dict:
    """Evaluate all health checks for the PagerDuty instance"""

    client = context.client

    # Fetch all necessary data
    services = client.get('/services', params={'limit': 100})
    teams = client.get('/teams', params={'limit': 100})
    users = client.get('/users', params={'limit': 100})
    escalation_policies = client.get('/escalation_policies', params={'limit': 100})
    schedules = client.get('/schedules', params={'limit': 100})
    incidents = client.get('/incidents', params={'statuses': ['triggered', 'acknowledged']})

    # Evaluate health checks
    return {
        'services': [evaluate_service_health(svc, incidents) for svc in services],
        'teams': [evaluate_team_health(team) for team in teams],
        'users': [evaluate_user_health(user) for user in users],
        'escalation_policies': [evaluate_ep_health(ep) for ep in escalation_policies],
        'schedules': [evaluate_schedule_health(schedule) for schedule in schedules],
    }
```

2. **Register the tool** in `pagerduty_mcp/server.py`

3. **Update MCP app** to call parent tool (requires MCP client setup)

## Environment Variables

Add to your `.env` file:

```bash
# Required for API access
PAGERDUTY_USER_API_KEY=your_api_key_here
PAGERDUTY_API_HOST=https://api.pagerduty.com

# Optional: Configure mock data counts
MOCK_SERVICE_COUNT=20
MOCK_USER_COUNT=15
MOCK_TEAM_COUNT=10
MOCK_EP_COUNT=12
MOCK_SCHEDULE_COUNT=8
```

## Health Check Evaluation Logic

Reference the health check definitions in [health-checks.ts](./health-checks.ts) for the complete list of 32 health checks organized by object type.

### Key Health Check Examples:

**Services**:
- Transient incidents % (< 5%)
- Triggered incident count (<= 1)
- Active incident count (<= 1)

**Users**:
- Contact methods (>= 3)
- High-urgency notification rules (>= 3)
- Staggered notifications (>= 1 min delay)

**Teams**:
- Responder readiness % (>= 90%)
- EPs with 3+ layers % (> 75%)
- Services with transient incidents % (<= 10%)

**Escalation Policies**:
- Layers count (>= 3)
- Loop count (> 1)
- Inactive users (0)

## Testing

After implementing real data integration:

```bash
# Build
npm run build

# Start with real data
PAGERDUTY_USER_API_KEY=your_key node dist/main.js

# Test from VSCode Copilot Chat
# Call the service-health-matrix tool - it should now show your real services!
```

## Performance Considerations

- **Caching**: Implement caching for API responses (5-10 minute TTL)
- **Pagination**: Handle large datasets with proper pagination
- **Parallel Requests**: Use `Promise.all()` for concurrent API calls
- **Error Handling**: Graceful degradation if specific endpoints fail

## Next Steps

1. Choose integration approach (Option 1 recommended for independence)
2. Implement API client and health check evaluation logic
3. Test with your PagerDuty instance
4. Tune health check thresholds based on your organization's standards
5. Add caching layer for performance
