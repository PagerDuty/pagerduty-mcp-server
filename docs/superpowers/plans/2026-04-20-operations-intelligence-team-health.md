# Operations Intelligence — Team Health Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Team Health tab to Operations Intelligence that surfaces responder fatigue indicators (sleep/off-hour interruptions, engaged time, risk badges), plus a collapsible Percentile Distribution section (P50–P95) on the Operational tab.

**Architecture:** Expand three Python Pydantic models to expose fields the API already returns but models previously omitted. Add one new Python tool (`get_incident_metrics_all`) for the `/analytics/metrics/incidents/all` endpoint that returns percentiles. On the frontend, expand TypeScript types, add a 4th parallel API call, compute fatigue risk client-side, and render two new components.

**Tech Stack:** Python 3.12+, Pydantic v2, FastMCP, React 18, TypeScript, Vite, CSS variables

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `pagerduty_mcp/models/analytics.py` | Modify | Add ~11 fields to 3 models + new `AnalyticsAggregatedMetrics` + `GetIncidentMetricsAllRequest` |
| `pagerduty_mcp/tools/analytics.py` | Modify | Add `get_incident_metrics_all` tool function |
| `pagerduty_mcp/tools/__init__.py` | Modify | Export `get_incident_metrics_all` in `read_tools` list |
| `pagerduty_mcp/server.py` | Modify | Update docstring on `add_operations_intelligence` |
| `mcp-apps/operations-intelligence/src/api.ts` | Modify | Expand types, add 4th parallel call, `computeRisk` function |
| `mcp-apps/operations-intelligence/src/mock.ts` | Modify | Add new fields to mock data for `VITE_MOCK=true` dev mode |
| `mcp-apps/operations-intelligence/src/components/TeamHealth.tsx` | Create | Fatigue risk summary + responder burden table + team interruption table |
| `mcp-apps/operations-intelligence/src/components/PercentileSection.tsx` | Create | Collapsible P50–P95 row below KPI bar |
| `mcp-apps/operations-intelligence/src/mcp-app.tsx` | Modify | Add `teamHealth` tab, render new components |
| `mcp-apps/operations-intelligence/src/styles.css` | Modify | Risk badge colors, tinted row styles, collapsible section styles |

---

## Task 1: Expand Python Pydantic models with fatigue + percentile fields

**Files:**
- Modify: `pagerduty_mcp/models/analytics.py`

- [ ] **Step 1: Add interruption breakdown fields to `AnalyticsResponderLoad`**

Open `pagerduty_mcp/models/analytics.py`. The current `AnalyticsResponderLoad` class ends around line 270. Add these fields after `mean_time_to_acknowledge_seconds`:

```python
class AnalyticsResponderLoad(BaseModel):
    """Per-responder aggregate load metrics from PagerDuty Analytics."""

    responder_id: str | None = Field(default=None)
    responder_name: str | None = Field(default=None)
    team_id: str | None = Field(default=None)
    team_name: str | None = Field(default=None)

    total_seconds_on_call: int | None = Field(default=None)
    total_incident_count: int | None = Field(default=None)
    total_incidents_acknowledged: int | None = Field(default=None)
    total_sleep_hour_interruptions: int | None = Field(default=None)
    total_engaged_seconds: int | None = Field(default=None)
    mean_time_to_acknowledge_seconds: int | None = Field(default=None)
    # New fatigue fields
    total_interruptions: int | None = Field(default=None)
    total_business_hour_interruptions: int | None = Field(default=None)
    total_off_hour_interruptions: int | None = Field(default=None)
    mean_engaged_seconds: int | None = Field(default=None)
```

- [ ] **Step 2: Add interruption breakdown fields to `AnalyticsTeamMetrics`**

The current `AnalyticsTeamMetrics` class. Add new fields after `up_time_pct`:

```python
class AnalyticsTeamMetrics(BaseModel):
    """Per-team aggregate incident metrics from PagerDuty Analytics."""

    team_id: str | None = Field(default=None)
    team_name: str | None = Field(default=None)

    total_incident_count: int | None = Field(default=None)
    mean_seconds_to_first_ack: int | None = Field(default=None, description="Mean MTTA in seconds.")
    mean_seconds_to_resolve: int | None = Field(default=None, description="Mean MTTR in seconds.")
    total_escalation_count: int | None = Field(default=None)
    total_incidents_manual_escalated: int | None = Field(default=None)
    total_interruptions: int | None = Field(default=None)
    up_time_pct: float | None = Field(default=None)
    # New fatigue fields
    total_business_hour_interruptions: int | None = Field(default=None)
    total_off_hour_interruptions: int | None = Field(default=None)
    total_sleep_hour_interruptions: int | None = Field(default=None)
    mean_engaged_seconds: int | None = Field(default=None)
```

- [ ] **Step 3: Add urgency + engagement fields to `AnalyticsServiceMetrics`**

```python
class AnalyticsServiceMetrics(BaseModel):
    """Per-service aggregate incident metrics from PagerDuty Analytics."""

    service_id: str | None = Field(default=None)
    service_name: str | None = Field(default=None)
    team_id: str | None = Field(default=None)
    team_name: str | None = Field(default=None)

    total_incident_count: int | None = Field(default=None)
    mean_seconds_to_first_ack: int | None = Field(default=None, description="Mean MTTA in seconds.")
    mean_seconds_to_resolve: int | None = Field(default=None, description="Mean MTTR in seconds.")
    total_escalation_count: int | None = Field(default=None)
    total_incidents_manual_escalated: int | None = Field(default=None)
    total_interruptions: int | None = Field(default=None)
    up_time_pct: float | None = Field(default=None, description="Service availability percentage.")
    # New fields
    total_high_urgency_incident_count: int | None = Field(default=None)
    total_low_urgency_incident_count: int | None = Field(default=None)
    mean_engaged_seconds: int | None = Field(default=None)
```

