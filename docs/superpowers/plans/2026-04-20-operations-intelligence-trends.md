# Operations Intelligence — Trends Tab & Logo Standardization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the broken Insights tab with a working Trends tab that renders time-series charts (incident volume, MTTA, MTTR per week) from real PagerDuty Analytics data; also update the PagerDuty logo across all MCP apps that use an inline SVG placeholder to use the official `pagerduty-icon.svg` asset.

**Architecture:** The Analytics API's team endpoint (`/analytics/metrics/incidents/teams`) accepts `aggregate_unit: "week"` which returns one row per team per week instead of an all-period aggregate. We call this in a 6th parallel fetch and store it as `TrendPoint[]` in `OpsData`. The Trends tab renders three pure-SVG charts (no chart library needed): incident volume bar chart, MTTA line chart, MTTR line chart. Each chart is a small responsive `<svg>` with hardcoded viewBox. Charts are rendered in TypeScript/React with zero external dependencies.

**Tech Stack:** React 18, TypeScript, Vite single-file build, PagerDuty Analytics API

---

## File Manifest

| File | Action |
|------|--------|
| `pagerduty_mcp/models/analytics.py` | Modify — add `aggregate_unit` to `GetIncidentMetricsByTeamRequest` |
| `mcp-apps/operations-intelligence/src/api.ts` | Modify — add `TrendPoint`, `TrendsData` types; add 6th fetch; remove `fetchInsight`; remove `InsightMessage` |
| `mcp-apps/operations-intelligence/src/mock.ts` | Modify — add `trendsData` to `MOCK_OPS_DATA`; remove `MOCK_INSIGHT_RESPONSES` |
| `mcp-apps/operations-intelligence/src/components/TrendsTab.tsx` | Create — three SVG charts |
| `mcp-apps/operations-intelligence/src/components/InsightCard.tsx` | Delete |
| `mcp-apps/operations-intelligence/src/components/InsightsChat.tsx` | Delete |
| `mcp-apps/operations-intelligence/src/components/InsightsTab.tsx` | Delete |
| `mcp-apps/operations-intelligence/src/mcp-app.tsx` | Modify — swap Insights tab for Trends tab |
| `mcp-apps/operations-intelligence/src/styles.css` | Modify — add chart styles; remove insight/chat styles |
| `mcp-apps/operations-intelligence/src/assets/pagerduty-icon.svg` | Create — copy from incident-command-center |
| `mcp-apps/operations-intelligence/src/components/PagerDutyLogo.tsx` | Modify — use SVG asset |
| `mcp-apps/post-mortem-builder/src/assets/pagerduty-icon.svg` | Create |
| `mcp-apps/post-mortem-builder/src/components/PagerDutyLogo.tsx` | Modify |
| `mcp-apps/shift-coverage-wizard/src/assets/pagerduty-icon.svg` | Create |
| `mcp-apps/shift-coverage-wizard/src/components/PagerDutyLogo.tsx` | Modify |

---

## Task 1: Add `aggregate_unit` to Python analytics request model

**Files:**
- Modify: `pagerduty_mcp/models/analytics.py`

The `GetIncidentMetricsByTeamRequest` model needs an `aggregate_unit` field so the UI can request weekly time-series data. The API accepts `"day"`, `"week"`, or `"month"` (nullable).

- [ ] **Step 1: Add `aggregate_unit` to `GetIncidentMetricsByTeamRequest`**

In `pagerduty_mcp/models/analytics.py`, find `GetIncidentMetricsByTeamRequest` (around line 185) and add the field after `order_by`:

```python
class GetIncidentMetricsByTeamRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: AnalyticsIncidentFilters = Field(
        description="Date range and optional filters to scope the metrics."
    )
    time_zone: str | None = Field(
        default=None,
        description="The time zone for results (e.g. 'America/New_York').",
    )
    order: str | None = Field(default=None, description="Sort order: 'asc' or 'desc'.")
    order_by: str | None = Field(default=None, description="Field to sort results by.")
    aggregate_unit: str | None = Field(
        default=None,
        description="Time unit to aggregate metrics by: 'day', 'week', or 'month'. If omitted, returns a single all-period row.",
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
        if self.order:
            body["order"] = self.order
        if self.order_by:
            body["order_by"] = self.order_by
        if self.aggregate_unit:
            body["aggregate_unit"] = self.aggregate_unit
        return body
```

