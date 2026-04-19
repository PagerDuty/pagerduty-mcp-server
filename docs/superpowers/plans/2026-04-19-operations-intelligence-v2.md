# Operations Intelligence v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Operations Intelligence MCP App into a compact PagerDuty Insights replica — replacing the raw-incident-list approach with proper pre-aggregated Analytics API metrics (service/team/responder lenses) and adding an AI-powered Insights tab via `insights_agent_tool` from the PagerDuty Advanced MCP server.

**Architecture:** Three new Python MCP tools call the PagerDuty Analytics API (`/analytics/metrics/incidents/services`, `/analytics/metrics/incidents/teams`, `/analytics/metrics/responders/all`). The frontend React app gains a two-tab layout: **Operational** (5 KPI cards + 3 metric tables) and **Insights** (auto-generated AI summary cards + a follow-up chat panel powered by `insights_agent_tool` on `pagerduty-advance-mcp` server).

**Tech Stack:** Python/Pydantic (backend tools), React 18/Preact (frontend), TypeScript, Vite + vite-plugin-singlefile (bundler), `@modelcontextprotocol/ext-apps` SDK (`app.callServerTool`).

---

## File Map

### Backend — modified/created

| File | Change |
|---|---|
| `pagerduty_mcp/models/analytics.py` | Add 3 request models + 3 response models |
| `pagerduty_mcp/tools/analytics.py` | Add 3 new tool functions |
| `pagerduty_mcp/tools/__init__.py` | Export 3 new tools in `read_tools` |
| `pagerduty_mcp/server.py` | Update docstring of `add_operations_intelligence` to reference new tools |

### Frontend — modified

| File | Change |
|---|---|
| `mcp-apps/operations-intelligence/src/api.ts` | Full rewrite — new types + 2 fetch functions |
| `mcp-apps/operations-intelligence/src/mcp-app.tsx` | Add tab state, remove incident table wiring, add Insights tab |
| `mcp-apps/operations-intelligence/src/components/SummaryCards.tsx` | Replace with analytics-driven KPI cards |
| `mcp-apps/operations-intelligence/src/components/ServiceBreakdown.tsx` | Replace with analytics columns (MTTA, MTTR p50, escalations) |
| `mcp-apps/operations-intelligence/src/styles.css` | Add tab styles, insight card styles, chat styles |

### Frontend — new components

| File | Purpose |
|---|---|
| `mcp-apps/operations-intelligence/src/components/TeamBreakdown.tsx` | Team metrics table |
| `mcp-apps/operations-intelligence/src/components/ResponderLoad.tsx` | Responder load table |
| `mcp-apps/operations-intelligence/src/components/InsightCard.tsx` | AI insight card with loading skeleton |
| `mcp-apps/operations-intelligence/src/components/InsightsChat.tsx` | Chat thread + input for follow-up questions |
| `mcp-apps/operations-intelligence/src/components/InsightsTab.tsx` | Orchestrates auto-summary + chat |

### Frontend — deleted

| File | Reason |
|---|---|
| `mcp-apps/operations-intelligence/src/components/IncidentTable.tsx` | No raw incident list in v2 |

### Build output (regenerated, not hand-edited)

| File | How |
|---|---|
| `pagerduty_mcp/operations_intelligence_view.html` | Run `npm run build` in `mcp-apps/operations-intelligence/` |

---

## Task 1: Add analytics Pydantic models for the 3 new endpoints

**Files:**
- Modify: `pagerduty_mcp/models/analytics.py`

- [ ] **Step 1: Add incident filters model and 3 request models**

Open `pagerduty_mcp/models/analytics.py` and append after the existing `AnalyticsResponderMetrics` class:

```python
class AnalyticsIncidentFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    created_at_start: str = Field(
        description="ISO8601 DateTime. Incidents created before this are omitted."
    )
    created_at_end: str = Field(
        description="ISO8601 DateTime. Incidents created on/after this are omitted."
    )
    team_ids: list[str] | None = Field(
        default=None,
        description="Only incidents related to these teams will be included.",
    )
    service_ids: list[str] | None = Field(
        default=None,
        description="Only incidents related to these services will be included.",
    )
    urgency: str | None = Field(
        default=None,
        description="Filter by urgency: 'high' or 'low'.",
    )


class GetIncidentMetricsByServiceRequest(BaseModel):
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
        return body


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
        return body


class GetResponderLoadMetricsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: AnalyticsFilters = Field(
        description="Date range (date_range_start/end) and optional filters."
    )
    time_zone: str | None = Field(
        default=None,
        description="The time zone for results (e.g. 'America/New_York').",
    )
    order: str | None = Field(default=None, description="Sort order: 'asc' or 'desc'.")
    order_by: str | None = Field(default=None, description="Field to sort results by.")

    def to_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "filters": {
                "date_range_start": self.filters.date_range_start,
                "date_range_end": self.filters.date_range_end,
            }
        }
        if self.filters.team_ids:
            body["filters"]["team_ids"] = self.filters.team_ids
        if self.filters.urgency:
            body["filters"]["urgency"] = self.filters.urgency
        if self.time_zone:
            body["time_zone"] = self.time_zone
        if self.order:
            body["order"] = self.order
        if self.order_by:
            body["order_by"] = self.order_by
        return body
```

- [ ] **Step 2: Add 3 response models**

Still in `pagerduty_mcp/models/analytics.py`, append after the request models:

```python
class AnalyticsServiceMetrics(BaseModel):
    """Per-service aggregate incident metrics from PagerDuty Analytics."""

    service_id: str | None = Field(default=None)
    service_name: str | None = Field(default=None)
    team_id: str | None = Field(default=None)
    team_name: str | None = Field(default=None)

    total_incident_count: int | None = Field(default=None)
    mean_seconds_to_first_ack: int | None = Field(default=None, description="Mean MTTA in seconds.")
    p50_seconds_to_resolve: int | None = Field(default=None, description="p50 MTTR in seconds.")
    p90_seconds_to_resolve: int | None = Field(default=None, description="p90 MTTR in seconds.")
    total_escalation_count: int | None = Field(default=None)
    total_incidents_manual_escalated: int | None = Field(default=None)
    total_interruptions: int | None = Field(default=None)
    up_time_pct: float | None = Field(default=None, description="Service availability percentage.")


class AnalyticsTeamMetrics(BaseModel):
    """Per-team aggregate incident metrics from PagerDuty Analytics."""

    team_id: str | None = Field(default=None)
    team_name: str | None = Field(default=None)

    total_incident_count: int | None = Field(default=None)
    mean_seconds_to_first_ack: int | None = Field(default=None, description="Mean MTTA in seconds.")
    p50_seconds_to_resolve: int | None = Field(default=None, description="p50 MTTR in seconds.")
    p90_seconds_to_resolve: int | None = Field(default=None, description="p90 MTTR in seconds.")
    mean_seconds_to_resolve: int | None = Field(default=None)
    total_escalation_count: int | None = Field(default=None)
    total_incidents_manual_escalated: int | None = Field(default=None)
    total_interruptions: int | None = Field(default=None)
    up_time_pct: float | None = Field(default=None)


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
```

