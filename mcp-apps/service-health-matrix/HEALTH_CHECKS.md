# PagerDuty Health Check Matrix

Updated Service Health Matrix to include comprehensive PagerDuty Health Checks organized by object type.

## 📊 Health Check Categories

Health checks are now organized by PagerDuty object type:

### 1. 🔧 **Services** (7 checks)
- **Transient Incidents**: Auto-resolved incidents < 10 minutes
- **Triggered Incident Count**: Current triggered incidents
- **Active Incident Count**: Current active (triggered + acknowledged) incidents
- **Acknowledged Incident Count**: Current acknowledged incidents
- **Acknowledged Incident %**: % acknowledged over last 90 days
- **Active Incident %**: % active over last 90 days
- **Triggered Incident %**: % triggered over last 90 days

### 2. 👥 **Teams** (13 checks)
- **Staggered Notifications %**: % responders with staggered high-urgency rules
- **Notification Rules %**: % responders with 3+ notification rules
- **Contact Methods %**: % responders with 3+ contact methods
- **Services with Transient Incidents %**: % of team services with transient incidents
- **Schedules with Inactive Users %**: % of team schedules with inactive users
- **Responders with Active Incidents**: % of team responders with multiple active incidents
- **Escalation Policies with Inactive Users %**: % of team EPs with inactive users
- **Escalation Policies > 1 Loop %**: % of team EPs with multiple loops
- **Escalation Policies >= 3 Layers %**: % of team EPs with 3+ layers
- **Service Active Incidents %**: % of team services with active incidents
- **Service Acknowledged Incidents %**: % of team services with acknowledged incidents
- **Service Triggered Incidents %**: % of team services with triggered incidents
- **User On Call %**: % of team users with excessive on-call assignments
- **Escalation Policies with Gaps %**: % of team EPs with coverage gaps

### 3. 🚨 **Escalation Policies** (6 checks)
- **Layers**: Should have 3 or more layers
- **Loops**: Should have more than 1 loop
- **Inactive Users**: Should have 0 inactive users
- **Service Association**: Should be associated with a service
- **Team Association**: Should be associated with a team
- **Coverage Gaps**: Should have 0 gaps in on-call coverage

### 4. 👤 **Users** (5 checks)
- **Contact Methods**: Should have 3+ contact methods (Phone, SMS, Email, Push, Slack)
- **Notification Rules**: Should have 3+ high-urgency notification rules
- **Staggered Notifications**: Should have staggered rules (>= 1 min delay)
- **Active Incidents**: Should have <= 1 active incident
- **On-Call Count**: Should be on-call for <= 3 areas simultaneously

### 5. 📅 **Schedules** (1 check)
- **Inactive Users**: Should have 0 inactive users

## 🎯 Severity Levels

- **Critical** 🔴 - Immediate action required (Red)
- **Major** 🟠 - Urgent attention needed (Orange)
- **High** 🟡 - Should be addressed soon (Yellow)
- **Medium** 🔵 - Recommended improvement (Blue)
- **Low** 🟢 - Minor observation (Green)

## 📁 File Structure

```
service-health-matrix/
├── server.ts                  # MCP server with health check data
├── health-checks.ts           # Health check definitions from CSV
├── src/
│   ├── mcp-app.tsx           # React UI (existing)
│   └── styles.css            # Styles (existing)
├── HEALTH_CHECKS.md          # This documentation
└── README.md                 # General app documentation
```

## 🔄 How It Works

### Server Side ([server.ts](server.ts:1))

1. **`generateMockHealthChecks(objectType)`**: Generates mock health check results for each object type
2. **Main Tool Response**:
   ```typescript
   {
     services: [{ id, name, teams, health_checks }],
     teams: [{ id, name, member_count, service_count, health_checks }],
     escalation_policies: [{ id, name, team, service_count, health_checks }],
     users: [{ id, name, role, teams, health_checks }],
     schedules: [{ id, name, team, user_count, health_checks }],
     metadata: { total_health_checks, passing, warning, failing }
   }
   ```

3. **Health Check Format**:
   ```typescript
   {
     id: string,              // e.g., "service-transient-incidents"
     status: 'pass' | 'warning' | 'fail',
     severity: 'critical' | 'major' | 'high' | 'medium' | 'low',
     current_value: string,   // Current measured value
     expected_value: string   // Target/expected value
   }
   ```

### Health Check Definitions ([health-checks.ts](health-checks.ts:1))

Contains the full catalog of 32 health checks with:
- Object type
- Rule name
- Urgency level
- Why it matters
- What it evaluates
- Expected values

Source: `/Users/svillanelo/Documents/GitHub/csg-sd-ai-workbench/Documentation/Solution_Gallery/HCs/KB HC Alerts - HC Alerts.csv`

## 🚀 Next Steps for Development

### Phase 1: Connect to Real PagerDuty Data
Replace mock data in `server.ts` with actual PagerDuty MCP tool calls:
```typescript
// Example: Fetch real services
const servicesResult = await app.callServerTool({
  name: "mcp__pagerduty-mcp-pdt-svillanelo__list_services",
  arguments: {}
});

// Example: Evaluate health check
const service = /* parsed from result */;
const transientPct = calculateTransientIncidents(service);
const check = {
  id: 'service-transient-incidents',
  status: transientPct < 5 ? 'pass' : 'fail',
  severity: getSeverity(transientPct),
  current_value: `${transientPct}%`,
  expected_value: '< 5%'
};
```

### Phase 2: Implement Health Check Logic
Create evaluation functions for each health check type:
- Count-based checks (incidents, users, layers)
- Percentage-based checks (transient %, responder readiness %)
- Boolean checks (associations, gaps)

### Phase 3: Update UI
The current UI displays service cards. Update to show:
- Object type tabs (Services, Teams, Users, EPs, Schedules)
- Health check status indicators
- Drill-down to show failing checks
- Filter by severity and status

### Phase 4: Add Actions
- Click health check → View details
- Quick fixes for common issues
- Export health report
- Schedule automated health assessments

## 📖 Reference

**Original Health Checks CSV**:
`/Users/svillanelo/Documents/GitHub/csg-sd-ai-workbench/Documentation/Solution_Gallery/HCs/KB HC Alerts - HC Alerts.csv`

**PagerDuty Health Check Documentation**: See CSV columns for:
- `why`: Business impact
- `what`: Technical evaluation
- `how_discovery`: Discovery method
- `how_analysis`: Analysis approach
- `how_alerting`: Alerting logic

## 🧪 Testing

Build and start the app:
```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/service-health-matrix
npm run build
node dist/main.js
```

The app runs on port **3003** by default.

Test via Claude Copilot Chat or direct tool call to `service-health-matrix`.