- [ ] **Step 2: Verify Python type checking passes**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server && uv run python -c "from pagerduty_mcp.models.analytics import GetIncidentMetricsByTeamRequest; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add pagerduty_mcp/models/analytics.py
git commit -m "feat: add aggregate_unit to GetIncidentMetricsByTeamRequest for trend queries"
```

---

## Task 2: TypeScript types, fetchTrendsData, mock data

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/api.ts`
- Modify: `mcp-apps/operations-intelligence/src/mock.ts`

Remove all `fetchInsight`/`InsightMessage` code. Add `TrendPoint`, `TrendsData`, update `OpsData`, add 6th parallel fetch.

- [ ] **Step 1: Add types and update `OpsData` in `src/api.ts`**

Add after the `AggregatedMetrics` interface (around line 75):

```typescript
export interface TrendPoint {
  weekStart: string;       // range_start from API, e.g. "2026-03-17"
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrMinutes: number | null;
  totalInterruptions: number;
}

export interface TrendsData {
  points: TrendPoint[];    // one entry per week, sorted ascending
}
```

Update `OpsData` — add `trendsData: TrendsData | null` after `aggregated`:

```typescript
export interface OpsData {
  // ... existing fields ...
  aggregated: AggregatedMetrics | null;
  trendsData: TrendsData | null;
  // Section data
  serviceMetrics: ServiceMetric[];
  teamMetrics: TeamMetric[];
  responderMetrics: ResponderMetric[];
}
```

- [ ] **Step 2: Add 6th parallel fetch in `fetchOpsData`**

In `fetchOpsData`, extend `Promise.allSettled` to 6 calls:

```typescript
const [teamsResult, serviceResult, teamResult, responderResult, aggregatedResult, trendsResult] = await Promise.allSettled([
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
  app.callServerTool({
    name: "get_incident_metrics_by_team",
    arguments: { request: { filters: incidentFilters, aggregate_unit: "week" } },
  }),
]);
```

- [ ] **Step 3: Map trends result**

After the aggregated block (after line ~252), add:

```typescript
// Trends — weekly rollup across all teams (aggregate_unit: "week")
const trendsRaw = trendsResult.status === "fulfilled" ? extract<any>(trendsResult.value) : null;
const trendsData: TrendsData | null = trendsRaw ? (() => {
  // Group by week: sum incidents/interruptions, weighted-avg MTTA/MTTR
  const byWeek = new Map<string, { totalIncidents: number; mttaSum: number; mttrSum: number; intSum: number; mttaCount: number; mttrCount: number }>();
  for (const row of (trendsRaw.response ?? [])) {
    const week = (row.range_start ?? "").substring(0, 10);
    if (!week) continue;
    const existing = byWeek.get(week) ?? { totalIncidents: 0, mttaSum: 0, mttrSum: 0, intSum: 0, mttaCount: 0, mttrCount: 0 };
    const inc = row.total_incident_count ?? 0;
    existing.totalIncidents += inc;
    existing.intSum += row.total_interruptions ?? 0;
    if (row.mean_seconds_to_first_ack != null && inc > 0) {
      existing.mttaSum += row.mean_seconds_to_first_ack * inc;
      existing.mttaCount += inc;
    }
    if (row.mean_seconds_to_resolve != null && inc > 0) {
      existing.mttrSum += row.mean_seconds_to_resolve * inc;
      existing.mttrCount += inc;
    }
    byWeek.set(week, existing);
  }
  const points: TrendPoint[] = Array.from(byWeek.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([weekStart, v]) => ({
      weekStart,
      totalIncidents: v.totalIncidents,
      mttaMinutes: v.mttaCount > 0 ? Math.round(v.mttaSum / v.mttaCount / 60) : null,
      mttrMinutes: v.mttrCount > 0 ? Math.round(v.mttrSum / v.mttrCount / 60) : null,
      totalInterruptions: v.intSum,
    }));
  return { points };
})() : null;
```

Add `trendsData` to the return object.

- [ ] **Step 4: Remove `fetchInsight` and `InsightMessage`**

Delete the entire `// ─── Insights fetch (PagerDuty Advanced MCP) ─────` section (lines ~288–327) and the `InsightMessage` interface (~line 95–98).

Also update the file header comment to remove "Insights tab calls insights_agent_tool".