- [ ] **Step 3: Run the existing tests to confirm no regressions**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
source ~/.nvm/nvm.sh && nvm use
python -m pytest tests/ -x -q 2>&1 | tail -20
```

Expected: all tests pass (no analytics tests exist yet — that's fine).

- [ ] **Step 4: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add pagerduty_mcp/models/analytics.py
git commit -m "feat: add analytics Pydantic models for service, team, and responder load metrics"
```

---

## Task 2: Add 3 new analytics tool functions

**Files:**
- Modify: `pagerduty_mcp/tools/analytics.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_analytics.py`:

```python
"""Unit tests for analytics tools."""

import unittest
from unittest.mock import Mock, patch

from pagerduty_mcp.models.analytics import (
    AnalyticsIncidentFilters,
    AnalyticsFilters,
    GetIncidentMetricsByServiceRequest,
    GetIncidentMetricsByTeamRequest,
    GetResponderLoadMetricsRequest,
)
from pagerduty_mcp.tools.analytics import (
    get_incident_metrics_by_service,
    get_incident_metrics_by_team,
    get_responder_load_metrics,
)


class TestGetIncidentMetricsByService(unittest.TestCase):
    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_returns_json_list(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {
            "data": [
                {
                    "service_id": "SVC1",
                    "service_name": "API",
                    "total_incident_count": 10,
                    "mean_seconds_to_first_ack": 120,
                    "p50_seconds_to_resolve": 600,
                    "p90_seconds_to_resolve": 1800,
                    "total_escalation_count": 2,
                    "total_incidents_manual_escalated": 1,
                    "total_interruptions": 5,
                    "up_time_pct": 99.5,
                }
            ]
        }
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByServiceRequest(
            filters=AnalyticsIncidentFilters(
                created_at_start="2026-03-01T00:00:00Z",
                created_at_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_incident_metrics_by_service(request)

        import json
        data = json.loads(result)
        self.assertEqual(len(data["response"]), 1)
        self.assertEqual(data["response"][0]["service_name"], "API")
        self.assertEqual(data["response"][0]["total_incident_count"], 10)
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/incidents/services",
            json={
                "filters": {
                    "created_at_start": "2026-03-01T00:00:00Z",
                    "created_at_end": "2026-04-01T00:00:00Z",
                }
            },
        )

    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_handles_empty_response(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {"data": []}
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByServiceRequest(
            filters=AnalyticsIncidentFilters(
                created_at_start="2026-03-01T00:00:00Z",
                created_at_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_incident_metrics_by_service(request)

        import json
        data = json.loads(result)
        self.assertEqual(data["response"], [])


class TestGetIncidentMetricsByTeam(unittest.TestCase):
    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_returns_json_list(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {
            "data": [
                {
                    "team_id": "T1",
                    "team_name": "Platform",
                    "total_incident_count": 5,
                    "mean_seconds_to_first_ack": 90,
                    "p50_seconds_to_resolve": 300,
                    "p90_seconds_to_resolve": 900,
                    "mean_seconds_to_resolve": 450,
                    "total_escalation_count": 1,
                    "total_incidents_manual_escalated": 0,
                    "total_interruptions": 3,
                    "up_time_pct": 99.9,
                }
            ]
        }
        mock_get_client.return_value = mock_client

        request = GetIncidentMetricsByTeamRequest(
            filters=AnalyticsIncidentFilters(
                created_at_start="2026-03-01T00:00:00Z",
                created_at_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_incident_metrics_by_team(request)

        import json
        data = json.loads(result)
        self.assertEqual(data["response"][0]["team_name"], "Platform")
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/incidents/teams",
            json={
                "filters": {
                    "created_at_start": "2026-03-01T00:00:00Z",
                    "created_at_end": "2026-04-01T00:00:00Z",
                }
            },
        )


class TestGetResponderLoadMetrics(unittest.TestCase):
    @patch("pagerduty_mcp.tools.analytics.get_client")
    def test_returns_json_list(self, mock_get_client):
        mock_client = Mock()
        mock_client.rpost.return_value = {
            "data": [
                {
                    "responder_id": "U1",
                    "responder_name": "Alice",
                    "total_seconds_on_call": 86400,
                    "total_incident_count": 3,
                    "total_incidents_acknowledged": 3,
                    "total_sleep_hour_interruptions": 1,
                    "total_engaged_seconds": 3600,
                    "mean_time_to_acknowledge_seconds": 45,
                }
            ]
        }
        mock_get_client.return_value = mock_client

        request = GetResponderLoadMetricsRequest(
            filters=AnalyticsFilters(
                date_range_start="2026-03-01T00:00:00Z",
                date_range_end="2026-04-01T00:00:00Z",
            )
        )
        result = get_responder_load_metrics(request)

        import json
        data = json.loads(result)
        self.assertEqual(data["response"][0]["responder_name"], "Alice")
        mock_client.rpost.assert_called_once_with(
            "/analytics/metrics/responders/all",
            json={
                "filters": {
                    "date_range_start": "2026-03-01T00:00:00Z",
                    "date_range_end": "2026-04-01T00:00:00Z",
                }
            },
        )
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
python -m pytest tests/test_analytics.py -v 2>&1 | tail -20
```

Expected: `ImportError` or `AttributeError` — functions don't exist yet.

- [ ] **Step 3: Add 3 tool functions to `pagerduty_mcp/tools/analytics.py`**

Replace the entire contents of `pagerduty_mcp/tools/analytics.py` with:

