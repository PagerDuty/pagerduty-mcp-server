# Operations Intelligence — Team Health Tab & Percentile Distribution

**Date:** 2026-04-20  
**Status:** Approved  
**Scope:** `mcp-apps/operations-intelligence/` + `pagerduty_mcp/models/analytics.py`

---

## Goal

Expand the Operations Intelligence MCP App to surface responder fatigue indicators as a first-class concern. The primary signal: **who is burning out?** — measured through sleep-hour interruptions, off-hour interruptions, on-call burden, and engaged time.

Secondary goal: add a collapsible Percentile Distribution section (P50/P75/P90/P95 ack & resolve) to the Operational tab's KPI bar.

---

## Changes Overview

### 1. Python model expansion (`pagerduty_mcp/models/analytics.py`)

The Pydantic models currently only capture a subset of the fields returned by the Analytics API. No tool logic changes are needed — Pydantic maps fields by name at construction time, so adding fields to models is sufficient.

**`AnalyticsResponderLoad`** — add:
- `total_interruptions: int | None`
- `total_business_hour_interruptions: int | None`
- `total_off_hour_interruptions: int | None`
- `total_sleep_hour_interruptions: int | None`
- `mean_engaged_seconds: int | None`
- `mean_time_to_acknowledge_seconds: int | None`

**`AnalyticsTeamMetrics`** — add:
- `total_interruptions: int | None`
- `total_business_hour_interruptions: int | None`
- `total_off_hour_interruptions: int | None`
- `total_sleep_hour_interruptions: int | None`
- `mean_engaged_seconds: int | None`

**`AnalyticsServiceMetrics`** — add:
- `total_high_urgency_incident_count: int | None`
- `total_low_urgency_incident_count: int | None`
- `mean_engaged_seconds: int | None`

### 2. New Python tool + aggregated metrics call (for percentiles)

The `/analytics/metrics/incidents/all` PagerDuty endpoint returns P50/P75/P90/P95 percentiles but has **no existing Python tool**. We must add:

- **New model `AnalyticsAggregatedMetrics`** in `analytics.py` with fields: `mean_seconds_to_first_ack`, `mean_seconds_to_resolve`, `p50_seconds_to_first_ack`, `p75_seconds_to_first_ack`, `p90_seconds_to_first_ack`, `p95_seconds_to_first_ack`, `p50_seconds_to_resolve`, `p75_seconds_to_resolve`, `p90_seconds_to_resolve`, `p95_seconds_to_resolve`, `total_incident_count`
- **New request model `GetIncidentMetricsAllRequest`** reusing `AnalyticsIncidentFilters`
- **New tool function `get_incident_metrics_all`** in `analytics.py` posting to `/analytics/metrics/incidents/all`
- **Register the tool** in `tools/__init__.py` and `server.py`

A 4th parallel `app.callServerTool` call is then added in `fetchOpsData` targeting `get_incident_metrics_all`. The result populates a new `AggregatedMetrics` type in `OpsData`.

> **Note:** Percentile metrics (P50–P95) are only available from the aggregated rollup endpoint (`/analytics/metrics/incidents/all`), not from per-team or per-service grouped endpoints.

### 3. TypeScript type expansions (`src/api.ts`)

**`ResponderMetric`** — add:
- `totalInterruptions: number`
- `businessHourInterruptions: number`
- `offHourInterruptions: number`
- `sleepInterruptions: number` (already exists, keep)
- `meanEngagedMinutes: number | null`
- `riskLevel: "high" | "medium" | "low"` (computed client-side)

**`TeamMetric`** — add:
- `businessHourInterruptions: number`
- `offHourInterruptions: number`
- `sleepHourInterruptions: number`
- `meanEngagedMinutes: number | null`