- [ ] **Step 4: Add `AnalyticsAggregatedMetrics` and `GetIncidentMetricsAllRequest` models**

Append these two new classes at the end of `pagerduty_mcp/models/analytics.py`:

```python
class GetIncidentMetricsAllRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: AnalyticsIncidentFilters = Field(
        description="Date range and optional filters to scope the metrics."
    )
    time_zone: str | None = Field(
        default=None,
        description="The time zone for results (e.g. 'America/New_York').",
    )

    def to_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "filters": {
                "created_at_start": self.filters.created_at_start,
                "created_at_end": self.filters.created_at_end,
            }
        }
        if self.filters.team_ids:
            body["filters"]["team_ids"] = self.filters.team_ids
        if self.filters.service_ids:
            body["filters"]["service_ids"] = self.filters.service_ids
        if self.filters.urgency:
            body["filters"]["urgency"] = self.filters.urgency
        if self.time_zone:
            body["time_zone"] = self.time_zone
        return body


class AnalyticsAggregatedMetrics(BaseModel):
    """Full-period aggregated incident metrics from PagerDuty Analytics.

    Returned by /analytics/metrics/incidents/all. Only this endpoint
    provides percentile fields (P50–P95).
    """

    total_incident_count: int | None = Field(default=None)
    mean_seconds_to_first_ack: int | None = Field(default=None)
    mean_seconds_to_resolve: int | None = Field(default=None)
    p50_seconds_to_first_ack: int | None = Field(default=None)
    p75_seconds_to_first_ack: int | None = Field(default=None)
    p90_seconds_to_first_ack: int | None = Field(default=None)
    p95_seconds_to_first_ack: int | None = Field(default=None)
    p50_seconds_to_resolve: int | None = Field(default=None)
    p75_seconds_to_resolve: int | None = Field(default=None)
    p90_seconds_to_resolve: int | None = Field(default=None)
    p95_seconds_to_resolve: int | None = Field(default=None)
```

- [ ] **Step 5: Verify Python imports compile**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
python -c "from pagerduty_mcp.models.analytics import AnalyticsAggregatedMetrics, GetIncidentMetricsAllRequest, AnalyticsResponderLoad, AnalyticsTeamMetrics, AnalyticsServiceMetrics; print('OK')"
```

Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add pagerduty_mcp/models/analytics.py
git commit -m "feat(analytics): expand Pydantic models with fatigue fields and aggregated metrics"
```

---

## Task 2: Add `get_incident_metrics_all` Python tool

**Files:**
- Modify: `pagerduty_mcp/tools/analytics.py`
- Modify: `pagerduty_mcp/tools/__init__.py`

- [ ] **Step 1: Add the tool function to `pagerduty_mcp/tools/analytics.py`**

Add these two imports at the top of the file (update the existing import from `pagerduty_mcp.models.analytics`):

```python
from pagerduty_mcp.models.analytics import (
    AnalyticsResponderMetrics,
    AnalyticsServiceMetrics,
    AnalyticsTeamMetrics,
    AnalyticsResponderLoad,
    AnalyticsAggregatedMetrics,
    GetResponderMetricsRequest,
    GetIncidentMetricsByServiceRequest,
    GetIncidentMetricsByTeamRequest,
    GetResponderLoadMetricsRequest,
    GetIncidentMetricsAllRequest,
)
```

Then append this function at the end of `pagerduty_mcp/tools/analytics.py`:

```python
def get_incident_metrics_all(request: GetIncidentMetricsAllRequest) -> str:
    """Get full-period aggregated incident metrics from PagerDuty Analytics.

    Returns rollup metrics for the entire requested period including percentile
    distributions (P50, P75, P90, P95) for ack and resolve times. These percentile
    fields are ONLY available from this endpoint — not from the per-team or per-service
    grouped endpoints.

    Args:
        request: Filters (required date range, optional team/service/urgency filters)
                 and optional time zone.

    Returns:
        JSON string of AnalyticsAggregatedMetrics object.
    """
    body = request.to_body()
    response = get_client().rpost("/analytics/metrics/incidents/all", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", response)
    elif isinstance(response, list) and len(response) > 0:
        raw_data = response[0]
    else:
        raw_data = {}
    metrics = AnalyticsAggregatedMetrics(**raw_data) if raw_data else AnalyticsAggregatedMetrics()
    return metrics.model_dump_json()
```

- [ ] **Step 2: Export from `pagerduty_mcp/tools/__init__.py`**

In the import block at the top of `tools/__init__.py`, update the analytics import:

```python
from .analytics import (
    get_incident_metrics_by_service,
    get_incident_metrics_by_team,
    get_responder_load_metrics,
    get_responder_metrics,
    get_incident_metrics_all,
)
```

Then in the `read_tools` list (around line 153), add `get_incident_metrics_all` after `get_responder_metrics`:

```python
    # Analytics
    get_incident_metrics_by_service,
    get_incident_metrics_by_team,
    get_responder_load_metrics,
    get_responder_metrics,
    get_incident_metrics_all,
```