```python
from pagerduty_mcp.client import get_client
from pagerduty_mcp.models.analytics import (
    AnalyticsResponderMetrics,
    AnalyticsServiceMetrics,
    AnalyticsTeamMetrics,
    AnalyticsResponderLoad,
    GetResponderMetricsRequest,
    GetIncidentMetricsByServiceRequest,
    GetIncidentMetricsByTeamRequest,
    GetResponderLoadMetricsRequest,
)
from pagerduty_mcp.models.base import ListResponseModel


def get_responder_metrics(request: GetResponderMetricsRequest) -> str:
    """Get responder metrics aggregated by team from PagerDuty Analytics.

    Returns per-user oncall seconds, interruption counts (business hours, off hours, sleep hours),
    engaged time, and incident counts for a given date range. Powered by PagerDuty's analytics
    engine — oncall hours are computed authoritatively, accounting for schedule overlaps.

    Args:
        request: Filters (required date range, optional team/responder/urgency filters),
                 time zone, and sort options.

    Returns:
        JSON string of ListResponseModel containing AnalyticsResponderMetrics objects.
    """
    body = request.to_body()
    response = get_client().rpost("/analytics/metrics/responders/teams", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsResponderMetrics(**item) for item in raw_data]
    return ListResponseModel[AnalyticsResponderMetrics](response=metrics).model_dump_json()


def get_incident_metrics_by_service(request: GetIncidentMetricsByServiceRequest) -> str:
    """Get aggregated incident metrics per service from PagerDuty Analytics.

    Returns service-level MTTA, MTTR percentiles (p50/p90), escalation counts, incident
    volume, and uptime percentage. Use this instead of list_incidents when you need
    service health metrics — data is pre-aggregated by PagerDuty's analytics engine.

    Args:
        request: Filters (required date range, optional team/service/urgency filters),
                 time zone, and sort options.

    Returns:
        JSON string of ListResponseModel containing AnalyticsServiceMetrics objects.
    """
    body = request.to_body()
    response = get_client().rpost("/analytics/metrics/incidents/services", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsServiceMetrics(**item) for item in raw_data]
    return ListResponseModel[AnalyticsServiceMetrics](response=metrics).model_dump_json()


def get_incident_metrics_by_team(request: GetIncidentMetricsByTeamRequest) -> str:
    """Get aggregated incident metrics per team from PagerDuty Analytics.

    Returns team-level MTTA, MTTR percentiles (p50/p90), escalation counts, incident
    volume, and uptime percentage. Use for team performance comparisons and dashboards.

    Args:
        request: Filters (required date range, optional team/service/urgency filters),
                 time zone, and sort options.

    Returns:
        JSON string of ListResponseModel containing AnalyticsTeamMetrics objects.
    """
    body = request.to_body()
    response = get_client().rpost("/analytics/metrics/incidents/teams", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsTeamMetrics(**item) for item in raw_data]
    return ListResponseModel[AnalyticsTeamMetrics](response=metrics).model_dump_json()


def get_responder_load_metrics(request: GetResponderLoadMetricsRequest) -> str:
    """Get aggregated load metrics per responder from PagerDuty Analytics.

    Returns per-responder on-call hours, incident count, acknowledgment count,
    sleep-hour interruptions, and engaged time. Use for responder workload analysis.

    Args:
        request: Filters (required date range, optional team/urgency filters),
                 time zone, and sort options.

    Returns:
        JSON string of ListResponseModel containing AnalyticsResponderLoad objects.
    """
    body = request.to_body()
    response = get_client().rpost("/analytics/metrics/responders/all", json=body)
    if isinstance(response, dict):
        raw_data = response.get("data", [])
    elif isinstance(response, list):
        raw_data = response
    else:
        raw_data = []
    metrics = [AnalyticsResponderLoad(**item) for item in raw_data]
    return ListResponseModel[AnalyticsResponderLoad](response=metrics).model_dump_json()
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
python -m pytest tests/test_analytics.py -v 2>&1 | tail -30
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Run full test suite to confirm no regressions**

```bash
python -m pytest tests/ -x -q 2>&1 | tail -10
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add pagerduty_mcp/tools/analytics.py tests/test_analytics.py
git commit -m "feat: add get_incident_metrics_by_service, get_incident_metrics_by_team, get_responder_load_metrics tools"
```

---

## Task 3: Register new tools in `__init__.py` and update server docstring

**Files:**
- Modify: `pagerduty_mcp/tools/__init__.py`
- Modify: `pagerduty_mcp/server.py`

- [ ] **Step 1: Export new tools from `__init__.py`**

In `pagerduty_mcp/tools/__init__.py`, find the line:
```python
from .analytics import get_responder_metrics
```
Replace it with:
```python
from .analytics import (
    get_incident_metrics_by_service,
    get_incident_metrics_by_team,
    get_responder_load_metrics,
    get_responder_metrics,
)
```

- [ ] **Step 2: Add new tools to `read_tools` list in `__init__.py`**

In `pagerduty_mcp/tools/__init__.py`, find the `read_tools` list (it contains `get_responder_metrics`). Add the 3 new functions to that list alongside it:

```python
    get_incident_metrics_by_service,
    get_incident_metrics_by_team,
    get_responder_load_metrics,
    get_responder_metrics,
```

- [ ] **Step 3: Update `add_operations_intelligence` docstring in `server.py`**

In `pagerduty_mcp/server.py`, find the `add_operations_intelligence` function and update the docstring comment to list the tools the UI now calls:

```python
def add_operations_intelligence(mcp_instance: FastMCP) -> None:
    """Add Operations Intelligence Report MCP App resource.

    The UI calls these MCP tools:
    - get_incident_metrics_by_service (Analytics API — service-level MTTA/MTTR/escalations)
    - get_incident_metrics_by_team (Analytics API — team-level MTTA/MTTR/escalations)
    - get_responder_load_metrics (Analytics API — responder on-call hours and interruptions)
    - list_teams (for team picker filter)
    - insights_agent_tool on pagerduty-advance-mcp (AI-powered insights tab)

    Args:
        mcp_instance: The MCP server instance
    """
```

Also update the tool docstring inside it:
```python
        """Operations Intelligence Report - Compact PagerDuty Insights dashboard.

        Two-tab dashboard: Operational (service/team/responder metrics from Analytics API)
        and Insights (AI-powered trend analysis via PagerDuty Advanced MCP insights_agent_tool).

        Returns:
            Text content indicating the UI is ready
        """
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
python -m pytest tests/ -x -q 2>&1 | tail -10
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add pagerduty_mcp/tools/__init__.py pagerduty_mcp/server.py
git commit -m "feat: register new analytics tools and update operations intelligence tool docstring"
```

---

## Task 4: Rewrite `api.ts` — new types and fetch functions

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/api.ts`

- [ ] **Step 1: Replace `api.ts` entirely**

