# Operations Intelligence v2 — Design Spec

**Date:** 2026-04-19
**Status:** Approved

## Goal

Redesign the Operations Intelligence MCP App to feel like a compact, embedded version of PagerDuty Insights. Replace the raw-incident-list approach with proper pre-aggregated Analytics API metrics across multiple lenses (service, team, responder), and add an AI-powered Insights tab backed by the PagerDuty Advanced MCP server's `insights_agent_tool`.

## Scope

- Rewrite `api.ts` to use Analytics API endpoints instead of `list_incidents`
- Remove the incident table (no raw incident list)
- Add three new backend MCP tools to `analytics.py`
- Add a two-tab layout: **Operational** and **Insights**
- Integrate `insights_agent_tool` from `pagerduty-advance-mcp` server

---

## Architecture

### Tab Structure

```
[Operational]  [Insights]
─────────────────────────────────────────────────────────
Filter bar: Team picker | Date From | Date To | Refresh
```

Both tabs share the filter bar. Changing filters and clicking Refresh re-fetches both tabs' data.

---

## Operational Tab

### KPI Summary Bar (5 cards)

Data source: `POST /analytics/metrics/incidents/teams` (aggregated across all teams or filtered team)

| Card | Metric | Source field |
|---|---|---|
| Total Incidents | `total_incident_count` | teams aggregate |
| MTTA | `mean_seconds_to_first_ack` → minutes | teams aggregate |
| MTTR p50 / p90 | `p50_seconds_to_resolve` / `p90_seconds_to_resolve` → minutes | teams aggregate |
| Escalation Rate | `total_incidents_manual_escalated / total_incident_count` % | teams aggregate |
| Uptime % | `up_time_pct` | teams aggregate |

### Section 1 — Service Performance

Data source: `POST /analytics/metrics/incidents/services`

Columns: Service | Incidents | MTTA (min) | MTTR p50 (min) | Escalations | High Urgency %

High Urgency % computed client-side if not directly available; alternatively filter with `urgency: "high"` in a second call (deferred — use total_incident_count for now).

### Section 2 — Team Performance

Data source: `POST /analytics/metrics/incidents/teams`

Columns: Team | Incidents | MTTA (min) | MTTR (min) | Escalations | Interruptions

### Section 3 — Responder Load

Data source: `POST /analytics/metrics/responders/all`

Columns: Responder | On-call hrs | Incidents | Acks | Sleep interruptions | Engaged time (min)

---

## Insights Tab

### Auto-Summary (on tab load or Refresh)

Fires 3 pre-written queries sequentially to `insights_agent_tool`, each embedding current filter state (team name, date range) in the query text:

1. `"Summarize MTTR and MTTA trends for [team] between [since] and [until]. Highlight any notable changes or anomalies."`
2. `"Which services have the highest incident volume and worst resolution times for [team] between [since] and [until]?"`
3. `"How is [team] performing in terms of escalations, on-call interruptions, and responder load between [since] and [until]?"`

Each response renders as an `InsightCard` (title + narrative body, with loading skeleton while streaming).

### Chat Panel

Below the auto-summary cards, a chat thread with:
- Message history (user messages + AI responses alternating)
- Text input + Send button
- Each user message calls `insights_agent_tool` with the same `session_id` (persisted per tab mount) to maintain conversation context
- Responses appended to the thread

---

## Backend Changes

### New tools in `pagerduty_mcp/tools/analytics.py`

Three new functions following the exact pattern of `get_responder_metrics`:

#### 1. `get_incident_metrics_by_service`
- Endpoint: `POST /analytics/metrics/incidents/services`
- Request model: `GetIncidentMetricsByServiceRequest`
- Fields: `created_at_start`, `created_at_end`, `team_ids`, `service_ids`, `urgency`, `time_zone`, `order`, `order_by`
- Response: list of service metric objects with all mean/percentile/total fields

#### 2. `get_incident_metrics_by_team`
- Endpoint: `POST /analytics/metrics/incidents/teams`
- Request model: `GetIncidentMetricsByTeamRequest`
- Fields: same as above plus `aggregate_unit` (optional, for time-series)
- Response: list of team metric objects