- [ ] **Step 5: Update `src/mock.ts`**

Add `trendsData` to `MOCK_OPS_DATA`. Remove `MOCK_INSIGHT_RESPONSES`. The mock data should have 4 weeks of realistic data:

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
  trendsData: {
    points: [
      { weekStart: "2026-03-24", totalIncidents: 9,  mttaMinutes: 11, mttrMinutes: 105, totalInterruptions: 6 },
      { weekStart: "2026-03-31", totalIncidents: 14, mttaMinutes: 9,  mttrMinutes: 98,  totalInterruptions: 9 },
      { weekStart: "2026-04-07", totalIncidents: 12, mttaMinutes: 7,  mttrMinutes: 88,  totalInterruptions: 7 },
      { weekStart: "2026-04-14", totalIncidents: 12, mttaMinutes: 6,  mttrMinutes: 82,  totalInterruptions: 4 },
    ],
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
```

- [ ] **Step 6: TypeScript check**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use && npx tsc --noEmit 2>&1
```

Expected: no errors

- [ ] **Step 7: Commit**

```bash
git add mcp-apps/operations-intelligence/src/api.ts mcp-apps/operations-intelligence/src/mock.ts
git commit -m "feat: add TrendsData types, weekly fetch, remove fetchInsight"
```

---

## Task 3: TrendsTab component with SVG charts + CSS

**Files:**
- Create: `mcp-apps/operations-intelligence/src/components/TrendsTab.tsx`
- Modify: `mcp-apps/operations-intelligence/src/styles.css`

Three pure-SVG charts rendered in React. No chart library — hand-built SVG with viewBox coordinates. Each chart is 100% wide, fixed height, responsive via `preserveAspectRatio`.

- [ ] **Step 1: Create `src/components/TrendsTab.tsx`**

```typescript
import type { TrendsData, TrendPoint } from "../api";

interface TrendsTabProps {
  trendsData: TrendsData | null;
}

const CHART_W = 600;
const CHART_H = 120;
const PAD = { top: 10, right: 16, bottom: 28, left: 44 };

function plotW() { return CHART_W - PAD.left - PAD.right; }
function plotH() { return CHART_H - PAD.top - PAD.bottom; }

function formatWeek(weekStart: string): string {
  const d = new Date(weekStart + "T00:00:00");
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

interface BarChartProps {
  points: TrendPoint[];
  getValue: (p: TrendPoint) => number;
  color: string;
  yLabel: string;
}

function BarChart({ points, getValue, color, yLabel }: BarChartProps) {
  if (points.length === 0) return <div className="chart-empty">No data</div>;
  const values = points.map(getValue);
  const maxVal = Math.max(...values, 1);
  const barW = plotW() / points.length * 0.6;
  const barGap = plotW() / points.length;

  return (
    <svg
      viewBox={`0 0 ${CHART_W} ${CHART_H}`}
      className="trend-chart"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* Y-axis */}
      <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={PAD.top + plotH()} stroke="var(--border-secondary)" strokeWidth="1" />
      {/* Y-axis label */}
      <text x={8} y={PAD.top + plotH() / 2} fontSize="10" fill="var(--text-secondary)" textAnchor="middle" transform={`rotate(-90, 8, ${PAD.top + plotH() / 2})`}>{yLabel}</text>
      {/* Y ticks: 0 and max */}
      <text x={PAD.left - 4} y={PAD.top + plotH()} fontSize="9" fill="var(--text-secondary)" textAnchor="end" dominantBaseline="middle">0</text>
      <text x={PAD.left - 4} y={PAD.top} fontSize="9" fill="var(--text-secondary)" textAnchor="end" dominantBaseline="middle">{maxVal}</text>
      {/* Bars */}
      {points.map((p, i) => {
        const val = getValue(p);
        const barH = (val / maxVal) * plotH();
        const x = PAD.left + i * barGap + (barGap - barW) / 2;
        const y = PAD.top + plotH() - barH;
        return (
          <g key={p.weekStart}>
            <rect x={x} y={y} width={barW} height={barH} fill={color} rx="2" opacity="0.85" />
            <text x={x + barW / 2} y={PAD.top + plotH() + 14} fontSize="9" fill="var(--text-secondary)" textAnchor="middle">{formatWeek(p.weekStart)}</text>
          </g>
        );
      })}
    </svg>
  );
}

interface LineChartProps {
  points: TrendPoint[];
  getValue: (p: TrendPoint) => number | null;
  color: string;
  yLabel: string;
}

function LineChart({ points, getValue, color, yLabel }: LineChartProps) {
  const valid = points.filter((p) => getValue(p) !== null);
  if (valid.length === 0) return <div className="chart-empty">No data</div>;
  const values = valid.map((p) => getValue(p) as number);
  const maxVal = Math.max(...values, 1);
  const minVal = Math.min(...values, 0);
  const range = maxVal - minVal || 1;

  function xOf(i: number) {
    return PAD.left + (i / (points.length - 1 || 1)) * plotW();
  }
  function yOf(val: number) {
    return PAD.top + plotH() - ((val - minVal) / range) * plotH();
  }

  const polyPoints = points
    .map((p, i) => {
      const v = getValue(p);
      return v !== null ? `${xOf(i)},${yOf(v)}` : null;
    })
    .filter(Boolean)
    .join(" ");

  return (
    <svg
      viewBox={`0 0 ${CHART_W} ${CHART_H}`}
      className="trend-chart"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* Y-axis */}
      <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={PAD.top + plotH()} stroke="var(--border-secondary)" strokeWidth="1" />
      {/* Y-axis label */}
      <text x={8} y={PAD.top + plotH() / 2} fontSize="10" fill="var(--text-secondary)" textAnchor="middle" transform={`rotate(-90, 8, ${PAD.top + plotH() / 2})`}>{yLabel}</text>
      {/* Y ticks */}
      <text x={PAD.left - 4} y={PAD.top + plotH()} fontSize="9" fill="var(--text-secondary)" textAnchor="end" dominantBaseline="middle">{minVal}</text>
      <text x={PAD.left - 4} y={PAD.top} fontSize="9" fill="var(--text-secondary)" textAnchor="end" dominantBaseline="middle">{maxVal}</text>
      {/* Line */}
      <polyline points={polyPoints} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      {/* Dots + X labels */}
      {points.map((p, i) => {
        const v = getValue(p);
        return (
          <g key={p.weekStart}>
            {v !== null && (
              <circle cx={xOf(i)} cy={yOf(v)} r="3.5" fill={color} />
            )}
            <text x={xOf(i)} y={PAD.top + plotH() + 14} fontSize="9" fill="var(--text-secondary)" textAnchor="middle">{formatWeek(p.weekStart)}</text>
          </g>
        );
      })}
    </svg>
  );
}

export function TrendsTab({ trendsData }: TrendsTabProps) {
  if (!trendsData || trendsData.points.length === 0) {
    return <div className="trends-empty">No trend data available for this period.</div>;
  }

  return (
    <div className="trends-tab">
      <div className="trend-card">
        <div className="trend-card-title">Incident Volume (per week)</div>
        <BarChart points={trendsData.points} getValue={(p) => p.totalIncidents} color="var(--status-triggered)" yLabel="Incidents" />
      </div>
      <div className="trend-card">
        <div className="trend-card-title">MTTA (mean time to ack, minutes)</div>
        <LineChart points={trendsData.points} getValue={(p) => p.mttaMinutes} color="var(--status-acknowledged)" yLabel="min" />
      </div>
      <div className="trend-card">
        <div className="trend-card-title">MTTR (mean time to resolve, minutes)</div>
        <LineChart points={trendsData.points} getValue={(p) => p.mttrMinutes} color="var(--pd-green)" yLabel="min" />
      </div>
      <div className="trend-card">
        <div className="trend-card-title">Interruptions (per week)</div>
        <BarChart points={trendsData.points} getValue={(p) => p.totalInterruptions} color="var(--color-escalation)" yLabel="Count" />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Add CSS to `src/styles.css`**

Remove the insight/chat CSS sections (search for `.insight-card`, `.insight-skeleton`, `.insight-error`, `.insight-tab`, `.chat-`, `.insights-tab`). Add trend CSS at the end:

```css
/* ── Trends tab ── */
.trends-tab {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.trends-empty {
  padding: 32px 16px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
}

.trend-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 12px 16px;
}

.trend-card-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.trend-chart {
  width: 100%;
  height: auto;
  display: block;
}

.chart-empty {
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 8px 0;
}
```

- [ ] **Step 3: TypeScript check**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use && npx tsc --noEmit 2>&1
```

Expected: no errors

- [ ] **Step 4: Commit**

```bash
git add mcp-apps/operations-intelligence/src/components/TrendsTab.tsx mcp-apps/operations-intelligence/src/styles.css
git commit -m "feat: add TrendsTab component with SVG bar/line charts"
```

---

## Task 4: Wire TrendsTab into mcp-app.tsx, remove Insights components

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/mcp-app.tsx`
- Delete: `mcp-apps/operations-intelligence/src/components/InsightCard.tsx`
- Delete: `mcp-apps/operations-intelligence/src/components/InsightsChat.tsx`
- Delete: `mcp-apps/operations-intelligence/src/components/InsightsTab.tsx`

- [ ] **Step 1: Update `src/mcp-app.tsx`**

Replace the header comment to say "Three tabs: Operational, Team Health, Trends".

Remove imports:
```typescript
import { InsightsTab } from "./components/InsightsTab";
import type { App as McpApp } from "@modelcontextprotocol/ext-apps";
```

Add import:
```typescript
import { TrendsTab } from "./components/TrendsTab";
```

Remove `McpApp` type alias usage (it was only needed for InsightsTab). The `app` variable from `useApp` is typed via `useApp`, so no cast needed.

Change `type Tab`:
```typescript
type Tab = "operational" | "teamHealth" | "trends";
```

Remove `refreshKey` state (it was only for InsightsTab).

Update tab bar — replace "Insights" button with "Trends":
```tsx
<button
  className={`tab-btn${tab === "trends" ? " tab-active" : ""}`}
  onClick={() => setTab("trends")}
>
  Trends
</button>
```

Replace the Insights branch in the render:
```tsx
) : tab === "trends" && data ? (
  <TrendsTab trendsData={data.trendsData} />
) : null}
```

Remove `selectedTeamName` memo if it was only used by InsightsTab. Check — it's passed as `teamName` to `InsightsTab`. If nothing else uses it, remove it.

- [ ] **Step 2: Delete old Insights component files**

```bash
rm mcp-apps/operations-intelligence/src/components/InsightCard.tsx
rm mcp-apps/operations-intelligence/src/components/InsightsChat.tsx
rm mcp-apps/operations-intelligence/src/components/InsightsTab.tsx
```

- [ ] **Step 3: TypeScript check + build**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use && npx tsc --noEmit && npm run build 2>&1 | tail -10
```