```typescript
/**
 * Operations Intelligence v2 - API layer
 *
 * Fetches pre-aggregated metrics from PagerDuty Analytics API tools.
 * No raw incident list — all metrics are server-side aggregated.
 *
 * Insights tab calls insights_agent_tool on pagerduty-advance-mcp server.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Team {
  id: string;
  name: string;
}

export interface ServiceMetric {
  id: string;
  name: string;
  teamName: string | null;
  totalIncidents: number;
  mttaMinutes: number | null;       // mean_seconds_to_first_ack / 60
  mttrP50Minutes: number | null;    // p50_seconds_to_resolve / 60
  mttrP90Minutes: number | null;    // p90_seconds_to_resolve / 60
  escalationCount: number;
  uptimePct: number | null;
}

export interface TeamMetric {
  id: string;
  name: string;
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrP50Minutes: number | null;
  mttrP90Minutes: number | null;
  escalationCount: number;
  totalInterruptions: number;
  uptimePct: number | null;
}

export interface ResponderMetric {
  id: string;
  name: string;
  teamName: string | null;
  onCallHours: number;              // total_seconds_on_call / 3600
  totalIncidents: number;
  totalAcks: number;
  sleepInterruptions: number;
  engagedMinutes: number;           // total_engaged_seconds / 60
}

export interface OpsData {
  teams: Team[];
  selectedTeam: string | null;
  since: string;
  until: string;
  // KPI summary — derived from team aggregate (first entry when team filter applied,
  // or sum/avg across all teams when no filter)
  totalIncidents: number;
  mttaMinutes: number | null;
  mttrP50Minutes: number | null;
  mttrP90Minutes: number | null;
  escalationRate: number | null;    // pct: total_escalated / total_incidents * 100
  uptimePct: number | null;
  // Section data
  serviceMetrics: ServiceMetric[];
  teamMetrics: TeamMetric[];
  responderMetrics: ResponderMetric[];
}

export interface InsightMessage {
  role: "user" | "assistant";
  content: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

function secToMin(seconds: number | null | undefined): number | null {
  if (seconds == null) return null;
  return Math.round(seconds / 60);
}

function secToHours(seconds: number | null | undefined): number {
  if (seconds == null) return 0;
  return Math.round((seconds / 3600) * 10) / 10;
}

function buildIncidentFilters(since: string, until: string, teamId: string | null) {
  const filters: Record<string, unknown> = {
    created_at_start: since,
    created_at_end: until,
  };
  if (teamId) filters["team_ids"] = [teamId];
  return filters;
}

// ─── Operational data fetch ───────────────────────────────────────────────────

export async function fetchOpsData(
  app: App,
  since: string,
  until: string,
  teamId: string | null
): Promise<OpsData> {
  const incidentFilters = buildIncidentFilters(since, until, teamId);
  // Responder endpoint uses date_range_start/end (different field names)
  const responderFilters: Record<string, unknown> = {
    date_range_start: since,
    date_range_end: until,
  };
  if (teamId) responderFilters["team_ids"] = [teamId];

  const [teamsResult, serviceResult, teamResult, responderResult] = await Promise.allSettled([
    app.callServerTool({ name: "list_teams", arguments: { query_model: { limit: 100 } } }),
    app.callServerTool({
      name: "get_incident_metrics_by_service",
      arguments: { filters: incidentFilters },
    }),
    app.callServerTool({
      name: "get_incident_metrics_by_team",
      arguments: { filters: incidentFilters },
    }),
    app.callServerTool({
      name: "get_responder_load_metrics",
      arguments: { filters: responderFilters },
    }),
  ]);

  // Teams
  const teamsData = teamsResult.status === "fulfilled" ? extract<any>(teamsResult.value) : null;
  const teams: Team[] = (teamsData?.response ?? []).map((t: any) => ({
    id: t.id,
    name: t.name ?? t.summary,
  }));

  // Service metrics
  const svcData = serviceResult.status === "fulfilled" ? extract<any>(serviceResult.value) : null;
  const serviceMetrics: ServiceMetric[] = (svcData?.response ?? []).map((s: any) => ({
    id: s.service_id ?? "",
    name: s.service_name ?? "Unknown",
    teamName: s.team_name ?? null,
    totalIncidents: s.total_incident_count ?? 0,
    mttaMinutes: secToMin(s.mean_seconds_to_first_ack),
    mttrP50Minutes: secToMin(s.p50_seconds_to_resolve),
    mttrP90Minutes: secToMin(s.p90_seconds_to_resolve),
    escalationCount: s.total_escalation_count ?? s.total_incidents_manual_escalated ?? 0,
    uptimePct: s.up_time_pct ?? null,
  }));

  // Team metrics
  const teamData = teamResult.status === "fulfilled" ? extract<any>(teamResult.value) : null;
  const teamMetrics: TeamMetric[] = (teamData?.response ?? []).map((t: any) => ({
    id: t.team_id ?? "",
    name: t.team_name ?? "Unknown",
    totalIncidents: t.total_incident_count ?? 0,
    mttaMinutes: secToMin(t.mean_seconds_to_first_ack),
    mttrP50Minutes: secToMin(t.p50_seconds_to_resolve),
    mttrP90Minutes: secToMin(t.p90_seconds_to_resolve),
    escalationCount: t.total_escalation_count ?? t.total_incidents_manual_escalated ?? 0,
    totalInterruptions: t.total_interruptions ?? 0,
    uptimePct: t.up_time_pct ?? null,
  }));

  // Responder metrics
  const respData = responderResult.status === "fulfilled" ? extract<any>(responderResult.value) : null;
  const responderMetrics: ResponderMetric[] = (respData?.response ?? []).map((r: any) => ({
    id: r.responder_id ?? "",
    name: r.responder_name ?? "Unknown",
    teamName: r.team_name ?? null,
    onCallHours: secToHours(r.total_seconds_on_call),
    totalIncidents: r.total_incident_count ?? 0,
    totalAcks: r.total_incidents_acknowledged ?? 0,
    sleepInterruptions: r.total_sleep_hour_interruptions ?? 0,
    engagedMinutes: secToMin(r.total_engaged_seconds) ?? 0,
  }));

  // KPI summary — aggregate across all returned teams
  const totalIncidents = teamMetrics.reduce((s, t) => s + t.totalIncidents, 0);
  const totalEscalations = teamMetrics.reduce((s, t) => s + t.escalationCount, 0);
  const mttaValues = teamMetrics.map((t) => t.mttaMinutes).filter((v): v is number => v !== null);
  const mttrP50Values = teamMetrics.map((t) => t.mttrP50Minutes).filter((v): v is number => v !== null);
  const mttrP90Values = teamMetrics.map((t) => t.mttrP90Minutes).filter((v): v is number => v !== null);
  const avg = (arr: number[]) => arr.length === 0 ? null : Math.round(arr.reduce((a, b) => a + b, 0) / arr.length);

  // uptime: average across services (more meaningful than teams)
  const uptimeValues = serviceMetrics.map((s) => s.uptimePct).filter((v): v is number => v !== null);
  const uptimePct = uptimeValues.length > 0
    ? Math.round((uptimeValues.reduce((a, b) => a + b, 0) / uptimeValues.length) * 10) / 10
    : null;

  return {
    teams,
    selectedTeam: teamId,
    since,
    until,
    totalIncidents,
    mttaMinutes: avg(mttaValues),
    mttrP50Minutes: avg(mttrP50Values),
    mttrP90Minutes: avg(mttrP90Values),
    escalationRate: totalIncidents > 0 ? Math.round((totalEscalations / totalIncidents) * 100) : null,
    uptimePct,
    serviceMetrics,
    teamMetrics,
    responderMetrics,
  };
}

// ─── Insights fetch (PagerDuty Advanced MCP) ─────────────────────────────────

export async function fetchInsight(
  app: App,
  message: string,
  sessionId: string
): Promise<string> {
  const result = await app.callServerTool({
    name: "insights_agent_tool",
    arguments: { message, session_id: sessionId },
  });
  const data = extract<{ message: string }>(result);
  return data?.message ?? "";
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
npm run typecheck 2>&1 | tail -20
```