- [ ] **Step 3: Verify tool registers**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
python -c "from pagerduty_mcp.tools import read_tools; names = [t.__name__ for t in read_tools]; assert 'get_incident_metrics_all' in names, names; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add pagerduty_mcp/tools/analytics.py pagerduty_mcp/tools/__init__.py
git commit -m "feat(analytics): add get_incident_metrics_all tool for P50-P95 percentile data"
```

---

## Task 3: Expand TypeScript types and `fetchOpsData` in `src/api.ts`

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/api.ts`

- [ ] **Step 1: Add fatigue fields to `ResponderMetric` interface**

In `src/api.ts`, replace the existing `ResponderMetric` interface:

```typescript
export interface ResponderMetric {
  id: string;
  name: string;
  teamName: string | null;
  onCallHours: number;              // total_seconds_on_call / 3600
  totalIncidents: number;
  totalAcks: number;
  sleepInterruptions: number;
  engagedMinutes: number | null;    // total_engaged_seconds / 60
  // New fatigue fields
  totalInterruptions: number;
  businessHourInterruptions: number;
  offHourInterruptions: number;
  meanEngagedMinutes: number | null; // mean_engaged_seconds / 60
  riskLevel: "high" | "medium" | "low";
}
```

- [ ] **Step 2: Add fatigue fields to `TeamMetric` interface**

Replace the existing `TeamMetric` interface:

```typescript
export interface TeamMetric {
  id: string;
  name: string;
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrMinutes: number | null;
  escalationCount: number;
  totalInterruptions: number;
  uptimePct: number | null;
  // New fatigue fields
  businessHourInterruptions: number;
  offHourInterruptions: number;
  sleepHourInterruptions: number;
  meanEngagedMinutes: number | null;
}
```

- [ ] **Step 3: Add `AggregatedMetrics` interface and update `OpsData`**

After the `TeamMetric` interface, add:

```typescript
export interface AggregatedMetrics {
  p50AckSeconds: number | null;
  p75AckSeconds: number | null;
  p90AckSeconds: number | null;
  p95AckSeconds: number | null;
  p50ResolveSeconds: number | null;
  p75ResolveSeconds: number | null;
  p90ResolveSeconds: number | null;
  p95ResolveSeconds: number | null;
}
```

Then in `OpsData`, add:

```typescript
export interface OpsData {
  teams: Team[];
  selectedTeam: string | null;
  since: string;
  until: string;
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrMinutes: number | null;
  escalationRate: number | null;
  uptimePct: number | null;
  aggregated: AggregatedMetrics | null;  // ← new
  serviceMetrics: ServiceMetric[];
  teamMetrics: TeamMetric[];
  responderMetrics: ResponderMetric[];
}
```

- [ ] **Step 4: Add `computeRisk` function and fatigue constants**

After the `secToHours` helper function, add:

```typescript
const FATIGUE_SLEEP_HIGH = 5;
const FATIGUE_SLEEP_MED = 2;
const FATIGUE_ENGAGED_HIGH_MIN = 480;
const FATIGUE_ENGAGED_MED_MIN = 240;

function computeRisk(sleepInt: number, engagedMin: number | null): "high" | "medium" | "low" {
  if (sleepInt >= FATIGUE_SLEEP_HIGH || (engagedMin !== null && engagedMin >= FATIGUE_ENGAGED_HIGH_MIN)) {
    return "high";
  }
  if (sleepInt >= FATIGUE_SLEEP_MED || (engagedMin !== null && engagedMin >= FATIGUE_ENGAGED_MED_MIN)) {
    return "medium";
  }
  return "low";
}
```

- [ ] **Step 5: Add 4th parallel call in `fetchOpsData` and map new fields**

In `fetchOpsData`, replace the `Promise.allSettled` call to add the aggregated call:

```typescript
  const [teamsResult, serviceResult, teamResult, responderResult, aggregatedResult] = await Promise.allSettled([
    app.callServerTool({ name: "list_teams", arguments: { query_model: { limit: 100 } } }),
    app.callServerTool({
      name: "get_incident_metrics_by_service",
      arguments: { request: { filters: incidentFilters } },
    }),
    app.callServerTool({
      name: "get_incident_metrics_by_team",
      arguments: { request: { filters: incidentFilters } },
    }),
    app.callServerTool({
      name: "get_responder_load_metrics",
      arguments: { request: { filters: responderFilters } },
    }),
    app.callServerTool({
      name: "get_incident_metrics_all",
      arguments: { request: { filters: incidentFilters } },
    }),
  ]);
```

Then update the `teamMetrics` mapping to include new fields:

```typescript
  const teamMetrics: TeamMetric[] = (teamData?.response ?? []).map((t: any) => ({
    id: t.team_id ?? "",
    name: t.team_name ?? "Unknown",
    totalIncidents: t.total_incident_count ?? 0,
    mttaMinutes: secToMin(t.mean_seconds_to_first_ack),
    mttrMinutes: secToMin(t.mean_seconds_to_resolve),
    escalationCount: t.total_escalation_count ?? t.total_incidents_manual_escalated ?? 0,
    totalInterruptions: t.total_interruptions ?? 0,
    uptimePct: t.up_time_pct ?? null,
    businessHourInterruptions: t.total_business_hour_interruptions ?? 0,
    offHourInterruptions: t.total_off_hour_interruptions ?? 0,
    sleepHourInterruptions: t.total_sleep_hour_interruptions ?? 0,
    meanEngagedMinutes: secToMin(t.mean_engaged_seconds),
  }));
```

Update the `responderMetrics` mapping:

```typescript
  const responderMetrics: ResponderMetric[] = (respData?.response ?? []).map((r: any) => {
    const sleepInt = r.total_sleep_hour_interruptions ?? 0;
    const engMin = secToMin(r.total_engaged_seconds);
    return {
      id: r.responder_id ?? "",
      name: r.responder_name ?? "Unknown",
      teamName: r.team_name ?? null,
      onCallHours: secToHours(r.total_seconds_on_call),
      totalIncidents: r.total_incident_count ?? 0,
      totalAcks: r.total_incidents_acknowledged ?? 0,
      sleepInterruptions: sleepInt,
      engagedMinutes: secToMin(r.total_engaged_seconds),
      totalInterruptions: r.total_interruptions ?? 0,
      businessHourInterruptions: r.total_business_hour_interruptions ?? 0,
      offHourInterruptions: r.total_off_hour_interruptions ?? 0,
      meanEngagedMinutes: secToMin(r.mean_engaged_seconds),
      riskLevel: computeRisk(sleepInt, engMin),
    };
  });
```

Add aggregated metrics mapping after responderMetrics (before the KPI summary block):

```typescript
  // Aggregated percentiles
  const aggRaw = aggregatedResult.status === "fulfilled" ? extract<any>(aggregatedResult.value) : null;
  const aggregated: AggregatedMetrics | null = aggRaw ? {
    p50AckSeconds: aggRaw.p50_seconds_to_first_ack ?? null,
    p75AckSeconds: aggRaw.p75_seconds_to_first_ack ?? null,
    p90AckSeconds: aggRaw.p90_seconds_to_first_ack ?? null,
    p95AckSeconds: aggRaw.p95_seconds_to_first_ack ?? null,
    p50ResolveSeconds: aggRaw.p50_seconds_to_resolve ?? null,
    p75ResolveSeconds: aggRaw.p75_seconds_to_resolve ?? null,
    p90ResolveSeconds: aggRaw.p90_seconds_to_resolve ?? null,
    p95ResolveSeconds: aggRaw.p95_seconds_to_resolve ?? null,
  } : null;
```

Update the `return` statement to include `aggregated`:

```typescript
  return {
    teams,
    selectedTeam: teamId,
    since,
    until,
    totalIncidents,
    mttaMinutes: weightedAvg(teamMetrics, (t) => t.mttaMinutes),
    mttrMinutes: weightedAvg(teamMetrics, (t) => t.mttrMinutes),
    escalationRate: totalIncidents > 0 ? Math.round((totalEscalations / totalIncidents) * 100) : null,
    uptimePct,
    aggregated,
    serviceMetrics,
    teamMetrics,
    responderMetrics,
  };
```

- [ ] **Step 6: Verify TypeScript compiles**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors (or only pre-existing errors unrelated to these files)

- [ ] **Step 7: Commit**

```bash
git add mcp-apps/operations-intelligence/src/api.ts
git commit -m "feat(ops-intelligence): expand TypeScript types with fatigue fields and aggregated percentiles"
```

---

## Task 4: Update mock data for VITE_MOCK dev mode

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/mock.ts`

- [ ] **Step 1: Replace the entire mock file content**

Replace `mcp-apps/operations-intelligence/src/mock.ts` with:

```typescript
import type { OpsData } from "./api";

export const MOCK_OPS_DATA: OpsData = {
  teams: [
    { id: "T1", name: "Platform" },
    { id: "T2", name: "Backend" },
    { id: "T3", name: "Frontend" },
  ],
  selectedTeam: null,
  since: "2026-03-21T00:00:00.000Z",
  until: "2026-04-20T23:59:59.000Z",
  totalIncidents: 47,
  mttaMinutes: 8,
  mttrMinutes: 94,
  escalationRate: 12,
  uptimePct: 99.2,
  aggregated: {
    p50AckSeconds: 240,
    p75AckSeconds: 480,
    p90AckSeconds: 900,
    p95AckSeconds: 1800,
    p50ResolveSeconds: 3600,
    p75ResolveSeconds: 5400,
    p90ResolveSeconds: 9000,
    p95ResolveSeconds: 14400,
  },
  serviceMetrics: [
    { id: "S1", name: "api-gateway",         teamName: "Platform", totalIncidents: 12, mttaMinutes: 6,  mttrMinutes: 72,  escalationCount: 2, uptimePct: 99.5 },
    { id: "S2", name: "auth-service",        teamName: "Backend",  totalIncidents: 9,  mttaMinutes: 11, mttrMinutes: 140, escalationCount: 3, uptimePct: 98.9 },
    { id: "S3", name: "payment-processor",   teamName: "Backend",  totalIncidents: 15, mttaMinutes: 5,  mttrMinutes: 55,  escalationCount: 1, uptimePct: 99.8 },
    { id: "S4", name: "user-dashboard",      teamName: "Frontend", totalIncidents: 6,  mttaMinutes: 14, mttrMinutes: 180, escalationCount: 2, uptimePct: 97.3 },
    { id: "S5", name: "notification-worker", teamName: "Platform", totalIncidents: 5,  mttaMinutes: 9,  mttrMinutes: 60,  escalationCount: 0, uptimePct: 99.1 },
  ],
  teamMetrics: [
    { id: "T1", name: "Platform", totalIncidents: 17, mttaMinutes: 7,  mttrMinutes: 66,  escalationCount: 2, totalInterruptions: 8,  uptimePct: 99.3, businessHourInterruptions: 5, offHourInterruptions: 2, sleepHourInterruptions: 1, meanEngagedMinutes: 45 },
    { id: "T2", name: "Backend",  totalIncidents: 24, mttaMinutes: 9,  mttrMinutes: 107, escalationCount: 4, totalInterruptions: 15, uptimePct: 99.1, businessHourInterruptions: 7, offHourInterruptions: 4, sleepHourInterruptions: 4, meanEngagedMinutes: 82 },
    { id: "T3", name: "Frontend", totalIncidents: 6,  mttaMinutes: 14, mttrMinutes: 180, escalationCount: 0, totalInterruptions: 3,  uptimePct: 97.3, businessHourInterruptions: 2, offHourInterruptions: 1, sleepHourInterruptions: 0, meanEngagedMinutes: 38 },
  ],
  responderMetrics: [
    { id: "R1", name: "Alice Chen",   teamName: "Platform", onCallHours: 168, totalIncidents: 11, totalAcks: 10, sleepInterruptions: 2, engagedMinutes: 240, totalInterruptions: 5,  businessHourInterruptions: 2, offHourInterruptions: 1, meanEngagedMinutes: 22, riskLevel: "medium" },
    { id: "R2", name: "Bob Martinez", teamName: "Backend",  onCallHours: 120, totalIncidents: 14, totalAcks: 13, sleepInterruptions: 6, engagedMinutes: 510, totalInterruptions: 12, businessHourInterruptions: 4, offHourInterruptions: 2, meanEngagedMinutes: 36, riskLevel: "high" },
    { id: "R3", name: "Carol Park",   teamName: "Backend",  onCallHours: 96,  totalIncidents: 10, totalAcks: 9,  sleepInterruptions: 1, engagedMinutes: 210, totalInterruptions: 4,  businessHourInterruptions: 2, offHourInterruptions: 1, meanEngagedMinutes: 21, riskLevel: "low" },
    { id: "R4", name: "Dave Kim",     teamName: "Frontend", onCallHours: 72,  totalIncidents: 6,  totalAcks: 6,  sleepInterruptions: 0, engagedMinutes: 150, totalInterruptions: 2,  businessHourInterruptions: 2, offHourInterruptions: 0, meanEngagedMinutes: 25, riskLevel: "low" },
    { id: "R5", name: "Eve Johnson",  teamName: "Platform", onCallHours: 144, totalIncidents: 6,  totalAcks: 5,  sleepInterruptions: 3, engagedMinutes: 490, totalInterruptions: 6,  businessHourInterruptions: 2, offHourInterruptions: 1, meanEngagedMinutes: 82, riskLevel: "high" },
  ],
};