Expected: clean build

- [ ] **Step 4: Run Playwright tests**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use 2>/dev/null || true && npx playwright test pw-test.spec.mjs --browser=chromium 2>&1 | tail -15
```

Expected: 3 passed (the Insights test will need updating — change the test to click "Trends" and look for `.trend-card`)

Update `pw-test.spec.mjs` test 3:
```javascript
// ── 3. Trends tab — charts render ──────────────────────────────────────
test("Trends tab — charts render", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".tabs", { timeout: 8000 });

  await page.click('button:has-text("Trends")');
  await page.waitForSelector(".trend-card", { timeout: 5000 });
  await screenshot(page, "03-trends");

  await expect(page.locator(".trend-card").first()).toBeVisible();
});
```

- [ ] **Step 5: Deploy**

```bash
cp mcp-apps/operations-intelligence/dist/mcp-app.html pagerduty_mcp/operations_intelligence_view.html
```

- [ ] **Step 6: Commit**

```bash
git add mcp-apps/operations-intelligence/src/mcp-app.tsx mcp-apps/operations-intelligence/src/components/ mcp-apps/operations-intelligence/pw-test.spec.mjs pagerduty_mcp/operations_intelligence_view.html && git add -f mcp-apps/operations-intelligence/dist/mcp-app.html
git commit -m "feat: replace Insights tab with Trends tab using real weekly analytics data"
```

---

## Task 5: Logo update for all MCP apps + rebuild + deploy

**Files:**
- Create: `mcp-apps/operations-intelligence/src/assets/pagerduty-icon.svg`
- Modify: `mcp-apps/operations-intelligence/src/components/PagerDutyLogo.tsx`
- Create: `mcp-apps/post-mortem-builder/src/assets/pagerduty-icon.svg`
- Modify: `mcp-apps/post-mortem-builder/src/components/PagerDutyLogo.tsx`
- Create: `mcp-apps/shift-coverage-wizard/src/assets/pagerduty-icon.svg`
- Modify: `mcp-apps/shift-coverage-wizard/src/components/PagerDutyLogo.tsx`

The official icon is at `mcp-apps/incident-command-center/src/assets/pagerduty-icon.svg`. It's a green "P" logo on transparent background with `fill-rule="evenodd"`. Copy it to each app's `src/assets/` and update the `PagerDutyLogo.tsx` to use the asset import pattern.

- [ ] **Step 1: Copy SVG asset to all three apps**

```bash
cp mcp-apps/incident-command-center/src/assets/pagerduty-icon.svg mcp-apps/operations-intelligence/src/assets/pagerduty-icon.svg
cp mcp-apps/incident-command-center/src/assets/pagerduty-icon.svg mcp-apps/post-mortem-builder/src/assets/pagerduty-icon.svg
cp mcp-apps/incident-command-center/src/assets/pagerduty-icon.svg mcp-apps/shift-coverage-wizard/src/assets/pagerduty-icon.svg
```

- [ ] **Step 2: Update `PagerDutyLogo.tsx` in each app**

Replace the inline SVG version with the asset import pattern. For each of the three apps:

```typescript
import logoSvg from "../assets/pagerduty-icon.svg";