Expected: no errors (some may appear until later tasks update the components that import from api.ts — that's OK for now).

- [ ] **Step 3: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/operations-intelligence/src/api.ts
git commit -m "feat: rewrite operations intelligence api.ts to use Analytics API and insights_agent_tool"
```

---

## Task 5: New shared CSS styles

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/styles.css`

- [ ] **Step 1: Append new styles to the end of `styles.css`**

Add the following at the bottom of the existing file (do not remove existing styles):

```css
/* ── Tabs ── */
.tabs {
  display: flex;
  gap: 2px;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.tab-btn {
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  margin-bottom: -1px;
}

.tab-btn:hover { color: var(--text-primary); }
.tab-btn.tab-active { color: var(--pd-green); border-bottom-color: var(--pd-green); }

/* ── Analytics tables (shared by ServiceBreakdown, TeamBreakdown, ResponderLoad) ── */
.analytics-section { padding: 16px 20px; border-bottom: 1px solid var(--border-primary); }

.analytics-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.analytics-table th {
  text-align: left;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border-primary);
  white-space: nowrap;
}

.analytics-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-primary);
}

.analytics-table tr:last-child td { border-bottom: none; }
.analytics-table tr:hover td { background: var(--bg-secondary); }

.analytics-table .col-name { font-weight: 500; }
.analytics-table .col-mono { font-family: monospace; font-size: 12px; }
.analytics-table .col-num { text-align: right; }
.analytics-table .col-warn { color: var(--color-escalation); font-weight: 600; }
.analytics-table .col-ok { color: var(--status-resolved); }

/* ── KPI summary bar ── */
.kpi-bar {
  display: flex;
  gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-primary);
  flex-wrap: wrap;
}

.kpi-card {
  flex: 1;
  min-width: 110px;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
}

.kpi-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.kpi-value { font-size: 22px; font-weight: 700; }
.kpi-sub { font-size: 11px; color: var(--text-tertiary); margin-top: 2px; }

/* ── Insights tab ── */
.insights-tab { display: flex; flex-direction: column; flex: 1; overflow: hidden; }

.insight-cards {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--border-primary);
}

.insight-card {
  flex: 1;
  min-width: 260px;
  max-width: 400px;
  padding: 14px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
}

.insight-card-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}

.insight-card-body { font-size: 13px; line-height: 1.6; color: var(--text-primary); }

.insight-skeleton {
  background: var(--bg-tertiary);
  border-radius: 4px;
  height: 12px;
  margin-bottom: 6px;
  animation: pulse 1.5s ease-in-out infinite;
}
.insight-skeleton:last-child { width: 60%; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.insight-error {
  font-size: 12px;
  color: var(--status-triggered);
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Chat panel ── */
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 20px;
  overflow: hidden;
  min-height: 200px;
}

.chat-panel-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 0 8px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 8px;
}

.chat-message { display: flex; flex-direction: column; gap: 2px; }
.chat-message-role { font-size: 10px; font-weight: 700; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.06em; }
.chat-message-content { font-size: 13px; line-height: 1.6; color: var(--text-primary); white-space: pre-wrap; }
.chat-message.chat-user .chat-message-role { color: var(--pd-green); }

.chat-input-row {
  display: flex;
  gap: 8px;
  padding: 10px 0 14px;
  border-top: 1px solid var(--border-primary);
}

.chat-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  resize: none;
  min-height: 36px;
  max-height: 100px;
}

.chat-input:focus { outline: none; border-color: var(--pd-green); }
```

- [ ] **Step 2: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/operations-intelligence/src/styles.css
git commit -m "feat: add tab, KPI bar, analytics table, insight card, and chat CSS styles"
```

---

## Task 6: Replace `SummaryCards.tsx` with KPI bar

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/components/SummaryCards.tsx`

- [ ] **Step 1: Replace the file entirely**

```tsx
import type { OpsData } from "../api";

function fmtMin(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}m`;
}

interface KpiCardProps {
  label: string;
  value: string;
  sub?: string;
  warn?: boolean;
}