export const MOCK_INSIGHT_RESPONSES: Record<string, string> = {
  "MTTA & MTTR Trends": "MTTA improved 18% this period, averaging 8 min across all teams. MTTR remains elevated at 94 min driven by Backend (107 min). auth-service is the outlier at 140 min — a DB migration in week 2 caused a spike that inflated the mean. Platform shows the most consistent response times.",
  "Noisiest Services": "payment-processor led with 15 incidents but resolved fastest (55 min MTTR, 99.8% uptime) — high volume, low impact. auth-service (9 incidents, 140 min MTTR) poses the biggest risk: 3 escalations and sub-99% uptime. user-dashboard has the worst uptime at 97.3% despite only 6 incidents.",
  "Team & Responder Load": "Backend carries the highest load: 24 incidents, 15 interruptions, Bob Martinez with 6 sleep-hour interruptions. Platform is well-distributed. Frontend's low volume (6 incidents) suggests either strong reliability or under-alerting — worth validating coverage. Consider redistributing Backend on-call to reduce Bob's sleep interruption count.",
};
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
npx tsc --noEmit 2>&1 | head -20
```

Expected: no new errors

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/operations-intelligence/src/mock.ts
git commit -m "feat(ops-intelligence): update mock data with fatigue fields and aggregated percentiles"
```

---

## Task 5: Add CSS for risk badges, tinted rows, and collapsible section

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/styles.css`

- [ ] **Step 1: Add risk badge and tinted row styles**

Append to the end of `src/styles.css`:

```css
/* ── Risk badges (Team Health tab) ── */
.risk-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
  display: inline-block;
}

.risk-badge.risk-high {
  background: rgba(229, 62, 62, 0.12);
  color: #e53e3e;
}

.risk-badge.risk-medium {
  background: rgba(221, 107, 32, 0.12);
  color: #dd6b20;
}

.risk-badge.risk-low {
  background: rgba(56, 161, 105, 0.12);
  color: #38a169;
}

/* Row tinting by risk level */
.analytics-table tr.row-risk-high td {
  background: rgba(229, 62, 62, 0.04);
}

.analytics-table tr.row-risk-medium td {
  background: rgba(221, 107, 32, 0.04);
}

/* ── Fatigue KPI summary (Team Health) ── */
.fatigue-summary {
  display: flex;
  gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-primary);
  flex-wrap: wrap;
}

.fatigue-kpi-card {
  flex: 1;
  min-width: 110px;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
}