interface PagerDutyLogoProps {
  size?: number;
}

export function PagerDutyLogo({ size = 36 }: PagerDutyLogoProps) {
  return (
    <img
      src={logoSvg}
      alt="PagerDuty"
      width={size}
      height={size}
      style={{ display: "block" }}
    />
  );
}
```

Files to update:
- `mcp-apps/operations-intelligence/src/components/PagerDutyLogo.tsx`
- `mcp-apps/post-mortem-builder/src/components/PagerDutyLogo.tsx`
- `mcp-apps/shift-coverage-wizard/src/components/PagerDutyLogo.tsx`

- [ ] **Step 3: Check vite config can handle SVG imports for each app**

Vite handles SVG as asset URL by default. Verify each app's `vite.config.ts` doesn't disable asset handling. If it uses `vite-plugin-singlefile`, the SVG will be inlined automatically.

```bash
for app in operations-intelligence post-mortem-builder shift-coverage-wizard; do
  echo "=== $app ==="; cat mcp-apps/$app/vite.config.ts 2>/dev/null | head -20
done
```

- [ ] **Step 4: Build all three apps**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence && source ~/.nvm/nvm.sh && nvm use 2>/dev/null || true && npm run build 2>&1 | tail -5
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/post-mortem-builder && source ~/.nvm/nvm.sh && nvm use 2>/dev/null || true && npm run build 2>&1 | tail -5
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/shift-coverage-wizard && source ~/.nvm/nvm.sh && nvm use 2>/dev/null || true && npm run build 2>&1 | tail -5
```