function KpiCard({ label, value, sub, warn }: KpiCardProps) {
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={warn ? { color: "var(--color-escalation)" } : undefined}>
        {value}
      </div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

export function SummaryCards({ data }: { data: OpsData }) {
  return (
    <div className="kpi-bar">
      <KpiCard
        label="Total Incidents"
        value={String(data.totalIncidents)}
        sub={`${data.teamMetrics.length} team${data.teamMetrics.length !== 1 ? "s" : ""}`}
      />
      <KpiCard
        label="MTTA"
        value={fmtMin(data.mttaMinutes)}
        sub="mean time to ack"
        warn={data.mttaMinutes !== null && data.mttaMinutes > 30}
      />
      <KpiCard
        label="MTTR p50"
        value={fmtMin(data.mttrP50Minutes)}
        sub={`p90: ${fmtMin(data.mttrP90Minutes)}`}
        warn={data.mttrP50Minutes !== null && data.mttrP50Minutes > 60}
      />
      <KpiCard
        label="Escalation Rate"
        value={data.escalationRate !== null ? `${data.escalationRate}%` : "—"}
        sub="of all incidents"
        warn={data.escalationRate !== null && data.escalationRate > 20}
      />
      <KpiCard
        label="Avg Uptime"
        value={data.uptimePct !== null ? `${data.uptimePct}%` : "—"}
        sub="across services"
        warn={data.uptimePct !== null && data.uptimePct < 99}
      />
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/operations-intelligence/src/components/SummaryCards.tsx
git commit -m "feat: replace SummaryCards with analytics-driven KPI bar (MTTA, MTTR p50/p90, escalation rate, uptime)"
```

---

## Task 7: Replace `ServiceBreakdown.tsx` with analytics table

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/components/ServiceBreakdown.tsx`

- [ ] **Step 1: Replace the file entirely**

```tsx
import type { ServiceMetric } from "../api";

function fmtMin(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export function ServiceBreakdown({ metrics }: { metrics: ServiceMetric[] }) {
  return (
    <div className="analytics-section">
      <div className="section-title">Service Performance</div>
      {metrics.length === 0 ? (
        <div className="empty-state">No service data for this period</div>
      ) : (
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Service</th>
              <th className="col-num">Incidents</th>
              <th className="col-num">MTTA</th>
              <th className="col-num">MTTR p50</th>
              <th className="col-num">MTTR p90</th>
              <th className="col-num">Escalations</th>
              <th className="col-num">Uptime</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((s) => (
              <tr key={s.id}>
                <td className="col-name">
                  {s.name}
                  {s.teamName && <span className="kpi-sub"> · {s.teamName}</span>}
                </td>
                <td className="col-num">{s.totalIncidents}</td>
                <td className={`col-mono col-num${s.mttaMinutes !== null && s.mttaMinutes > 30 ? " col-warn" : ""}`}>
                  {fmtMin(s.mttaMinutes)}
                </td>
                <td className={`col-mono col-num${s.mttrP50Minutes !== null && s.mttrP50Minutes > 60 ? " col-warn" : ""}`}>
                  {fmtMin(s.mttrP50Minutes)}
                </td>
                <td className="col-mono col-num">{fmtMin(s.mttrP90Minutes)}</td>
                <td className={`col-num${s.escalationCount > 0 ? " col-warn" : " col-ok"}`}>
                  {s.escalationCount}
                </td>
                <td className={`col-num${s.uptimePct !== null && s.uptimePct < 99 ? " col-warn" : " col-ok"}`}>
                  {s.uptimePct !== null ? `${s.uptimePct}%` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/operations-intelligence/src/components/ServiceBreakdown.tsx
git commit -m "feat: rewrite ServiceBreakdown with analytics columns (MTTA, MTTR p50/p90, escalations, uptime)"
```

---

## Task 8: Add `TeamBreakdown.tsx` and `ResponderLoad.tsx`

**Files:**
- Create: `mcp-apps/operations-intelligence/src/components/TeamBreakdown.tsx`
- Create: `mcp-apps/operations-intelligence/src/components/ResponderLoad.tsx`

- [ ] **Step 1: Create `TeamBreakdown.tsx`**

```tsx
import type { TeamMetric } from "../api";

function fmtMin(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export function TeamBreakdown({ metrics }: { metrics: TeamMetric[] }) {
  return (
    <div className="analytics-section">
      <div className="section-title">Team Performance</div>
      {metrics.length === 0 ? (
        <div className="empty-state">No team data for this period</div>
      ) : (
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Team</th>
              <th className="col-num">Incidents</th>
              <th className="col-num">MTTA</th>
              <th className="col-num">MTTR p50</th>
              <th className="col-num">Escalations</th>
              <th className="col-num">Interruptions</th>
              <th className="col-num">Uptime</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((t) => (
              <tr key={t.id}>
                <td className="col-name">{t.name}</td>
                <td className="col-num">{t.totalIncidents}</td>
                <td className={`col-mono col-num${t.mttaMinutes !== null && t.mttaMinutes > 30 ? " col-warn" : ""}`}>
                  {fmtMin(t.mttaMinutes)}
                </td>
                <td className={`col-mono col-num${t.mttrP50Minutes !== null && t.mttrP50Minutes > 60 ? " col-warn" : ""}`}>
                  {fmtMin(t.mttrP50Minutes)}
                </td>
                <td className={`col-num${t.escalationCount > 0 ? " col-warn" : " col-ok"}`}>
                  {t.escalationCount}
                </td>
                <td className={`col-num${t.totalInterruptions > 10 ? " col-warn" : ""}`}>
                  {t.totalInterruptions}
                </td>
                <td className={`col-num${t.uptimePct !== null && t.uptimePct < 99 ? " col-warn" : " col-ok"}`}>
                  {t.uptimePct !== null ? `${t.uptimePct}%` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create `ResponderLoad.tsx`**

```tsx
import type { ResponderMetric } from "../api";

function fmtHours(h: number): string {
  return `${h}h`;
}

function fmtMin(minutes: number): string {
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export function ResponderLoad({ metrics }: { metrics: ResponderMetric[] }) {
  return (
    <div className="analytics-section">
      <div className="section-title">Responder Load</div>
      {metrics.length === 0 ? (
        <div className="empty-state">No responder data for this period</div>
      ) : (
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Responder</th>
              <th className="col-num">On-call hrs</th>
              <th className="col-num">Incidents</th>
              <th className="col-num">Acks</th>
              <th className="col-num">Sleep interruptions</th>
              <th className="col-num">Engaged time</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((r) => (
              <tr key={r.id}>
                <td className="col-name">
                  {r.name}
                  {r.teamName && <span className="kpi-sub"> · {r.teamName}</span>}
                </td>
                <td className="col-num col-mono">{fmtHours(r.onCallHours)}</td>
                <td className="col-num">{r.totalIncidents}</td>
                <td className="col-num">{r.totalAcks}</td>
                <td className={`col-num${r.sleepInterruptions > 0 ? " col-warn" : " col-ok"}`}>
                  {r.sleepInterruptions}
                </td>
                <td className="col-num col-mono">{fmtMin(r.engagedMinutes)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/operations-intelligence/src/components/TeamBreakdown.tsx \
        mcp-apps/operations-intelligence/src/components/ResponderLoad.tsx
git commit -m "feat: add TeamBreakdown and ResponderLoad analytics table components"
```

---

## Task 9: Add `InsightCard.tsx`, `InsightsChat.tsx`, and `InsightsTab.tsx`

**Files:**
- Create: `mcp-apps/operations-intelligence/src/components/InsightCard.tsx`
- Create: `mcp-apps/operations-intelligence/src/components/InsightsChat.tsx`
- Create: `mcp-apps/operations-intelligence/src/components/InsightsTab.tsx`

- [ ] **Step 1: Create `InsightCard.tsx`**

```tsx
interface InsightCardProps {
  title: string;
  content: string | null;  // null = loading
  error?: string | null;
  onRetry?: () => void;
}

export function InsightCard({ title, content, error, onRetry }: InsightCardProps) {
  return (
    <div className="insight-card">
      <div className="insight-card-title">{title}</div>
      {error ? (
        <div className="insight-error">
          Could not load insight.
          {onRetry && (
            <button className="btn btn-sm" onClick={onRetry} style={{ marginLeft: 8 }}>
              Retry
            </button>
          )}
        </div>
      ) : content === null ? (
        <>
          <div className="insight-skeleton" style={{ width: "90%" }} />
          <div className="insight-skeleton" style={{ width: "75%" }} />
          <div className="insight-skeleton" style={{ width: "80%" }} />
          <div className="insight-skeleton" />
        </>
      ) : (
        <div className="insight-card-body">{content}</div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create `InsightsChat.tsx`**

```tsx
import { useRef, useState } from "react";
import type { InsightMessage } from "../api";

interface InsightsChatProps {
  messages: InsightMessage[];
  loading: boolean;
  onSend: (message: string) => void;
}

export function InsightsChat({ messages, loading, onSend }: InsightsChatProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  function handleSend() {
    const msg = input.trim();
    if (!msg || loading) return;
    setInput("");
    onSend(msg);
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-panel-title">Ask a follow-up question</div>
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state" style={{ padding: "20px 0" }}>
            Ask anything about your operational metrics, trends, or team performance.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-message ${m.role === "user" ? "chat-user" : "chat-assistant"}`}>
            <div className="chat-message-role">{m.role === "user" ? "You" : "Insights Agent"}</div>
            <div className="chat-message-content">{m.content}</div>
          </div>
        ))}
        {loading && (
          <div className="chat-message chat-assistant">
            <div className="chat-message-role">Insights Agent</div>
            <div className="insight-skeleton" style={{ width: "60%", marginTop: 4 }} />
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-row">
        <textarea
          className="chat-input"
          placeholder="e.g. Which team had the most sleep interruptions last month?"
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={loading}
        />
        <button
          className="btn btn-primary btn-sm"
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create `InsightsTab.tsx`**

```tsx
import { useCallback, useEffect, useRef, useState } from "react";
import type { App } from "@modelcontextprotocol/ext-apps";
import { fetchInsight, type InsightMessage } from "../api";
import { InsightCard } from "./InsightCard";
import { InsightsChat } from "./InsightsChat";

interface InsightsTabProps {
  app: App;
  teamName: string;
  since: string;
  until: string;
  refreshKey: number;  // increment to trigger re-fetch
}

interface AutoInsight {
  title: string;
  query: string;
  content: string | null;
  error: string | null;
}

export function InsightsTab({ app, teamName, since, until, refreshKey }: InsightsTabProps) {
  const sessionId = useRef(crypto.randomUUID());
  const team = teamName || "all teams";

  const [insights, setInsights] = useState<AutoInsight[]>([
    {
      title: "MTTA & MTTR Trends",
      query: `Summarize MTTA and MTTR trends for ${team} between ${since} and ${until}. Highlight any notable changes or anomalies.`,
      content: null,
      error: null,
    },
    {
      title: "Noisiest Services",
      query: `Which services have the highest incident volume and worst resolution times for ${team} between ${since} and ${until}?`,
      content: null,
      error: null,
    },
    {
      title: "Team & Responder Load",
      query: `How is ${team} performing in terms of escalations, on-call interruptions, and responder load between ${since} and ${until}?`,
      content: null,
      error: null,
    },
  ]);

  const [chatMessages, setChatMessages] = useState<InsightMessage[]>([]);
  const [chatLoading, setChatLoading] = useState(false);

  const loadInsight = useCallback(
    async (idx: number, query: string) => {
      setInsights((prev) =>
        prev.map((ins, i) => (i === idx ? { ...ins, content: null, error: null } : ins))
      );
      try {
        const content = await fetchInsight(app, query, sessionId.current);
        setInsights((prev) =>
          prev.map((ins, i) => (i === idx ? { ...ins, content } : ins))
        );
      } catch {
        setInsights((prev) =>
          prev.map((ins, i) =>
            i === idx ? { ...ins, error: "Failed to load insight" } : ins
          )
        );
      }
    },
    [app]
  );

  // Load all 3 auto-insights on mount and when refreshKey changes
  useEffect(() => {
    sessionId.current = crypto.randomUUID();
    setChatMessages([]);
    const queries: [string, string, string] = [
      `Summarize MTTA and MTTR trends for ${team} between ${since} and ${until}. Highlight any notable changes or anomalies.`,
      `Which services have the highest incident volume and worst resolution times for ${team} between ${since} and ${until}?`,
      `How is ${team} performing in terms of escalations, on-call interruptions, and responder load between ${since} and ${until}?`,
    ];
    setInsights((prev) =>
      prev.map((ins, i) => ({ ...ins, query: queries[i]!, content: null, error: null }))
    );
    queries.forEach((q, i) => loadInsight(i, q));
  }, [refreshKey]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSend(message: string) {
    setChatMessages((prev) => [...prev, { role: "user", content: message }]);
    setChatLoading(true);
    try {
      const reply = await fetchInsight(app, message, sessionId.current);
      setChatMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't process that request. Please try again." },
      ]);
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <div className="insights-tab">
      <div className="insight-cards">
        {insights.map((ins, i) => (
          <InsightCard
            key={i}
            title={ins.title}
            content={ins.content}
            error={ins.error}
            onRetry={() => loadInsight(i, ins.query)}
          />
        ))}
      </div>
      <InsightsChat
        messages={chatMessages}
        loading={chatLoading}
        onSend={handleSend}
      />
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/operations-intelligence/src/components/InsightCard.tsx \
        mcp-apps/operations-intelligence/src/components/InsightsChat.tsx \
        mcp-apps/operations-intelligence/src/components/InsightsTab.tsx
git commit -m "feat: add InsightCard, InsightsChat, and InsightsTab components for AI insights"
```

---

## Task 10: Rewrite `mcp-app.tsx` — tabs and Operational view

**Files:**
- Modify: `mcp-apps/operations-intelligence/src/mcp-app.tsx`
- Delete: `mcp-apps/operations-intelligence/src/components/IncidentTable.tsx`

- [ ] **Step 1: Delete `IncidentTable.tsx`**

```bash
rm /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence/src/components/IncidentTable.tsx
```

- [ ] **Step 2: Replace `mcp-app.tsx` entirely**

```tsx
/**
 * Operations Intelligence v2 - Main App
 *
 * Two tabs:
 *   Operational: KPI bar + Service / Team / Responder metric tables
 *   Insights:    Auto-generated AI summary cards + follow-up chat
 */

import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchOpsData, type OpsData } from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { SummaryCards } from "./components/SummaryCards";
import { ServiceBreakdown } from "./components/ServiceBreakdown";
import { TeamBreakdown } from "./components/TeamBreakdown";
import { ResponderLoad } from "./components/ResponderLoad";
import { InsightsTab } from "./components/InsightsTab";

type Tab = "operational" | "insights";

function getDefaultSince(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().split("T")[0]!;
}

function getToday(): string {
  return new Date().toISOString().split("T")[0]!;
}

function detectTheme(): "dark" | "light" {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Operations Intelligence", version: "2.0.0" },
    capabilities: {},
  });

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [tab, setTab] = useState<Tab>("operational");
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);
  const [selectedTeam, setSelectedTeam] = useState<string>("");
  // refreshKey increments on each Refresh click to trigger InsightsTab re-fetch
  const [refreshKey, setRefreshKey] = useState(0);

  const [data, setData] = useState<OpsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if ((ctx as any).theme) setTheme((ctx as any).theme === "dark" ? "dark" : "light");
    };
  }, [app]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const load = useCallback(async () => {
    if (!app) return;
    setLoading(true);
    setError(null);
    setRefreshKey((k) => k + 1);
    try {
      const d = await fetchOpsData(
        app,
        new Date(since).toISOString(),
        new Date(until + "T23:59:59").toISOString(),
        selectedTeam || null
      );
      setData(d);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [app, since, until, selectedTeam]);

  useEffect(() => {
    load();
  }, [load]);

  const selectedTeamName = useMemo(() => {
    if (!selectedTeam || !data) return "";
    return data.teams.find((t) => t.id === selectedTeam)?.name ?? "";
  }, [selectedTeam, data]);

  const displayError = connectionError?.message ?? error;

  return (
    <div className="app">
      <header className="app-header">
        <span className="pd-icon"><PagerDutyLogo size={22} /></span>
        <h1>Operations Intelligence</h1>
      </header>

      <div className="controls">
        <label>Team</label>
        <select value={selectedTeam} onChange={(e) => setSelectedTeam(e.currentTarget.value)}>
          <option value="">All teams</option>
          {(data?.teams ?? []).map((t) => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
        <label>From</label>
        <input type="date" value={since} onChange={(e) => setSince(e.currentTarget.value)} />
        <label>To</label>
        <input type="date" value={until} onChange={(e) => setUntil(e.currentTarget.value)} />
        <button className="btn btn-primary btn-sm" onClick={load} disabled={loading}>
          {loading ? "Loading…" : "Refresh"}
        </button>
      </div>

      <div className="tabs">
        <button
          className={`tab-btn${tab === "operational" ? " tab-active" : ""}`}
          onClick={() => setTab("operational")}
        >
          Operational
        </button>
        <button
          className={`tab-btn${tab === "insights" ? " tab-active" : ""}`}
          onClick={() => setTab("insights")}
        >
          Insights
        </button>
      </div>

      {displayError && <div className="error-state">{displayError}</div>}

      {loading && !data ? (
        <div className="loading">Loading operational data…</div>
      ) : tab === "operational" && data ? (
        <div className="body">
          <SummaryCards data={data} />
          <ServiceBreakdown metrics={data.serviceMetrics} />
          <TeamBreakdown metrics={data.teamMetrics} />
          <ResponderLoad metrics={data.responderMetrics} />
        </div>
      ) : tab === "insights" && app ? (
        <InsightsTab
          app={app}
          teamName={selectedTeamName}
          since={since}
          until={until}
          refreshKey={refreshKey}
        />
      ) : null}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

- [ ] **Step 3: Run TypeScript typecheck**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
npm run typecheck 2>&1 | tail -20
```

Expected: 0 errors.

- [ ] **Step 4: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/operations-intelligence/src/mcp-app.tsx
git rm mcp-apps/operations-intelligence/src/components/IncidentTable.tsx
git commit -m "feat: rewrite mcp-app.tsx with two-tab layout (Operational + Insights), remove IncidentTable"
```

---

## Task 11: Build and deploy the frontend bundle

**Files:**
- Regenerate: `pagerduty_mcp/operations_intelligence_view.html`

- [ ] **Step 1: Install dependencies (if needed)**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use
npm install 2>&1 | tail -5
```

Expected: clean install, no errors.

- [ ] **Step 2: Build the frontend bundle**

```bash
npm run build 2>&1 | tail -20
```

Expected: `dist/mcp-app.html` created, no TypeScript errors, no Rollup errors.

- [ ] **Step 3: Copy bundle to Python server**

```bash
cp dist/mcp-app.html /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/pagerduty_mcp/operations_intelligence_view.html
```

- [ ] **Step 4: Verify the HTML file was updated**

```bash
wc -c /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/pagerduty_mcp/operations_intelligence_view.html
```

Expected: file size > 50KB (bundled React app).

- [ ] **Step 5: Run Python tests one final time**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
python -m pytest tests/ -x -q 2>&1 | tail -10
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add pagerduty_mcp/operations_intelligence_view.html
git commit -m "feat: build and deploy Operations Intelligence v2 frontend bundle"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] Two-tab layout (Operational + Insights) → Task 10
- [x] KPI summary bar: Total Incidents, MTTA, MTTR p50/p90, Escalation Rate, Uptime → Tasks 4, 6
- [x] Service Performance table with MTTA, MTTR p50, escalations, uptime → Tasks 4, 7
- [x] Team Performance table → Tasks 4, 8
- [x] Responder Load table → Tasks 4, 8
- [x] `get_incident_metrics_by_service` backend tool → Tasks 1, 2, 3
- [x] `get_incident_metrics_by_team` backend tool → Tasks 1, 2, 3
- [x] `get_responder_load_metrics` backend tool → Tasks 1, 2, 3
- [x] InsightCard with loading skeleton → Task 9
- [x] Auto-fire 3 pre-written queries on Insights tab load → Task 9 (InsightsTab.tsx)
- [x] Chat follow-up panel → Task 9
- [x] `insights_agent_tool` call via `pagerduty-advance-mcp` server → Task 4 (`fetchInsight`)
- [x] IncidentTable removed → Task 10
- [x] Frontend bundle regenerated → Task 11

**Type consistency check:**
- `ServiceMetric` defined in `api.ts` Task 4, used in `ServiceBreakdown.tsx` Task 7 ✓
- `TeamMetric` defined Task 4, used in `TeamBreakdown.tsx` Task 8 ✓
- `ResponderMetric` defined Task 4, used in `ResponderLoad.tsx` Task 8 ✓
- `InsightMessage` defined Task 4, used in `InsightsChat.tsx` Task 9 ✓
- `fetchInsight` defined Task 4, called in `InsightsTab.tsx` Task 9 ✓
- `OpsData` fields `serviceMetrics`, `teamMetrics`, `responderMetrics` defined Task 4, read in `mcp-app.tsx` Task 10 ✓
- `refreshKey` prop on `InsightsTab` defined in `InsightsTab.tsx` Task 9, passed from `mcp-app.tsx` Task 10 ✓