**New type `AggregatedMetrics`:**
```typescript
interface AggregatedMetrics {
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

**`OpsData`** — add `aggregated: AggregatedMetrics | null`

### 4. Risk badge computation

Computed in `api.ts` when mapping `AnalyticsResponderLoad` → `ResponderMetric`. Thresholds are named constants (not magic numbers):

```typescript
const FATIGUE_SLEEP_HIGH = 5;   // sleep interruptions in period
const FATIGUE_SLEEP_MED  = 2;
const FATIGUE_ENGAGED_HIGH_MIN = 480;  // 8 hours engaged
const FATIGUE_ENGAGED_MED_MIN  = 240;  // 4 hours engaged

function computeRisk(sleepInt: number, engagedMin: number | null): "high" | "medium" | "low"
```

### 5. New components

**`src/components/TeamHealth.tsx`**

Three sections rendered vertically:

1. **Fatigue Risk Summary (KPI cards row)**
   - High Risk responder count (🔴)
   - Medium Risk responder count (🟡)  
   - Low Risk responder count (🟢)
   - Total sleep interruptions across all responders

2. **Responder Burden Table** (sortable by any column, default sort: sleep interruptions desc)
   - Columns: Name | Team | On-Call Hrs | Sleep Int | Off-Hr Int | Business Int | Engaged Mins | Incidents | Risk
   - Row background tinted by risk level: red-tint / yellow-tint / none
   - Risk column: colored badge "High" / "Medium" / "Low"

3. **Team Interruption Breakdown Table**
   - Columns: Team | Business Hrs | Off Hrs | Sleep Hrs | Total Interruptions | Mean Engaged Mins
   - Sorted by Total Interruptions desc by default

**`src/components/PercentileSection.tsx`**

Collapsible row below the KPI bar on the Operational tab:
- Toggle "▶ Percentile Distribution" / "▼ Percentile Distribution"
- 8 cells: P50/P75/P90/P95 Ack, P50/P75/P90/P95 Resolve
- Displayed in minutes (converted from seconds)
- Shows `—` when data unavailable

### 6. Main app changes (`src/mcp-app.tsx`)

- Tab state: `"operational" | "teamHealth" | "insights"`
- Tab bar: `Operational | Team Health | Insights`
- Render `<TeamHealth metrics={data.responderMetrics} teamMetrics={data.teamMetrics} />` when `tab === "teamHealth"`
- Render `<PercentileSection aggregated={data.aggregated} />` inside the Operational tab body, below `<SummaryCards>`

### 7. Mock data (`src/mock.ts`)

Add all new fields to `MOCK_OPS_DATA` so `VITE_MOCK=true` dev mode works end-to-end without a live MCP server:
- `responderMetrics`: populate interruption breakdowns + risk levels
- `teamMetrics`: populate interruption breakdowns
- `aggregated`: populate with sample percentile values

---

## File Manifest

| File | Action |
|------|--------|
| `pagerduty_mcp/models/analytics.py` | Modify — add ~11 fields across 3 models + new `AnalyticsAggregatedMetrics` + `GetIncidentMetricsAllRequest` |
| `pagerduty_mcp/tools/analytics.py` | Modify — add `get_incident_metrics_all` tool function |
| `pagerduty_mcp/tools/__init__.py` | Modify — export `get_incident_metrics_all` |
| `pagerduty_mcp/server.py` | Modify — register `get_incident_metrics_all` tool |
| `mcp-apps/operations-intelligence/src/api.ts` | Modify — expand types, add 4th API call, compute risk |
| `mcp-apps/operations-intelligence/src/mcp-app.tsx` | Modify — add tab state + render new components |
| `mcp-apps/operations-intelligence/src/mock.ts` | Modify — add new fields to mock data |
| `mcp-apps/operations-intelligence/src/components/TeamHealth.tsx` | Create |
| `mcp-apps/operations-intelligence/src/components/PercentileSection.tsx` | Create |
| `mcp-apps/operations-intelligence/src/styles.css` | Modify — add risk badge colors, tinted row styles, collapsible styles |

---

## Out of Scope

- No changes to `server.ts`, `main.ts`, `vite.config.ts`
- No changes to existing Python tool functions (only additive: new `get_incident_metrics_all`)
- No changes to Insights tab
- No drill-down modals for individual responders (future)
- No threshold configuration UI (constants in code only)