#### 3. `get_responder_load_metrics`
- Endpoint: `POST /analytics/metrics/responders/all`
- Request model: `GetResponderLoadMetricsRequest`
- Fields: `date_range_start`, `date_range_end`, `team_ids`, `urgency`, `time_zone`, `order`, `order_by`
- Response: list of responder metric objects (on-call seconds, interruptions, engaged seconds)

### Registration

- All three added to `pagerduty_mcp/tools/__init__.py` as read-only tools
- All three registered in `server.py` alongside existing analytics tools
- New Pydantic models added to `pagerduty_mcp/models/analytics.py`

---

## Frontend Changes

### Files Modified

| File | Change |
|---|---|
| `src/api.ts` | Full rewrite: `fetchOpsData()` calls 3 new analytics tools; add `fetchInsightsSummary()` |
| `src/mcp-app.tsx` | Add tab state, route to Operational/Insights views, remove incident table |
| `src/components/SummaryCards.tsx` | Replace manual MTTR with p50/p90, add MTTA and Escalation Rate and Uptime cards |
| `src/components/ServiceBreakdown.tsx` | Rework into full analytics table (MTTA, MTTR p50, escalations columns) |

### Files Removed

| File | Reason |
|---|---|
| `src/components/IncidentTable.tsx` | No raw incident list in v2 |

### New Files

| File | Purpose |
|---|---|
| `src/components/TeamBreakdown.tsx` | Team performance table (mirrors ServiceBreakdown structure) |
| `src/components/ResponderLoad.tsx` | Responder load table |
| `src/components/InsightCard.tsx` | Single AI insight card with loading skeleton |
| `src/components/InsightsChat.tsx` | Chat thread + input for follow-up questions |
| `src/components/InsightsTab.tsx` | Orchestrates 3 auto-summary InsightCards + InsightsChat |

### Updated Types in `api.ts`

```ts
// Replaces OpsData
export interface OpsData {
  teams: Team[];
  selectedTeam: string | null;
  since: string;
  until: string;
  // KPI summary (from team aggregate)
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrP50Minutes: number | null;
  mttrP90Minutes: number | null;
  escalationRate: number | null;   // 0-100 %
  uptimePct: number | null;
  // Section data
  serviceMetrics: ServiceMetric[];
  teamMetrics: TeamMetric[];
  responderMetrics: ResponderMetric[];
}

export interface ServiceMetric {
  id: string;
  name: string;
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrP50Minutes: number | null;
  escalationCount: number;
}

export interface TeamMetric {
  id: string;
  name: string;
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrMinutes: number | null;
  escalationCount: number;
  totalInterruptions: number;
}

export interface ResponderMetric {
  id: string;
  name: string;
  onCallHours: number;
  totalIncidents: number;
  totalAcks: number;
  sleepInterruptions: number;
  engagedMinutes: number;
}
```

---

## Data Flow

```
Filter bar (team, since, until)
        │
        ├─ Operational tab
        │     ├─ get_incident_metrics_by_team  → KPI cards + Team section
        │     ├─ get_incident_metrics_by_service → Service section
        │     └─ get_responder_load_metrics    → Responder section
        │
        └─ Insights tab
              ├─ insights_agent_tool (query 1: MTTR trends)     → InsightCard
              ├─ insights_agent_tool (query 2: noisy services)  → InsightCard
              ├─ insights_agent_tool (query 3: team load)       → InsightCard
              └─ insights_agent_tool (user chat input)          → InsightsChat thread
```

The `insights_agent_tool` is called on the `pagerduty-advance-mcp` MCP server using `app.callServerTool({ name: "insights_agent_tool", serverName: "pagerduty-advance-mcp", ... })`.

---

## Error Handling

- Each analytics API call wrapped in try/catch; failures show an inline error banner per section (not a full-page error)
- If `insights_agent_tool` fails, InsightCard shows "Could not load insight" with a retry button
- Partial failures allowed: Operational tab can render with 2 of 3 sections if one call fails

---

## Out of Scope

- Time-series charts (aggregate_unit day/week/month trend lines) — deferred
- High urgency % per service via second filtered API call — deferred
- Export/download of metrics — not in scope
- Priority-based filtering — not in scope