.fatigue-kpi-card.fatigue-high { border-left: 3px solid #e53e3e; }
.fatigue-kpi-card.fatigue-medium { border-left: 3px solid #dd6b20; }
.fatigue-kpi-card.fatigue-low { border-left: 3px solid #38a169; }

/* ── Percentile section (Operational tab) ── */
.percentile-section {
  border-bottom: 1px solid var(--border-primary);
}

.percentile-toggle {
  width: 100%;
  text-align: left;
  padding: 8px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.percentile-toggle:hover { color: var(--text-primary); background: var(--bg-secondary); }

.percentile-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr) repeat(4, 1fr);
  gap: 8px;
  padding: 8px 20px 12px;
}

.percentile-cell {
  padding: 8px 10px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 6px;
}

.percentile-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 2px;
}

.percentile-value {
  font-size: 15px;
  font-weight: 700;
  font-family: monospace;
}

/* Dark mode overrides for new elements */
:root[data-theme="dark"] .analytics-table tr.row-risk-high td {
  background: rgba(229, 62, 62, 0.08);
}

:root[data-theme="dark"] .analytics-table tr.row-risk-medium td {
  background: rgba(221, 107, 32, 0.08);
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/operations-intelligence/src/styles.css
git commit -m "feat(ops-intelligence): add CSS for risk badges, tinted rows, and percentile section"
```

---

## Task 6: Create `PercentileSection` component

**Files:**
- Create: `mcp-apps/operations-intelligence/src/components/PercentileSection.tsx`

- [ ] **Step 1: Create the component**

```typescript
import { useState } from "react";
import type { AggregatedMetrics } from "../api";

function fmtSec(seconds: number | null): string {
  if (seconds === null) return "—";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}m`;
}

interface PercentileCellProps {
  label: string;
  value: number | null;
}

function PercentileCell({ label, value }: PercentileCellProps) {
  return (
    <div className="percentile-cell">
      <div className="percentile-label">{label}</div>
      <div className="percentile-value">{fmtSec(value)}</div>
    </div>
  );
}

interface PercentileSectionProps {
  aggregated: AggregatedMetrics | null;
}

export function PercentileSection({ aggregated }: PercentileSectionProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="percentile-section">
      <button className="percentile-toggle" onClick={() => setOpen((o) => !o)}>
        <span>{open ? "▼" : "▶"}</span>
        Percentile Distribution
      </button>
      {open && (
        <div className="percentile-grid">
          <PercentileCell label="P50 Ack"     value={aggregated?.p50AckSeconds ?? null} />
          <PercentileCell label="P75 Ack"     value={aggregated?.p75AckSeconds ?? null} />
          <PercentileCell label="P90 Ack"     value={aggregated?.p90AckSeconds ?? null} />
          <PercentileCell label="P95 Ack"     value={aggregated?.p95AckSeconds ?? null} />
          <PercentileCell label="P50 Resolve" value={aggregated?.p50ResolveSeconds ?? null} />
          <PercentileCell label="P75 Resolve" value={aggregated?.p75ResolveSeconds ?? null} />
          <PercentileCell label="P90 Resolve" value={aggregated?.p90ResolveSeconds ?? null} />
          <PercentileCell label="P95 Resolve" value={aggregated?.p95ResolveSeconds ?? null} />
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
npx tsc --noEmit 2>&1 | head -20
```

Expected: no new errors

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/operations-intelligence/src/components/PercentileSection.tsx
git commit -m "feat(ops-intelligence): add PercentileSection collapsible component"
```

---

## Task 7: Create `TeamHealth` component

**Files:**
- Create: `mcp-apps/operations-intelligence/src/components/TeamHealth.tsx`

- [ ] **Step 1: Create the component**

```typescript
import { useState } from "react";
import type { ResponderMetric, TeamMetric } from "../api";
import { fmtMin } from "../utils";

type SortKey = "sleepInterruptions" | "offHourInterruptions" | "businessHourInterruptions" | "onCallHours" | "engagedMinutes" | "totalIncidents";

interface TeamHealthProps {
  metrics: ResponderMetric[];
  teamMetrics: TeamMetric[];
}

function RiskBadge({ level }: { level: "high" | "medium" | "low" }) {
  const labels = { high: "High", medium: "Medium", low: "Low" };
  return <span className={`risk-badge risk-${level}`}>{labels[level]}</span>;
}

export function TeamHealth({ metrics, teamMetrics }: TeamHealthProps) {
  const [sortKey, setSortKey] = useState<SortKey>("sleepInterruptions");

  const highCount = metrics.filter((r) => r.riskLevel === "high").length;
  const medCount = metrics.filter((r) => r.riskLevel === "medium").length;
  const lowCount = metrics.filter((r) => r.riskLevel === "low").length;
  const totalSleepInt = metrics.reduce((s, r) => s + r.sleepInterruptions, 0);

  const sorted = [...metrics].sort((a, b) => {
    if (sortKey === "engagedMinutes") {
      return (b.engagedMinutes ?? 0) - (a.engagedMinutes ?? 0);
    }
    return (b[sortKey] as number) - (a[sortKey] as number);
  });

  const sortedTeams = [...teamMetrics].sort(
    (a, b) => (b.businessHourInterruptions + b.offHourInterruptions + b.sleepHourInterruptions) -
               (a.businessHourInterruptions + a.offHourInterruptions + a.sleepHourInterruptions)
  );

  function ThSort({ col, label }: { col: SortKey; label: string }) {
    return (
      <th
        className={`col-num th-sortable${sortKey === col ? " th-active" : ""}`}
        onClick={() => setSortKey(col)}
      >
        {label}{sortKey === col ? " ↓" : ""}
      </th>
    );
  }

  return (
    <div className="body">
      {/* Fatigue risk summary */}
      <div className="fatigue-summary">
        <div className="fatigue-kpi-card fatigue-high">
          <div className="kpi-label">High Risk</div>
          <div className="kpi-value">{highCount}</div>
          <div className="kpi-sub">responders</div>
        </div>
        <div className="fatigue-kpi-card fatigue-medium">
          <div className="kpi-label">Medium Risk</div>
          <div className="kpi-value">{medCount}</div>
          <div className="kpi-sub">responders</div>
        </div>
        <div className="fatigue-kpi-card fatigue-low">
          <div className="kpi-label">Low Risk</div>
          <div className="kpi-value">{lowCount}</div>
          <div className="kpi-sub">responders</div>
        </div>
        <div className="fatigue-kpi-card">
          <div className="kpi-label">Sleep Interruptions</div>
          <div className="kpi-value">{totalSleepInt}</div>
          <div className="kpi-sub">total this period</div>
        </div>
      </div>

      {/* Responder burden table */}
      <div className="analytics-section">
        <div className="section-title">Responder Burden</div>
        {metrics.length === 0 ? (
          <div className="empty-state">No responder data for this period</div>
        ) : (
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Responder</th>
                <ThSort col="onCallHours"              label="On-Call Hrs" />
                <ThSort col="sleepInterruptions"       label="Sleep Int" />
                <ThSort col="offHourInterruptions"     label="Off-Hr Int" />
                <ThSort col="businessHourInterruptions" label="Business Int" />
                <ThSort col="engagedMinutes"           label="Engaged Time" />
                <ThSort col="totalIncidents"           label="Incidents" />
                <th className="col-num">Risk</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((r) => (
                <tr key={r.id} className={r.riskLevel !== "low" ? `row-risk-${r.riskLevel}` : ""}>
                  <td className="col-name">
                    {r.name}
                    {r.teamName && <span className="kpi-sub"> · {r.teamName}</span>}
                  </td>
                  <td className="col-num col-mono">{r.onCallHours}h</td>
                  <td className={`col-num${r.sleepInterruptions >= 5 ? " col-warn" : r.sleepInterruptions >= 2 ? "" : " col-ok"}`}>
                    {r.sleepInterruptions}
                  </td>
                  <td className="col-num">{r.offHourInterruptions}</td>
                  <td className="col-num">{r.businessHourInterruptions}</td>
                  <td className="col-num col-mono">{fmtMin(r.engagedMinutes)}</td>
                  <td className="col-num">{r.totalIncidents}</td>
                  <td className="col-num"><RiskBadge level={r.riskLevel} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Team interruption breakdown */}
      <div className="analytics-section">
        <div className="section-title">Team Interruption Breakdown</div>
        {teamMetrics.length === 0 ? (
          <div className="empty-state">No team data for this period</div>
        ) : (
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Team</th>
                <th className="col-num">Business Hrs</th>
                <th className="col-num">Off Hrs</th>
                <th className="col-num">Sleep Hrs</th>
                <th className="col-num">Total Int</th>
                <th className="col-num">Mean Engaged</th>
              </tr>
            </thead>
            <tbody>
              {sortedTeams.map((t) => (
                <tr key={t.id}>
                  <td className="col-name">{t.name}</td>
                  <td className="col-num">{t.businessHourInterruptions}</td>
                  <td className="col-num">{t.offHourInterruptions}</td>
                  <td className={`col-num${t.sleepHourInterruptions > 0 ? " col-warn" : " col-ok"}`}>
                    {t.sleepHourInterruptions}
                  </td>
                  <td className="col-num">{t.totalInterruptions}</td>
                  <td className="col-num col-mono">{fmtMin(t.meanEngagedMinutes)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
npx tsc --noEmit 2>&1 | head -20
```

Expected: no new errors

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/operations-intelligence/src/components/TeamHealth.tsx
git commit -m "feat(ops-intelligence): add TeamHealth component with fatigue risk summary and burden tables"
```

---

## Task 8: Wire up new tab and components in `mcp-app.tsx`

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/mcp-app.tsx`

- [ ] **Step 1: Add new imports**

At the top of `src/mcp-app.tsx`, add to the existing component imports:

```typescript
import { TeamHealth } from "./components/TeamHealth";
import { PercentileSection } from "./components/PercentileSection";
```

- [ ] **Step 2: Update the Tab type**

Replace:

```typescript
type Tab = "operational" | "insights";
```

With:

```typescript
type Tab = "operational" | "teamHealth" | "insights";
```

- [ ] **Step 3: Update the tab bar JSX**

Replace the existing `.tabs` div:

```tsx
      <div className="tabs">
        <button
          className={`tab-btn${tab === "operational" ? " tab-active" : ""}`}
          onClick={() => setTab("operational")}
        >
          Operational
        </button>
        <button
          className={`tab-btn${tab === "teamHealth" ? " tab-active" : ""}`}
          onClick={() => setTab("teamHealth")}
        >
          Team Health
        </button>
        <button
          className={`tab-btn${tab === "insights" ? " tab-active" : ""}`}
          onClick={() => setTab("insights")}
        >
          Insights
        </button>
      </div>
```

- [ ] **Step 4: Update the render body to add Team Health tab and PercentileSection**

Replace the conditional render block (the `loading && !data ? ... : tab === "operational" && data ? ...` section):

```tsx
      {loading && !data ? (
        <div className="loading">Loading operational data…</div>
      ) : tab === "operational" && data ? (
        <div className="body">
          <SummaryCards data={data} />
          <PercentileSection aggregated={data.aggregated} />
          <ServiceBreakdown metrics={data.serviceMetrics} />
          <TeamBreakdown metrics={data.teamMetrics} />
          <ResponderLoad metrics={data.responderMetrics} />
        </div>
      ) : tab === "teamHealth" && data ? (
        <TeamHealth metrics={data.responderMetrics} teamMetrics={data.teamMetrics} />
      ) : tab === "insights" && (app || mockMode) ? (
        <InsightsTab
          app={app ?? ({} as McpApp)}
          teamName={selectedTeamName}
          since={since}
          until={until}
          refreshKey={refreshKey}
        />
      ) : null}
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
npx tsc --noEmit 2>&1 | head -20
```

Expected: no errors

- [ ] **Step 6: Commit**

```bash
git add mcp-apps/operations-intelligence/src/mcp-app.tsx
git commit -m "feat(ops-intelligence): wire up Team Health tab and PercentileSection in main app"
```

---

## Task 9: Build and smoke-test with VITE_MOCK=true

**Files:**
- Build output: `mcp-apps/operations-intelligence/dist/mcp-app.html`

- [ ] **Step 1: Build the app**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
npm run build 2>&1 | tail -20
```

Expected: `dist/mcp-app.html` created with no errors

- [ ] **Step 2: Smoke-test with mock data**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
VITE_MOCK=true npm run dev &
sleep 3
npx playwright screenshot http://localhost:5173 /tmp/ops-intel-operational.png
npx playwright screenshot "http://localhost:5173" /tmp/ops-intel-operational.png --wait-for-timeout 2000
```

Open `/tmp/ops-intel-operational.png` and verify:
- KPI bar shows 5 metric cards
- "▶ Percentile Distribution" toggle is visible below KPI bar
- `Operational | Team Health | Insights` tabs are shown

- [ ] **Step 3: Test Team Health tab**

```bash
npx playwright open http://localhost:5173
```

Click **Team Health** tab and verify:
- Fatigue Risk Summary shows 4 KPI cards (High Risk: 2, Medium Risk: 1, Low Risk: 2, Sleep Interruptions: 12)
- Responder Burden table shows 5 rows sorted by Sleep Int desc (Bob 6, Eve 3, Alice 2, Carol 1, Dave 0)
- Bob and Eve rows have red tint; Alice row has orange tint
- Risk badges show: Bob → "High", Eve → "High", Alice → "Medium"
- Team Interruption Breakdown table shows 3 rows

- [ ] **Step 4: Test Percentile Distribution**

Click the **Operational** tab, then click **▶ Percentile Distribution**. Verify 8 cells appear: P50/P75/P90/P95 Ack and Resolve in minutes (4m, 8m, 15m, 30m, 1h, 1h 30m, 2h 30m, 4h).

- [ ] **Step 5: Kill dev server and commit build artifact**

```bash
kill %1 2>/dev/null || true
```

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
npm run build
git add mcp-apps/operations-intelligence/dist/ mcp-apps/operations-intelligence/package.json
git commit -m "build(ops-intelligence): rebuild with Team Health tab and percentile distribution"
```

---

## Task 10: Update server.py docstring

**Files:**
- Modify: `pagerduty_mcp/server.py`

- [ ] **Step 1: Update the `add_operations_intelligence` docstring**

In `server.py`, update the docstring of `add_operations_intelligence` to document the new tool and the three-tab structure:

```python
def add_operations_intelligence(mcp_instance: FastMCP) -> None:
    """Add Operations Intelligence Report MCP App resource.

    The UI calls these MCP tools:
    - get_incident_metrics_by_service (Analytics API — service-level MTTA/MTTR/escalations)
    - get_incident_metrics_by_team (Analytics API — team-level MTTA/MTTR/escalations/interruptions)
    - get_responder_load_metrics (Analytics API — responder on-call hours, interruptions, and fatigue)
    - get_incident_metrics_all (Analytics API — full-period rollup with P50/P75/P90/P95 percentiles)
    - list_teams (for team picker filter)
    - insights_agent_tool on pagerduty-advance-mcp (AI-powered insights tab)

    Args:
        mcp_instance: The MCP server instance
    """
```

Also update the tool description text in the `operations_intelligence()` function body:

```python
        return [
            TextContent(
                type="text",
                text="Operations Intelligence Report UI initialized. Three-tab dashboard: Operational (KPI bar + service/team/responder metrics), Team Health (responder fatigue indicators — sleep interruptions, off-hour load, risk badges), and Insights (AI-powered trend analysis via insights_agent_tool on pagerduty-advance-mcp)."
            )
        ]
```

- [ ] **Step 2: Commit**

```bash
git add pagerduty_mcp/server.py
git commit -m "docs(server): update operations_intelligence docstring for three-tab structure"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| Expand `AnalyticsResponderLoad` with interruption fields | Task 1 Step 1 |
| Expand `AnalyticsTeamMetrics` with interruption fields | Task 1 Step 2 |
| Expand `AnalyticsServiceMetrics` with urgency/engagement | Task 1 Step 3 |
| New `AnalyticsAggregatedMetrics` + `GetIncidentMetricsAllRequest` | Task 1 Step 4 |
| New `get_incident_metrics_all` Python tool | Task 2 Step 1 |
| Export tool in `read_tools` | Task 2 Step 2 |
| Expand `ResponderMetric` TS type | Task 3 Step 1 |
| Expand `TeamMetric` TS type | Task 3 Step 2 |
| `AggregatedMetrics` type + `OpsData.aggregated` | Task 3 Step 3 |
| `computeRisk` with named constants | Task 3 Step 4 |
| 4th parallel `get_incident_metrics_all` call | Task 3 Step 5 |
| Mock data with all new fields | Task 4 |
| CSS for risk badges, tinted rows, percentile section | Task 5 |
| `PercentileSection` collapsible component | Task 6 |
| `TeamHealth` component (3 sections) | Task 7 |
| 3-tab `mcp-app.tsx` with PercentileSection wired | Task 8 |
| Build + smoke test | Task 9 |
| `server.py` docstring update | Task 10 |