Expected: all three build successfully.

- [ ] **Step 5: Deploy to Python package**

```bash
cp mcp-apps/operations-intelligence/dist/mcp-app.html pagerduty_mcp/operations_intelligence_view.html
cp mcp-apps/post-mortem-builder/dist/mcp-app.html pagerduty_mcp/post_mortem_builder_view.html
cp mcp-apps/shift-coverage-wizard/dist/mcp-app.html pagerduty_mcp/shift_coverage_wizard_view.html
```

- [ ] **Step 6: Commit**

```bash
git add mcp-apps/operations-intelligence/src/assets/ mcp-apps/operations-intelligence/src/components/PagerDutyLogo.tsx
git add mcp-apps/post-mortem-builder/src/assets/ mcp-apps/post-mortem-builder/src/components/PagerDutyLogo.tsx
git add mcp-apps/shift-coverage-wizard/src/assets/ mcp-apps/shift-coverage-wizard/src/components/PagerDutyLogo.tsx
git add pagerduty_mcp/operations_intelligence_view.html pagerduty_mcp/post_mortem_builder_view.html pagerduty_mcp/shift_coverage_wizard_view.html
git add -f mcp-apps/operations-intelligence/dist/mcp-app.html mcp-apps/post-mortem-builder/dist/mcp-app.html mcp-apps/shift-coverage-wizard/dist/mcp-app.html
git commit -m "feat: use official PagerDuty icon across operations-intelligence, post-mortem-builder, shift-coverage-wizard"
```
