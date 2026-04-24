# On-Call Manager V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the On-Call Manager MCP app into a 4-card home screen (My On-Calls, Overrides, Schedules, Escalation Policies) with full end-to-end create/edit/delete capabilities for all four domains, plus fix the "No users found" bug and add user-colored timeline bars.

**Architecture:** New Python tools for missing operations (list/delete overrides, create/update/delete escalation policies) land first; the React app is then fully replaced — `mcp-app.tsx` becomes a home screen with modal routing, existing tab components are converted to modals, and two new modals (Schedules, Escalation Policies) are added. A `userColor` utility provides consistent per-user palette colors.

**Tech Stack:** Python/FastMCP (pdpyras client), React 18 + Preact compat, TypeScript 5, Vite singlefile, Catppuccin Mocha palette.

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Modify | `pagerduty_mcp/tools/schedules.py` | Add `list_schedule_overrides`, `delete_schedule_override` |
| Modify | `pagerduty_mcp/models/schedules.py` | Add `ScheduleOverrideDetail` model |
| Modify | `pagerduty_mcp/tools/escalation_policies.py` | Add `create_escalation_policy`, `update_escalation_policy`, `delete_escalation_policy` |
| Modify | `pagerduty_mcp/models/escalation_policies.py` | Add `EscalationPolicyCreate` model |
| Modify | `pagerduty_mcp/tools/__init__.py` | Register all new tools |
| Modify | `mcp-apps/oncall-manager/src/api.ts` | New types + 10 new API functions, fix `fetchScheduleUsers` fallback |
| Modify | `mcp-apps/oncall-manager/src/mock.ts` | Extend with overrides-per-schedule, schedule detail, escalation policies |
| Modify | `mcp-apps/oncall-manager/src/styles.css` | Home cards, modal overlay, user color vars, availability badges |
| Create | `mcp-apps/oncall-manager/src/utils/userColor.ts` | Hash userId → palette color |
| Replace | `mcp-apps/oncall-manager/src/mcp-app.tsx` | Home screen: 4 cards + modal routing |
| Replace | `mcp-apps/oncall-manager/src/components/MyOnCalls.tsx` | Modal variant: colored bars, no empty rows |
| Replace | `mcp-apps/oncall-manager/src/components/CoverageWizard.tsx` | Fix user fallback + availability badges |
| Replace | `mcp-apps/oncall-manager/src/components/OverridesTab.tsx` → `OverridesModal.tsx` | Real override list with delete |
| Create | `mcp-apps/oncall-manager/src/components/SchedulesModal.tsx` | List → detail → edit layers |
| Create | `mcp-apps/oncall-manager/src/components/EscalationPoliciesModal.tsx` | List → detail → edit rules |

---

## Task 1: Python — new schedule override tools

**Files:**
- Modify: `pagerduty_mcp/models/schedules.py`
- Modify: `pagerduty_mcp/tools/schedules.py`

- [ ] **Step 1: Add `ScheduleOverrideDetail` model to models/schedules.py**

Add after the existing `Override` class (around line 118):

```python
class ScheduleOverrideUser(BaseModel):
    id: str
    name: str | None = None
    summary: str | None = None
    type: str | None = None


class ScheduleOverrideDetail(BaseModel):
    id: str
    start: datetime
    end: datetime
    user: ScheduleOverrideUser
```

Also update the `__init__.py` for models to export it. Check `pagerduty_mcp/models/__init__.py` and add `ScheduleOverrideDetail, ScheduleOverrideUser` to the import from `.schedules`.

- [ ] **Step 2: Add `list_schedule_overrides` and `delete_schedule_override` to tools/schedules.py**

Add `import json` at the top if not present. Add these two functions after `list_schedule_users`:

```python
def list_schedule_overrides(schedule_id: str, since: str, until: str) -> str:
    """List overrides for a schedule within a date range.

    Args:
        schedule_id: The ID of the schedule
        since: Start of the date range (ISO 8601)
        until: End of the date range (ISO 8601)

    Returns:
        JSON string with an 'overrides' array
    """
    import json
    response = get_client().rget(
        f"/schedules/{schedule_id}/overrides",
        params={"since": since, "until": until},
    )
    # rget returns the full response dict: {"overrides": [...]}
    overrides = response.get("overrides", []) if isinstance(response, dict) else []
    return json.dumps({"overrides": overrides})


def delete_schedule_override(schedule_id: str, override_id: str) -> str:
    """Delete a schedule override.

    Args:
        schedule_id: The ID of the schedule
        override_id: The ID of the override to delete

    Returns:
        JSON string confirming deletion
    """
    import json
    get_client().rdelete(f"/schedules/{schedule_id}/overrides/{override_id}")
    return json.dumps({"success": True})
```

- [ ] **Step 3: Commit**

```bash
git add pagerduty_mcp/models/schedules.py pagerduty_mcp/tools/schedules.py
git commit -m "feat: add list_schedule_overrides and delete_schedule_override tools"
```

---

## Task 2: Python — escalation policy write tools

**Files:**
- Modify: `pagerduty_mcp/models/escalation_policies.py`
- Modify: `pagerduty_mcp/tools/escalation_policies.py`

- [ ] **Step 1: Add `EscalationPolicyCreate` model to models/escalation_policies.py**

Add after the `EscalationPolicyQuery` class:

```python
class EscalationPolicyCreate(BaseModel):
    name: str = Field(description="The name of the escalation policy")
    description: str | None = Field(default=None, description="Description of the policy")
    num_loops: int = Field(default=0, description="Number of times the policy repeats after reaching the end")
    escalation_rules: list[EscalationRule] = Field(description="Ordered list of escalation rules")
    on_call_handoff_notifications: Literal["if_has_services", "always"] | None = Field(
        default="if_has_services",
        description="When to send on-call handoff notifications",
    )
    teams: list[TeamReference] | None = Field(default=None, description="Teams to associate")
```

- [ ] **Step 2: Add write functions to tools/escalation_policies.py**

Replace the full file content with:

```python
import json

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import (
    EscalationPolicy,
    EscalationPolicyCreate,
    EscalationPolicyQuery,
    ListResponseModel,
)
from pagerduty_mcp.utils import paginate


def list_escalation_policies(
    query_model: EscalationPolicyQuery,
) -> str:
    """List escalation policies with optional filtering."""
    response = paginate(client=get_client(), entity="escalation_policies", params=query_model.to_params())
    policies = [EscalationPolicy(**policy) for policy in response]
    return ListResponseModel[EscalationPolicy](response=policies).model_dump_json()


def get_escalation_policy(policy_id: str) -> str:
    """Get a specific escalation policy."""
    response = get_client().rget(f"/escalation_policies/{policy_id}")
    return EscalationPolicy.model_validate(response).model_dump_json()


def create_escalation_policy(escalation_policy: EscalationPolicyCreate) -> str:
    """Create a new escalation policy.

    Args:
        escalation_policy: The policy data to create

    Returns:
        JSON string of the created EscalationPolicy
    """
    payload = escalation_policy.model_dump(exclude_none=True)
    response = get_client().rpost(
        "/escalation_policies",
        json={"escalation_policy": payload},
    )
    return EscalationPolicy.model_validate(response).model_dump_json()


def update_escalation_policy(policy_id: str, escalation_policy: EscalationPolicyCreate) -> str:
    """Update an existing escalation policy.

    Args:
        policy_id: The ID of the escalation policy to update
        escalation_policy: The updated policy data

    Returns:
        JSON string of the updated EscalationPolicy
    """
    payload = escalation_policy.model_dump(exclude_none=True)
    response = get_client().rput(
        f"/escalation_policies/{policy_id}",
        json={"escalation_policy": payload},
    )
    return EscalationPolicy.model_validate(response).model_dump_json()


def delete_escalation_policy(policy_id: str) -> str:
    """Delete an escalation policy.

    Args:
        policy_id: The ID of the escalation policy to delete

    Returns:
        JSON string confirming deletion
    """
    get_client().rdelete(f"/escalation_policies/{policy_id}")
    return json.dumps({"success": True})
```

- [ ] **Step 3: Commit**

```bash
git add pagerduty_mcp/models/escalation_policies.py pagerduty_mcp/tools/escalation_policies.py
git commit -m "feat: add create/update/delete escalation policy tools"
```

---

## Task 3: Python — register new tools in __init__.py

**Files:**
- Modify: `pagerduty_mcp/tools/__init__.py`
- Modify: `pagerduty_mcp/models/__init__.py` (if needed for new model exports)

- [ ] **Step 1: Update the escalation_policies import block**

Find the existing import block (around line 26-33):
```python
# Currently disabled to prevent issues with the escalation policies domain
from .escalation_policies import (
    # create_escalation_policy,
    get_escalation_policy,
    # get_escalation_policy_on_call,
    # get_escalation_policy_services,
    list_escalation_policies,
)
```

Replace with:
```python
from .escalation_policies import (
    create_escalation_policy,
    delete_escalation_policy,
    get_escalation_policy,
    list_escalation_policies,
    update_escalation_policy,
)
```

- [ ] **Step 2: Update the schedules import block**

Find the existing schedules import (around line 68-75):
```python
from .schedules import (
    create_schedule,
    create_schedule_override,
    get_schedule,
    list_schedule_users,
    list_schedules,
    update_schedule,
)
```

Replace with:
```python
from .schedules import (
    create_schedule,
    create_schedule_override,
    delete_schedule_override,
    get_schedule,
    list_schedule_overrides,
    list_schedule_users,
    list_schedules,
    update_schedule,
)
```

- [ ] **Step 3: Add new tools to read_tools and write_tools lists**

In `read_tools`, add under `# Schedules`:
```python
    list_schedule_overrides,
```

In `write_tools`, add under `# Schedules`:
```python
    delete_schedule_override,
```

Replace the comment `# Escalation Policies - currently disabled` and commented line with:
```python
    # Escalation Policies
    create_escalation_policy,
    update_escalation_policy,
    delete_escalation_policy,
```

- [ ] **Step 4: Verify Python is importable**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
source .venv/bin/activate 2>/dev/null || true
python -c "from pagerduty_mcp.tools import list_schedule_overrides, delete_schedule_override, create_escalation_policy, update_escalation_policy, delete_escalation_policy; print('OK')"
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add pagerduty_mcp/tools/__init__.py
git commit -m "feat: register new schedule override and escalation policy tools"
```

---

## Task 4: TypeScript — extend api.ts with new types and functions

**Files:**
- Modify: `mcp-apps/oncall-manager/src/api.ts`

Replace the entire file with the following (it extends everything existing plus adds new):

- [ ] **Step 1: Write new api.ts**

```ts
import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

const MOCK_MODE = import.meta.env.VITE_MOCK === "true";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface CurrentUser {
  id: string;
  name: string;
  email: string;
}

export interface Schedule {
  id: string;
  name: string;
  timeZone: string;
}

export interface ScheduleLayer {
  id: string;
  name: string;
  rotationSeconds: number;
  rotationVirtualStart: string;
  start: string;
  end: string | null;
  restrictions: any[] | null;
  users: ScheduleUser[];
}

export interface ScheduleDetail {
  id: string;
  name: string;
  description: string | null;
  timeZone: string;
  layers: ScheduleLayer[];
  allUsers: ScheduleUser[];  // from schedule.users
}

export interface OnCallShift {
  scheduleId: string;
  scheduleName: string;
  userId: string;
  userName: string;
  start: string;
  end: string;
  escalationLevel: number;
}

export interface OverrideDetail {
  id: string;
  scheduleId: string;
  scheduleName: string;
  start: string;
  end: string;
  user: { id: string; name: string; };
}

export interface ScheduleUser {
  id: string;
  name: string;
  email: string;
}

export interface EscalationTarget {
  id: string;
  type: "user_reference" | "schedule_reference";
  summary: string;
}

export interface EscalationRule {
  id?: string;
  escalation_delay_in_minutes: number;
  targets: EscalationTarget[];
}

export interface EscalationPolicy {
  id: string;
  name: string;
  description: string | null;
  num_loops: number;
  escalation_rules: EscalationRule[];
  services: Array<{ id: string; summary: string }>;
  teams: Array<{ id: string; summary: string }>;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

// ─── Current user ─────────────────────────────────────────────────────────────

export async function fetchCurrentUser(app: App): Promise<CurrentUser | null> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.currentUser;
  }
  const result = await app.callServerTool({ name: "get_user_data", arguments: {} });
  const data = extract<any>(result);
  const user = data?.response ?? data;
  if (!user?.id) return null;
  return { id: user.id, name: user.name, email: user.email };
}

// ─── Schedules ────────────────────────────────────────────────────────────────

export async function fetchSchedules(app: App): Promise<Schedule[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.schedules;
  }
  const result = await app.callServerTool({
    name: "list_schedules",
    arguments: { query_model: { limit: 100 } },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map((s: any) => ({
    id: s.id,
    name: s.name ?? s.summary,
    timeZone: s.time_zone ?? "UTC",
  }));
}

export async function fetchScheduleDetail(app: App, scheduleId: string): Promise<ScheduleDetail | null> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.scheduleDetails[scheduleId] ?? null;
  }
  const result = await app.callServerTool({
    name: "get_schedule",
    arguments: { schedule_id: scheduleId },
  });
  const data = extract<any>(result);
  const s = data?.schedule ?? data;
  if (!s?.id) return null;

  const layers: ScheduleLayer[] = (s.schedule_layers ?? []).map((l: any) => ({
    id: l.id,
    name: l.name,
    rotationSeconds: l.rotation_turn_length_seconds ?? 604800,
    rotationVirtualStart: l.rotation_virtual_start,
    start: l.start,
    end: l.end ?? null,
    restrictions: l.restrictions ?? null,
    users: (l.users ?? []).map((lu: any) => ({
      id: lu.user?.id ?? lu.id,
      name: lu.user?.summary ?? lu.user?.name ?? "Unknown",
      email: lu.user?.email ?? "",
    })),
  }));

  const allUsers: ScheduleUser[] = (s.users ?? []).map((u: any) => ({
    id: u.id,
    name: u.name ?? u.summary,
    email: u.email ?? "",
  }));

  return {
    id: s.id,
    name: s.name,
    description: s.description ?? null,
    timeZone: s.time_zone ?? "UTC",
    layers,
    allUsers,
  };
}

export async function saveScheduleDetail(
  app: App,
  scheduleDetail: ScheduleDetail,
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "update_schedule",
    arguments: {
      schedule_id: scheduleDetail.id,
      update_model: {
        schedule: {
          name: scheduleDetail.name,
          time_zone: scheduleDetail.timeZone,
          description: scheduleDetail.description,
          type: "schedule",
          schedule_layers: scheduleDetail.layers.map((l) => ({
            name: l.name,
            start: l.start,
            end: l.end ?? undefined,
            rotation_virtual_start: l.rotationVirtualStart,
            rotation_turn_length_seconds: l.rotationSeconds,
            users: l.users.map((u) => ({
              user: { id: u.id, type: "user_reference" },
            })),
            restrictions: l.restrictions ?? undefined,
          })),
        },
      },
    },
  });
  return !result.isError;
}

// ─── On-calls ─────────────────────────────────────────────────────────────────

export async function fetchUserShifts(
  app: App,
  userId: string,
  since: string,
  until: string,
): Promise<OnCallShift[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.myShifts;
  }
  const result = await app.callServerTool({
    name: "list_oncalls",
    arguments: {
      query_model: { user_ids: [userId], since, until, earliest: false },
    },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items
    .filter((o: any) => o.schedule?.id && o.start && o.end && o.user?.id)
    .map((o: any) => ({
      scheduleId: o.schedule.id,
      scheduleName: o.schedule.summary ?? o.schedule.id,
      userId: o.user.id,
      userName: o.user.summary ?? o.user.name ?? "Unknown",
      start: o.start,
      end: o.end,
      escalationLevel: o.escalation_level ?? 0,
    }));
}

export async function fetchAllOnCalls(
  app: App,
  since: string,
  until: string,
): Promise<OnCallShift[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.allShifts;
  }
  const result = await app.callServerTool({
    name: "list_oncalls",
    arguments: { query_model: { since, until, earliest: false } },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items
    .filter((o: any) => o.schedule?.id && o.start && o.end && o.user?.id)
    .map((o: any) => ({
      scheduleId: o.schedule.id,
      scheduleName: o.schedule.summary ?? o.schedule.id,
      userId: o.user.id,
      userName: o.user.summary ?? o.user.name ?? "Unknown",
      start: o.start,
      end: o.end,
      escalationLevel: o.escalation_level ?? 0,
    }));
}

// ─── Overrides ────────────────────────────────────────────────────────────────

export async function fetchScheduleOverrides(
  app: App,
  scheduleId: string,
  since: string,
  until: string,
): Promise<OverrideDetail[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return (MOCK_ONCALL_DATA.overridesBySchedule[scheduleId] ?? []).map((o) => ({
      ...o,
      scheduleId,
      scheduleName: MOCK_ONCALL_DATA.schedules.find((s) => s.id === scheduleId)?.name ?? scheduleId,
    }));
  }
  const result = await app.callServerTool({
    name: "list_schedule_overrides",
    arguments: { schedule_id: scheduleId, since, until },
  });
  const data = extract<any>(result);
  const items: any[] = data?.overrides ?? [];
  return items.map((o: any) => ({
    id: o.id,
    scheduleId,
    scheduleName: "",
    start: o.start,
    end: o.end,
    user: { id: o.user?.id ?? "", name: o.user?.name ?? o.user?.summary ?? "Unknown" },
  }));
}

export async function deleteOverride(
  app: App,
  scheduleId: string,
  overrideId: string,
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "delete_schedule_override",
    arguments: { schedule_id: scheduleId, override_id: overrideId },
  });
  return !result.isError;
}

export async function createOverride(
  app: App,
  scheduleId: string,
  userId: string,
  start: string,
  end: string,
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "create_schedule_override",
    arguments: {
      schedule_id: scheduleId,
      override_request: {
        overrides: [{ start, end, user: { id: userId, type: "user_reference" } }],
      },
    },
  });
  return !result.isError;
}

// ─── Schedule users (with fallback) ──────────────────────────────────────────

export async function fetchScheduleUsers(
  app: App,
  scheduleId: string,
): Promise<ScheduleUser[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.scheduleUsers[scheduleId] ?? [];
  }
  // Primary: list_schedule_users
  const result = await app.callServerTool({
    name: "list_schedule_users",
    arguments: { schedule_id: scheduleId },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  if (items.length > 0) {
    return items.map((u: any) => ({
      id: u.id,
      name: u.name ?? u.summary,
      email: u.email ?? "",
    }));
  }
  // Fallback: extract unique users from list_oncalls for this schedule
  const since = new Date().toISOString();
  const until = new Date(Date.now() + 30 * 86_400_000).toISOString();
  const fallback = await app.callServerTool({
    name: "list_oncalls",
    arguments: {
      query_model: { schedule_ids: [scheduleId], since, until, earliest: false },
    },
  });
  const fallbackData = extract<any>(fallback);
  const fallbackItems: any[] = fallbackData?.response ?? [];
  const seen = new Set<string>();
  const users: ScheduleUser[] = [];
  for (const o of fallbackItems) {
    if (o.user?.id && !seen.has(o.user.id)) {
      seen.add(o.user.id);
      users.push({
        id: o.user.id,
        name: o.user.summary ?? o.user.name ?? "Unknown",
        email: o.user.email ?? "",
      });
    }
  }
  return users;
}

// ─── All users (for adding to schedules / EP targets) ────────────────────────

export async function fetchUsers(app: App, query?: string): Promise<ScheduleUser[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    const all = MOCK_ONCALL_DATA.allUsers;
    if (!query) return all;
    const q = query.toLowerCase();
    return all.filter((u) => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q));
  }
  const args: any = { query_model: { limit: 100 } };
  if (query) args.query_model.query = query;
  const result = await app.callServerTool({ name: "list_users", arguments: args });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map((u: any) => ({
    id: u.id,
    name: u.name ?? u.summary,
    email: u.email ?? "",
  }));
}

// ─── Escalation policies ─────────────────────────────────────────────────────

export async function fetchEscalationPolicies(
  app: App,
  query?: string,
): Promise<EscalationPolicy[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    const all = MOCK_ONCALL_DATA.escalationPolicies;
    if (!query) return all;
    const q = query.toLowerCase();
    return all.filter((p) => p.name.toLowerCase().includes(q));
  }
  const args: any = { query_model: { limit: 100, include: ["services", "teams"] } };
  if (query) args.query_model.query = query;
  const result = await app.callServerTool({
    name: "list_escalation_policies",
    arguments: args,
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map(mapEscalationPolicy);
}

export async function fetchEscalationPolicy(
  app: App,
  policyId: string,
): Promise<EscalationPolicy | null> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.escalationPolicies.find((p) => p.id === policyId) ?? null;
  }
  const result = await app.callServerTool({
    name: "get_escalation_policy",
    arguments: { policy_id: policyId },
  });
  const data = extract<any>(result);
  if (!data?.id) return null;
  return mapEscalationPolicy(data);
}

export async function updateEscalationPolicy(
  app: App,
  policyId: string,
  policy: Pick<EscalationPolicy, "name" | "description" | "num_loops" | "escalation_rules">,
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "update_escalation_policy",
    arguments: {
      policy_id: policyId,
      escalation_policy: {
        name: policy.name,
        description: policy.description,
        num_loops: policy.num_loops,
        escalation_rules: policy.escalation_rules.map((r) => ({
          escalation_delay_in_minutes: r.escalation_delay_in_minutes,
          targets: r.targets.map((t) => ({ id: t.id, type: t.type })),
        })),
      },
    },
  });
  return !result.isError;
}

export async function createEscalationPolicy(
  app: App,
  policy: Pick<EscalationPolicy, "name" | "description" | "num_loops" | "escalation_rules">,
): Promise<EscalationPolicy | null> {
  const result = await app.callServerTool({
    name: "create_escalation_policy",
    arguments: {
      escalation_policy: {
        name: policy.name,
        description: policy.description,
        num_loops: policy.num_loops,
        escalation_rules: policy.escalation_rules.map((r) => ({
          escalation_delay_in_minutes: r.escalation_delay_in_minutes,
          targets: r.targets.map((t) => ({ id: t.id, type: t.type })),
        })),
      },
    },
  });
  const data = extract<any>(result);
  if (!data?.id) return null;
  return mapEscalationPolicy(data);
}

export async function deleteEscalationPolicy(app: App, policyId: string): Promise<boolean> {
  const result = await app.callServerTool({
    name: "delete_escalation_policy",
    arguments: { policy_id: policyId },
  });
  return !result.isError;
}

function mapEscalationPolicy(p: any): EscalationPolicy {
  return {
    id: p.id,
    name: p.name,
    description: p.description ?? null,
    num_loops: p.num_loops ?? 0,
    escalation_rules: (p.escalation_rules ?? []).map((r: any) => ({
      id: r.id,
      escalation_delay_in_minutes: r.escalation_delay_in_minutes ?? 30,
      targets: (r.targets ?? []).map((t: any) => ({
        id: t.id,
        type: t.type as "user_reference" | "schedule_reference",
        summary: t.summary ?? t.name ?? t.id,
      })),
    })),
    services: (p.services ?? []).map((s: any) => ({ id: s.id, summary: s.summary })),
    teams: (p.teams ?? []).map((t: any) => ({ id: t.id, summary: t.summary })),
  };
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/api.ts
git commit -m "feat: extend oncall-manager API layer with overrides, schedule detail, EP CRUD"
```

---

## Task 5: TypeScript — update mock.ts

**Files:**
- Modify: `mcp-apps/oncall-manager/src/mock.ts`

Replace the entire file:

- [ ] **Step 1: Write new mock.ts**

```ts
import type {
  CurrentUser,
  EscalationPolicy,
  OnCallShift,
  OverrideDetail,
  Schedule,
  ScheduleDetail,
  ScheduleUser,
} from "./api";

const NOW = new Date();
const D = (offsetDays: number, hour = 9) => {
  const d = new Date(NOW);
  d.setDate(d.getDate() + offsetDays);
  d.setHours(hour, 0, 0, 0);
  return d.toISOString();
};

const ALICE: ScheduleUser = { id: "U001", name: "Alice Chen", email: "alice@example.com" };
const BOB: ScheduleUser = { id: "U002", name: "Bob Kim", email: "bob@example.com" };
const CARLOS: ScheduleUser = { id: "U003", name: "Carlos M.", email: "carlos@example.com" };
const DANA: ScheduleUser = { id: "U004", name: "Dana W.", email: "dana@example.com" };
const ERIC: ScheduleUser = { id: "U005", name: "Eric L.", email: "eric@example.com" };
const FIONA: ScheduleUser = { id: "U006", name: "Fiona R.", email: "fiona@example.com" };

export const MOCK_ONCALL_DATA: {
  currentUser: CurrentUser;
  schedules: Schedule[];
  myShifts: OnCallShift[];
  allShifts: OnCallShift[];
  overridesBySchedule: Record<string, Omit<OverrideDetail, "scheduleId" | "scheduleName">[]>;
  scheduleUsers: Record<string, ScheduleUser[]>;
  scheduleDetails: Record<string, ScheduleDetail>;
  allUsers: ScheduleUser[];
  escalationPolicies: EscalationPolicy[];
} = {
  currentUser: ALICE,

  schedules: [
    { id: "S001", name: "Infra Primary", timeZone: "America/New_York" },
    { id: "S002", name: "Platform On-Call", timeZone: "America/New_York" },
    { id: "S003", name: "Backend Primary", timeZone: "America/Los_Angeles" },
  ],

  myShifts: [
    { scheduleId: "S001", scheduleName: "Infra Primary", userId: "U001", userName: "Alice Chen", start: D(-1), end: D(1), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", userId: "U001", userName: "Alice Chen", start: D(3), end: D(5), escalationLevel: 1 },
  ],

  allShifts: [
    { scheduleId: "S001", scheduleName: "Infra Primary", userId: "U001", userName: "Alice Chen", start: D(-1), end: D(1), escalationLevel: 1 },
    { scheduleId: "S001", scheduleName: "Infra Primary", userId: "U002", userName: "Bob Kim", start: D(1), end: D(3), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", userId: "U004", userName: "Dana W.", start: D(0), end: D(2), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", userId: "U001", userName: "Alice Chen", start: D(3), end: D(5), escalationLevel: 1 },
    { scheduleId: "S003", scheduleName: "Backend Primary", userId: "U003", userName: "Carlos M.", start: D(2), end: D(4), escalationLevel: 1 },
    { scheduleId: "S003", scheduleName: "Backend Primary", userId: "U006", userName: "Fiona R.", start: D(5), end: D(7), escalationLevel: 1 },
  ],

  overridesBySchedule: {
    S001: [
      { id: "OR001", start: D(2), end: D(3), user: { id: "U002", name: "Bob Kim" } },
    ],
    S002: [],
    S003: [
      { id: "OR002", start: D(5), end: D(6), user: { id: "U001", name: "Alice Chen" } },
    ],
  },

  scheduleUsers: {
    S001: [ALICE, BOB, CARLOS],
    S002: [ALICE, DANA, ERIC],
    S003: [CARLOS, BOB, FIONA],
  },

  scheduleDetails: {
    S001: {
      id: "S001",
      name: "Infra Primary",
      description: "Primary on-call rotation for infrastructure incidents",
      timeZone: "America/New_York",
      allUsers: [ALICE, BOB, CARLOS],
      layers: [
        {
          id: "L001",
          name: "Weekly Rotation",
          rotationSeconds: 604800,
          rotationVirtualStart: D(-7),
          start: D(-30),
          end: null,
          restrictions: null,
          users: [ALICE, BOB, CARLOS],
        },
      ],
    },
    S002: {
      id: "S002",
      name: "Platform On-Call",
      description: null,
      timeZone: "America/New_York",
      allUsers: [ALICE, DANA, ERIC],
      layers: [
        {
          id: "L002",
          name: "Weekly Rotation",
          rotationSeconds: 604800,
          rotationVirtualStart: D(-7),
          start: D(-30),
          end: null,
          restrictions: null,
          users: [ALICE, DANA, ERIC],
        },
      ],
    },
    S003: {
      id: "S003",
      name: "Backend Primary",
      description: "Backend team rotation",
      timeZone: "America/Los_Angeles",
      allUsers: [CARLOS, BOB, FIONA],
      layers: [
        {
          id: "L003",
          name: "Weekly Rotation",
          rotationSeconds: 604800,
          rotationVirtualStart: D(-7),
          start: D(-30),
          end: null,
          restrictions: null,
          users: [CARLOS, BOB, FIONA],
        },
      ],
    },
  },

  allUsers: [ALICE, BOB, CARLOS, DANA, ERIC, FIONA],

  escalationPolicies: [
    {
      id: "EP001",
      name: "Infra Escalation Policy",
      description: "Escalation for infrastructure incidents",
      num_loops: 2,
      escalation_rules: [
        {
          id: "ER001",
          escalation_delay_in_minutes: 30,
          targets: [
            { id: "U001", type: "user_reference", summary: "Alice Chen" },
            { id: "S001", type: "schedule_reference", summary: "Infra Primary" },
          ],
        },
        {
          id: "ER002",
          escalation_delay_in_minutes: 60,
          targets: [
            { id: "U004", type: "user_reference", summary: "Dana W." },
          ],
        },
      ],
      services: [{ id: "SVC001", summary: "Payment Service" }],
      teams: [{ id: "T001", summary: "Infrastructure" }],
    },
    {
      id: "EP002",
      name: "Platform Escalation",
      description: null,
      num_loops: 1,
      escalation_rules: [
        {
          id: "ER003",
          escalation_delay_in_minutes: 15,
          targets: [
            { id: "S002", type: "schedule_reference", summary: "Platform On-Call" },
          ],
        },
      ],
      services: [],
      teams: [{ id: "T002", summary: "Platform" }],
    },
  ],
};
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/mock.ts
git commit -m "feat: expand oncall-manager mock data (overrides, schedule detail, escalation policies)"
```

---

## Task 6: CSS + userColor utility

**Files:**
- Modify: `mcp-apps/oncall-manager/src/styles.css`
- Create: `mcp-apps/oncall-manager/src/utils/userColor.ts`

- [ ] **Step 1: Create src/utils/userColor.ts**

```ts
const PALETTE = [
  "#89b4fa", // blue
  "#a6e3a1", // green
  "#cba6f7", // mauve
  "#fab387", // peach
  "#f9e2af", // yellow
  "#94e2d5", // teal
  "#f38ba8", // red
  "#89dceb", // sky
];

export function userColor(userId: string): string {
  let hash = 0;
  for (let i = 0; i < userId.length; i++) {
    hash = (hash * 31 + userId.charCodeAt(i)) & 0xffffffff;
  }
  return PALETTE[Math.abs(hash) % PALETTE.length];
}

// All palette colors are light — dark mantle text works for all
export const USER_COLOR_FG = "#1e1e2e";
```

- [ ] **Step 2: Replace src/styles.css**

```css
/* ─── Reset & base ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --base: #1e1e2e;
  --mantle: #181825;
  --crust: #11111b;
  --surface0: #313244;
  --surface1: #45475a;
  --surface2: #585b70;
  --overlay0: #6c7086;
  --overlay1: #7f849c;
  --text: #cdd6f4;
  --subtext0: #a6adc8;
  --subtext1: #bac2de;
  --blue: #89b4fa;
  --mauve: #cba6f7;
  --green: #a6e3a1;
  --yellow: #f9e2af;
  --red: #f38ba8;
  --peach: #fab387;
  --teal: #94e2d5;
  --sky: #89dceb;
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 13px;
  color: var(--text);
  background: var(--base);
}

body { background: var(--base); min-height: 100vh; }
#root { min-height: 100vh; }

/* ─── App shell ─── */
.app { display: flex; flex-direction: column; min-height: 100vh; }

.app-header {
  background: var(--mantle);
  border-bottom: 1px solid var(--surface0);
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.app-header .dot { color: var(--green); font-size: 10px; }
.app-header h1 { font-size: 15px; font-weight: 700; letter-spacing: -0.02em; }
.app-header .user-chip {
  font-size: 10px;
  color: var(--overlay0);
  background: var(--surface0);
  padding: 2px 8px;
  border-radius: 10px;
}

/* ─── Home: 4-card grid ─── */
.home-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  padding: 20px;
  flex: 1;
}

.home-card {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 130px;
  user-select: none;
}
.home-card:hover { border-color: var(--blue); background: rgba(137,180,250,0.04); }
.home-card:active { background: rgba(137,180,250,0.08); }

.home-card-icon { font-size: 22px; line-height: 1; }
.home-card-title { font-size: 14px; font-weight: 700; }
.home-card-desc { font-size: 11px; color: var(--overlay1); flex: 1; }
.home-card-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  align-self: flex-start;
}
.home-card-badge.active { background: rgba(166,227,161,0.2); color: var(--green); }
.home-card-badge.info { background: rgba(137,180,250,0.2); color: var(--blue); }
.home-card-badge.warn { background: rgba(249,226,175,0.2); color: var(--yellow); }

/* ─── Modal overlay ─── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(17,17,27,0.85);
  display: flex;
  align-items: stretch;
  justify-content: flex-end;
  z-index: 50;
}
.modal-panel {
  background: var(--base);
  border-left: 1px solid var(--surface0);
  width: min(680px, 100vw);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.modal-header {
  background: var(--mantle);
  border-bottom: 1px solid var(--surface0);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.modal-header h2 { font-size: 14px; font-weight: 700; flex: 1; }
.modal-close {
  background: transparent;
  border: none;
  color: var(--overlay0);
  cursor: pointer;
  font-size: 16px;
  padding: 2px 6px;
  border-radius: 4px;
  line-height: 1;
}
.modal-close:hover { background: var(--surface0); color: var(--text); }
.modal-body { flex: 1; overflow-y: auto; padding: 16px; }

/* ─── Sub-modal (wizard / confirm dialogs) ─── */
.submodal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(17,17,27,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.submodal-dialog {
  background: var(--base);
  border: 1px solid var(--surface1);
  border-radius: 10px;
  width: min(520px, 95vw);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.submodal-header {
  background: var(--mantle);
  border-bottom: 1px solid var(--surface0);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.submodal-header h3 { font-size: 13px; font-weight: 600; flex: 1; }
.submodal-body { padding: 16px; overflow-y: auto; flex: 1; }
.submodal-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--surface0);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--mantle);
}

/* ─── List + detail navigation ─── */
.detail-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--blue);
  cursor: pointer;
  padding: 4px 0;
  margin-bottom: 14px;
  background: none;
  border: none;
}
.detail-back:hover { text-decoration: underline; }

/* ─── Countdown cards ─── */
.countdown-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.countdown-card {
  flex: 1;
  min-width: 160px;
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 8px;
  padding: 14px 16px;
}
.countdown-card.active-now { border-color: var(--green); }
.countdown-card.upcoming { border-color: var(--blue); }
.countdown-card .label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 4px;
}
.countdown-card.active-now .label { color: var(--green); }
.countdown-card.upcoming .label { color: var(--blue); }
.countdown-card .schedule-name { font-size: 13px; font-weight: 600; margin-bottom: 2px; }
.countdown-card .time-detail { font-size: 11px; color: var(--overlay0); margin-bottom: 6px; }
.countdown-card .countdown-timer { font-size: 12px; font-weight: 600; margin-bottom: 10px; }
.countdown-card.active-now .countdown-timer { color: var(--green); }
.countdown-card.upcoming .countdown-timer { color: var(--blue); }
.countdown-card .actions { display: flex; gap: 6px; flex-wrap: wrap; }

/* ─── 7-day schedule grid ─── */
.schedule-grid-wrap { overflow-x: auto; }
.schedule-grid-table { width: 100%; border-collapse: collapse; font-size: 11px; table-layout: fixed; }
.schedule-grid-table th {
  background: var(--mantle);
  color: var(--overlay0);
  font-weight: 500;
  padding: 6px 4px;
  text-align: center;
  border-bottom: 1px solid var(--surface0);
  white-space: nowrap;
}
.schedule-grid-table th:first-child { text-align: left; width: 140px; padding-left: 8px; }
.schedule-grid-table td {
  padding: 3px 4px;
  border-bottom: 1px solid var(--surface0);
  vertical-align: middle;
}
.schedule-grid-table td:first-child { padding-left: 8px; color: var(--subtext1); white-space: nowrap; }
.schedule-grid-table tr:last-child td { border-bottom: none; }

.shift-bar {
  display: block;
  border-radius: 3px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #1e1e2e;
}
.shift-bar + .shift-bar { margin-top: 2px; }

/* ─── Override list ─── */
.override-list { display: flex; flex-direction: column; gap: 6px; }
.override-row {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 6px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.override-row .or-user-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
  color: #1e1e2e;
}
.override-row .or-info { flex: 1; min-width: 0; }
.override-row .or-user { font-weight: 600; font-size: 12px; }
.override-row .or-meta { font-size: 10px; color: var(--overlay0); }
.override-row .or-actions { display: flex; gap: 6px; flex-shrink: 0; }

/* ─── Schedule detail: layers ─── */
.layer-card {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}
.layer-header {
  background: var(--surface0);
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.layer-title { font-weight: 600; font-size: 12px; flex: 1; }
.layer-meta { font-size: 10px; color: var(--overlay0); }
.layer-users { padding: 8px 12px; display: flex; flex-direction: column; gap: 4px; }
.layer-user-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  border-bottom: 1px solid var(--surface0);
}
.layer-user-row:last-child { border-bottom: none; }
.layer-user-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  flex-shrink: 0;
  color: #1e1e2e;
}
.layer-user-name { flex: 1; font-size: 12px; }
.layer-user-order { font-size: 10px; color: var(--overlay0); margin-right: 4px; }

/* ─── Escalation policy: rules ─── */
.ep-rule-card {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 8px;
  margin-bottom: 10px;
}
.ep-rule-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--surface0);
  border-radius: 8px 8px 0 0;
}
.ep-rule-num {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--blue);
  color: var(--mantle);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
}
.ep-rule-delay { font-size: 12px; font-weight: 600; flex: 1; }
.ep-rule-body { padding: 8px 12px; display: flex; flex-direction: column; gap: 4px; }
.ep-target-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  border-bottom: 1px solid var(--surface0);
}
.ep-target-row:last-child { border-bottom: none; }
.ep-target-icon { font-size: 12px; flex-shrink: 0; }
.ep-target-name { flex: 1; font-size: 12px; }
.ep-target-type {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 3px;
  background: var(--surface1);
  color: var(--subtext0);
}

/* ─── Availability badges (wizard step 2) ─── */
.avail-badge {
  font-size: 9px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 3px;
  flex-shrink: 0;
}
.avail-badge.free { background: rgba(166,227,161,0.2); color: var(--green); }
.avail-badge.conflict { background: rgba(249,226,175,0.2); color: var(--yellow); }

/* ─── Wizard steps ─── */
.wizard-steps {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 10px 16px;
  border-bottom: 1px solid var(--surface0);
  background: var(--mantle);
}
.wizard-step { display: flex; align-items: center; gap: 6px; font-size: 10px; color: var(--overlay0); }
.wizard-step.active { color: var(--blue); font-weight: 600; }
.wizard-step.done { color: var(--green); }
.wizard-step-num {
  width: 18px; height: 18px;
  border-radius: 50%;
  background: var(--surface0);
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 600;
}
.wizard-step.active .wizard-step-num { background: var(--blue); color: var(--mantle); }
.wizard-step.done .wizard-step-num { background: var(--green); color: var(--mantle); }
.wizard-step-sep { color: var(--surface1); margin: 0 6px; font-size: 10px; }

/* ─── Shift picker ─── */
.shift-list { display: flex; flex-direction: column; gap: 6px; }
.shift-option {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 6px;
  padding: 10px 12px;
  cursor: pointer;
  transition: border-color 0.15s;
}
.shift-option:hover { border-color: var(--blue); }
.shift-option.selected { border-color: var(--blue); background: rgba(137,180,250,0.1); }
.shift-option .shift-sched { font-size: 10px; color: var(--overlay0); margin-bottom: 2px; }
.shift-option .shift-dates { font-size: 12px; font-weight: 500; }

/* ─── User picker ─── */
.user-search {
  background: var(--surface0);
  border: 1px solid var(--surface1);
  border-radius: 4px;
  color: var(--text);
  padding: 6px 10px;
  font-size: 12px;
  width: 100%;
  margin-bottom: 10px;
}
.user-search:focus { outline: 1px solid var(--blue); border-color: var(--blue); }
.user-list { display: flex; flex-direction: column; gap: 4px; max-height: 260px; overflow-y: auto; }
.user-option {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 5px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: border-color 0.15s;
}
.user-option:hover { border-color: var(--blue); }
.user-option.selected { border-color: var(--blue); background: rgba(137,180,250,0.1); }
.user-option-dot {
  width: 22px; height: 22px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 9px; font-weight: 700;
  flex-shrink: 0;
  color: #1e1e2e;
}
.user-option-info { flex: 1; min-width: 0; }
.user-option .user-name { font-weight: 600; font-size: 12px; }
.user-option .user-email { font-size: 10px; color: var(--overlay0); }

/* ─── Confirm card ─── */
.confirm-card { background: var(--mantle); border: 1px solid var(--surface0); border-radius: 8px; padding: 14px 16px; }
.confirm-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px; }
.confirm-row .label { color: var(--overlay0); }
.confirm-row .value { font-weight: 500; }

/* ─── Forms ─── */
.create-form { background: var(--mantle); border: 1px solid var(--surface0); border-radius: 8px; padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; }
.form-row { display: flex; gap: 10px; flex-wrap: wrap; }
.form-field { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 140px; }
.form-field label { font-size: 10px; color: var(--overlay0); font-weight: 500; }
.form-field select,
.form-field input[type="text"],
.form-field input[type="number"],
.form-field input[type="datetime-local"],
.form-field textarea {
  background: var(--surface0);
  border: 1px solid var(--surface1);
  border-radius: 4px;
  color: var(--text);
  padding: 5px 8px;
  font-size: 12px;
  width: 100%;
}
.form-field select:focus,
.form-field input:focus,
.form-field textarea:focus { outline: 1px solid var(--blue); border-color: var(--blue); }
.form-field textarea { resize: vertical; min-height: 60px; }

/* ─── Buttons ─── */
.btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 5px 12px; border: none; border-radius: 5px;
  cursor: pointer; font-size: 11px; font-weight: 600;
  transition: opacity 0.15s; line-height: 1.4;
}
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-primary { background: var(--blue); color: var(--mantle); }
.btn-secondary { background: var(--surface0); color: var(--text); }
.btn-danger { background: var(--red); color: var(--mantle); }
.btn-ghost { background: transparent; color: var(--blue); padding: 3px 6px; }
.btn-ghost:hover { background: var(--surface0); }
.btn-ghost-danger { background: transparent; color: var(--red); padding: 3px 6px; }
.btn-ghost-danger:hover { background: rgba(243,139,168,0.1); }
.btn-sm { font-size: 10px; padding: 3px 8px; }

/* ─── Section headings ─── */
.section-heading {
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--overlay1); margin-bottom: 10px; margin-top: 20px;
}
.section-heading:first-child { margin-top: 0; }

/* ─── Search bar ─── */
.search-input {
  background: var(--surface0);
  border: 1px solid var(--surface1);
  border-radius: 6px;
  color: var(--text);
  padding: 7px 12px;
  font-size: 12px;
  width: 100%;
  margin-bottom: 12px;
}
.search-input:focus { outline: 1px solid var(--blue); border-color: var(--blue); }

/* ─── List rows ─── */
.list-row {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 6px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: border-color 0.15s;
  margin-bottom: 6px;
}
.list-row:hover { border-color: var(--blue); }
.list-row .list-row-title { font-weight: 600; font-size: 12px; flex: 1; }
.list-row .list-row-meta { font-size: 10px; color: var(--overlay0); }
.list-row .list-row-chevron { color: var(--overlay0); font-size: 12px; }

/* ─── Schedule picker (overrides) ─── */
.schedule-picker {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 14px;
  flex-wrap: wrap;
}
.schedule-picker label { font-size: 11px; color: var(--overlay0); flex-shrink: 0; }
.schedule-picker select {
  background: var(--surface0);
  border: 1px solid var(--surface1);
  border-radius: 4px;
  color: var(--text);
  padding: 5px 8px;
  font-size: 12px;
  flex: 1;
  min-width: 180px;
}

/* ─── Empty / error / loading ─── */
.empty-state { text-align: center; color: var(--overlay0); padding: 32px 16px; font-size: 12px; }
.error-banner { background: rgba(243,139,168,0.15); border: 1px solid var(--red); color: var(--red); border-radius: 6px; padding: 8px 12px; font-size: 12px; margin-bottom: 12px; }
.loading-row { display: flex; align-items: center; gap: 8px; color: var(--overlay0); font-size: 12px; padding: 12px 0; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  width: 14px; height: 14px;
  border: 2px solid var(--surface1);
  border-top-color: var(--blue);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

/* ─── Divider ─── */
.divider { border: none; border-top: 1px solid var(--surface0); margin: 14px 0; }
```

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-manager/src/utils/userColor.ts mcp-apps/oncall-manager/src/styles.css
git commit -m "feat: add userColor utility and redesign CSS (home cards, modal panels, colored bars)"
```

---

## Task 7: CoverageWizard — fix user fallback + availability badges

**Files:**
- Replace: `mcp-apps/oncall-manager/src/components/CoverageWizard.tsx`

- [ ] **Step 1: Replace CoverageWizard.tsx**

```tsx
import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { createOverride, fetchAllOnCalls, fetchScheduleUsers } from "../api";
import type { OnCallShift, ScheduleUser } from "../api";
import { USER_COLOR_FG, userColor } from "../utils/userColor";

interface Props {
  app: App;
  shifts: OnCallShift[];
  preselectedShift?: OnCallShift;
  onClose: () => void;
  onDone: () => void;
}

function fmtRange(start: string, end: string): string {
  const fmt = (iso: string) =>
    new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  return `${fmt(start)} → ${fmt(end)}`;
}

export function CoverageWizard({ app, shifts, preselectedShift, onClose, onDone }: Props) {
  const [step, setStep] = useState<1 | 2 | 3>(preselectedShift ? 2 : 1);
  const [selectedShift, setSelectedShift] = useState<OnCallShift | null>(preselectedShift ?? null);
  const [users, setUsers] = useState<ScheduleUser[]>([]);
  const [conflictIds, setConflictIds] = useState<Set<string>>(new Set());
  const [userSearch, setUserSearch] = useState("");
  const [selectedUser, setSelectedUser] = useState<ScheduleUser | null>(null);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (step !== 2 || !selectedShift) return;
    setLoadingUsers(true);
    Promise.all([
      fetchScheduleUsers(app, selectedShift.scheduleId),
      fetchAllOnCalls(app, selectedShift.start, selectedShift.end),
    ])
      .then(([schedUsers, onCalls]) => {
        setUsers(schedUsers);
        // Mark users already on call during the shift window as conflicts
        const ids = new Set(onCalls.map((o) => o.userId));
        setConflictIds(ids);
      })
      .catch(() => setUsers([]))
      .finally(() => setLoadingUsers(false));
  }, [step, selectedShift]);

  const filteredUsers = users.filter(
    (u) =>
      u.name.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.email.toLowerCase().includes(userSearch.toLowerCase()),
  );

  async function handleConfirm() {
    if (!selectedShift || !selectedUser) return;
    setSubmitting(true);
    setError(null);
    try {
      const ok = await createOverride(app, selectedShift.scheduleId, selectedUser.id, selectedShift.start, selectedShift.end);
      if (ok) { onDone(); } else { setError("Failed to create override. Please try again."); }
    } catch (e: any) {
      setError(e?.message ?? "Unexpected error");
    } finally {
      setSubmitting(false);
    }
  }

  const stepLabels = ["Select shift", "Choose coverage", "Confirm"];

  return (
    <div className="submodal-overlay" onClick={onClose}>
      <div className="submodal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="submodal-header">
          <h3>🔄 Find Coverage</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="wizard-steps">
          {[1, 2, 3].map((n, i) => (
            <span key={n} style={{ display: "contents" }}>
              <div className={`wizard-step ${step === n ? "active" : step > n ? "done" : ""}`}>
                <span className="wizard-step-num">{step > n ? "✓" : n}</span>
                {stepLabels[i]}
              </div>
              {i < 2 && <span className="wizard-step-sep">›</span>}
            </span>
          ))}
        </div>

        <div className="submodal-body">
          {step === 1 && (
            <div className="shift-list">
              {shifts.length === 0 && <p className="empty-state">No upcoming shifts found.</p>}
              {shifts.map((s, i) => (
                <div
                  key={i}
                  className={`shift-option ${selectedShift === s ? "selected" : ""}`}
                  onClick={() => setSelectedShift(s)}
                >
                  <div className="shift-sched">{s.scheduleName}</div>
                  <div className="shift-dates">{fmtRange(s.start, s.end)}</div>
                </div>
              ))}
            </div>
          )}

          {step === 2 && (
            <>
              {loadingUsers ? (
                <div className="loading-row"><span className="spinner" />Loading users…</div>
              ) : (
                <>
                  <input
                    className="user-search"
                    placeholder="Search by name or email…"
                    value={userSearch}
                    onChange={(e) => setUserSearch((e.target as HTMLInputElement).value)}
                    autoFocus
                  />
                  <div className="user-list">
                    {filteredUsers.length === 0 && <p className="empty-state">No users found.</p>}
                    {filteredUsers.map((u) => {
                      const color = userColor(u.id);
                      const isConflict = conflictIds.has(u.id);
                      return (
                        <div
                          key={u.id}
                          className={`user-option ${selectedUser?.id === u.id ? "selected" : ""}`}
                          onClick={() => setSelectedUser(u)}
                        >
                          <div className="user-option-dot" style={{ background: color, color: USER_COLOR_FG }}>
                            {u.name[0]}
                          </div>
                          <div className="user-option-info">
                            <div className="user-name">{u.name}</div>
                            {u.email && <div className="user-email">{u.email}</div>}
                          </div>
                          <span className={`avail-badge ${isConflict ? "conflict" : "free"}`}>
                            {isConflict ? "⚠ On-call" : "✓ Free"}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </>
          )}

          {step === 3 && selectedShift && selectedUser && (
            <>
              {error && <p className="error-banner">{error}</p>}
              <div className="confirm-card">
                <div className="confirm-row"><span className="label">Schedule</span><span className="value">{selectedShift.scheduleName}</span></div>
                <div className="confirm-row"><span className="label">Period</span><span className="value">{fmtRange(selectedShift.start, selectedShift.end)}</span></div>
                <div className="confirm-row"><span className="label">Coverage by</span><span className="value">{selectedUser.name}</span></div>
              </div>
            </>
          )}
        </div>

        <div className="submodal-footer">
          <button
            className="btn btn-secondary"
            onClick={step === 1 ? onClose : () => setStep((s) => (s - 1) as 1 | 2 | 3)}
            disabled={submitting}
          >
            {step === 1 ? "Cancel" : "← Back"}
          </button>
          {step < 3 ? (
            <button
              className="btn btn-primary"
              onClick={() => setStep((s) => (s + 1) as 2 | 3)}
              disabled={(step === 1 && !selectedShift) || (step === 2 && !selectedUser)}
            >
              Next →
            </button>
          ) : (
            <button className="btn btn-primary" onClick={handleConfirm} disabled={submitting}>
              {submitting ? "Creating…" : "Create Override"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/components/CoverageWizard.tsx
git commit -m "fix: coverage wizard fallback users + availability badges"
```

---

## Task 8: MyOnCalls modal — colored bars, no empty rows

**Files:**
- Replace: `mcp-apps/oncall-manager/src/components/MyOnCalls.tsx`

- [ ] **Step 1: Replace MyOnCalls.tsx**

```tsx
import type { App } from "@modelcontextprotocol/ext-apps";
import { useState } from "react";
import type { CurrentUser, OnCallShift, Schedule } from "../api";
import { USER_COLOR_FG, userColor } from "../utils/userColor";
import { CoverageWizard } from "./CoverageWizard";

interface Props {
  app: App;
  currentUser: CurrentUser;
  myShifts: OnCallShift[];
  allShifts: OnCallShift[];
  schedules: Schedule[];
  onOverrideCreated: () => void;
  onClose: () => void;
}

function isNow(shift: OnCallShift): boolean {
  const now = Date.now();
  return new Date(shift.start).getTime() <= now && new Date(shift.end).getTime() > now;
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function countdownLabel(shift: OnCallShift): string {
  const ms = new Date(shift.start).getTime() - Date.now();
  if (ms <= 0) {
    const rem = new Date(shift.end).getTime() - Date.now();
    const h = Math.floor(rem / 3_600_000);
    const m = Math.floor((rem % 3_600_000) / 60_000);
    return h > 0 ? `${h}h ${m}m remaining` : `${m}m remaining`;
  }
  const d = Math.floor(ms / 86_400_000);
  const h = Math.floor((ms % 86_400_000) / 3_600_000);
  return d > 0 ? `in ${d}d ${h}h` : `in ${h}h`;
}

function getDays(n = 7): Date[] {
  return Array.from({ length: n }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() + i);
    d.setHours(0, 0, 0, 0);
    return d;
  });
}

function shiftsOnDay(shifts: OnCallShift[], scheduleId: string, day: Date): OnCallShift[] {
  const start = day.getTime();
  const end = start + 86_400_000;
  return shifts.filter(
    (s) =>
      s.scheduleId === scheduleId &&
      new Date(s.start).getTime() < end &&
      new Date(s.end).getTime() > start,
  );
}

export function MyOnCalls({ app, currentUser, myShifts, allShifts, schedules, onOverrideCreated, onClose }: Props) {
  const [wizardShift, setWizardShift] = useState<OnCallShift | undefined>(undefined);
  const [showWizard, setShowWizard] = useState(false);

  const activeShift = myShifts.find(isNow);
  const nextShift = myShifts.filter((s) => !isNow(s)).sort(
    (a, b) => new Date(a.start).getTime() - new Date(b.start).getTime(),
  )[0];
  const days = getDays(7);
  const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  // Only show schedules that have at least one shift this week
  const activeScheduleIds = new Set(allShifts.map((s) => s.scheduleId));
  const visibleSchedules = schedules.filter((s) => activeScheduleIds.has(s.id));

  return (
    <>
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>📅 My On-Calls</h2>
            <button className="modal-close" onClick={onClose}>✕</button>
          </div>
          <div className="modal-body">
            {/* Countdown cards */}
            <div className="countdown-row">
              {activeShift ? (
                <div className="countdown-card active-now">
                  <div className="label">🟢 On-call now</div>
                  <div className="schedule-name">{activeShift.scheduleName}</div>
                  <div className="time-detail">{fmtDate(activeShift.start)} → {fmtDate(activeShift.end)}</div>
                  <div className="countdown-timer">{countdownLabel(activeShift)}</div>
                  <div className="actions">
                    <button className="btn btn-secondary btn-sm" onClick={() => { setWizardShift(activeShift); setShowWizard(true); }}>
                      🔄 Find coverage
                    </button>
                  </div>
                </div>
              ) : (
                <div className="countdown-card" style={{ borderColor: "var(--surface0)" }}>
                  <div className="label" style={{ color: "var(--overlay0)" }}>Not on-call</div>
                  <div className="schedule-name" style={{ color: "var(--overlay0)" }}>No active shift</div>
                </div>
              )}
              {nextShift ? (
                <div className="countdown-card upcoming">
                  <div className="label">🔵 Next shift</div>
                  <div className="schedule-name">{nextShift.scheduleName}</div>
                  <div className="time-detail">{fmtDate(nextShift.start)} → {fmtDate(nextShift.end)}</div>
                  <div className="countdown-timer">{countdownLabel(nextShift)}</div>
                  <div className="actions">
                    <button className="btn btn-secondary btn-sm" onClick={() => { setWizardShift(nextShift); setShowWizard(true); }}>
                      🔄 Find coverage
                    </button>
                  </div>
                </div>
              ) : !activeShift ? (
                <div className="countdown-card" style={{ borderColor: "var(--surface0)" }}>
                  <div className="label" style={{ color: "var(--overlay0)" }}>Next shift</div>
                  <div className="schedule-name" style={{ color: "var(--overlay0)" }}>No upcoming shifts</div>
                </div>
              ) : null}
            </div>

            {/* 7-day grid */}
            <p className="section-heading">7-Day Schedule</p>
            <div className="schedule-grid-wrap">
              <table className="schedule-grid-table">
                <thead>
                  <tr>
                    <th>Schedule</th>
                    {days.map((d) => (
                      <th key={d.toISOString()} style={{ width: `${85 / 7}%` }}>
                        <div style={{ fontSize: 9, color: "var(--overlay0)" }}>{DAY_NAMES[d.getDay()]}</div>
                        <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text)" }}>{d.getDate()}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {visibleSchedules.map((sched) => (
                    <tr key={sched.id}>
                      <td style={{ fontSize: 11 }}>{sched.name}</td>
                      {days.map((day) => {
                        const dayShifts = shiftsOnDay(allShifts, sched.id, day);
                        return (
                          <td key={day.toISOString()}>
                            {dayShifts.map((s, i) => {
                              const color = userColor(s.userId);
                              const firstName = s.userName.split(" ")[0];
                              return (
                                <span
                                  key={i}
                                  className="shift-bar"
                                  style={{ background: color, color: USER_COLOR_FG }}
                                  title={`${s.userName}: ${new Date(s.start).toLocaleDateString()} → ${new Date(s.end).toLocaleDateString()}`}
                                >
                                  {firstName}
                                </span>
                              );
                            })}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                  {visibleSchedules.length === 0 && (
                    <tr><td colSpan={8} className="empty-state">No shifts in the next 7 days</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {showWizard && (
        <CoverageWizard
          app={app}
          shifts={myShifts}
          preselectedShift={wizardShift}
          onClose={() => setShowWizard(false)}
          onDone={() => { setShowWizard(false); onOverrideCreated(); }}
        />
      )}
    </>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/components/MyOnCalls.tsx
git commit -m "feat: MyOnCalls modal — colored bars, no empty rows, filter active schedules"
```

---

## Task 9: OverridesModal

**Files:**
- Create: `mcp-apps/oncall-manager/src/components/OverridesModal.tsx`
- Delete: `mcp-apps/oncall-manager/src/components/OverridesTab.tsx` (replaced by new file)

- [ ] **Step 1: Create OverridesModal.tsx**

```tsx
import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { createOverride, deleteOverride, fetchScheduleOverrides, fetchScheduleUsers } from "../api";
import type { OnCallShift, OverrideDetail, Schedule, ScheduleUser } from "../api";
import { USER_COLOR_FG, userColor } from "../utils/userColor";
import { CoverageWizard } from "./CoverageWizard";

interface Props {
  app: App;
  schedules: Schedule[];
  myShifts: OnCallShift[];
  onClose: () => void;
}

function fmtRange(start: string, end: string): string {
  const fmt = (iso: string) =>
    new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  return `${fmt(start)} → ${fmt(end)}`;
}

function toLocalInput(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function OverridesModal({ app, schedules, myShifts, onClose }: Props) {
  const [selectedScheduleId, setSelectedScheduleId] = useState(schedules[0]?.id ?? "");
  const [overrides, setOverrides] = useState<OverrideDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [showWizard, setShowWizard] = useState(false);

  // Create form state
  const [formUsers, setFormUsers] = useState<ScheduleUser[]>([]);
  const [formUser, setFormUser] = useState("");
  const [formStart, setFormStart] = useState(toLocalInput(new Date().toISOString()));
  const [formEnd, setFormEnd] = useState(toLocalInput(new Date(Date.now() + 86_400_000).toISOString()));
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const since = new Date().toISOString();
  const until = new Date(Date.now() + 30 * 86_400_000).toISOString();

  useEffect(() => {
    if (!selectedScheduleId) return;
    setLoading(true);
    fetchScheduleOverrides(app, selectedScheduleId, since, until)
      .then((items) => {
        const sched = schedules.find((s) => s.id === selectedScheduleId);
        setOverrides(items.map((o) => ({ ...o, scheduleName: sched?.name ?? selectedScheduleId })));
      })
      .catch(() => setOverrides([]))
      .finally(() => setLoading(false));
  }, [selectedScheduleId]);

  useEffect(() => {
    if (!selectedScheduleId) return;
    fetchScheduleUsers(app, selectedScheduleId)
      .then((users) => {
        setFormUsers(users);
        setFormUser(users[0]?.id ?? "");
      })
      .catch(() => setFormUsers([]));
  }, [selectedScheduleId]);

  async function handleCreate() {
    if (!selectedScheduleId || !formUser) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const ok = await createOverride(app, selectedScheduleId, formUser, new Date(formStart).toISOString(), new Date(formEnd).toISOString());
      if (ok) {
        setShowForm(false);
        // Reload
        const items = await fetchScheduleOverrides(app, selectedScheduleId, since, until);
        const sched = schedules.find((s) => s.id === selectedScheduleId);
        setOverrides(items.map((o) => ({ ...o, scheduleName: sched?.name ?? selectedScheduleId })));
      } else {
        setFormError("Failed to create override.");
      }
    } catch (e: any) {
      setFormError(e?.message ?? "Unexpected error");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(override: OverrideDetail) {
    const ok = await deleteOverride(app, override.scheduleId, override.id);
    if (ok) setOverrides((prev) => prev.filter((o) => o.id !== override.id));
  }

  return (
    <>
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>🔄 Overrides</h2>
            <div style={{ display: "flex", gap: 6, marginLeft: "auto", marginRight: 8 }}>
              <button className="btn btn-secondary btn-sm" onClick={() => setShowWizard(true)}>
                Find Coverage
              </button>
              <button className="btn btn-primary btn-sm" onClick={() => setShowForm((v) => !v)}>
                {showForm ? "Cancel" : "+ New Override"}
              </button>
            </div>
            <button className="modal-close" onClick={onClose}>✕</button>
          </div>
          <div className="modal-body">
            {/* Schedule picker */}
            <div className="schedule-picker">
              <label>Schedule:</label>
              <select value={selectedScheduleId} onChange={(e) => setSelectedScheduleId((e.target as HTMLSelectElement).value)}>
                {schedules.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>

            {/* Inline create form */}
            {showForm && (
              <div className="create-form" style={{ marginBottom: 16 }}>
                {formError && <p className="error-banner">{formError}</p>}
                <div className="form-row">
                  <div className="form-field">
                    <label>Override user</label>
                    <select value={formUser} onChange={(e) => setFormUser((e.target as HTMLSelectElement).value)}>
                      {formUsers.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
                    </select>
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-field">
                    <label>Start</label>
                    <input type="datetime-local" value={formStart} onChange={(e) => setFormStart((e.target as HTMLInputElement).value)} />
                  </div>
                  <div className="form-field">
                    <label>End</label>
                    <input type="datetime-local" value={formEnd} onChange={(e) => setFormEnd((e.target as HTMLInputElement).value)} />
                  </div>
                </div>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <button className="btn btn-primary" onClick={handleCreate} disabled={submitting || !formUser}>
                    {submitting ? "Creating…" : "Create Override"}
                  </button>
                </div>
              </div>
            )}

            {/* Override list */}
            {loading ? (
              <div className="loading-row"><span className="spinner" />Loading overrides…</div>
            ) : overrides.length === 0 ? (
              <p className="empty-state">No active or upcoming overrides for this schedule.</p>
            ) : (
              <div className="override-list">
                {overrides.map((o) => {
                  const color = userColor(o.user.id);
                  const initial = (o.user.name || "?")[0].toUpperCase();
                  return (
                    <div key={o.id} className="override-row">
                      <div className="or-user-dot" style={{ background: color, color: USER_COLOR_FG }}>{initial}</div>
                      <div className="or-info">
                        <div className="or-user">{o.user.name}</div>
                        <div className="or-meta">{fmtRange(o.start, o.end)}</div>
                      </div>
                      <div className="or-actions">
                        <span style={{ fontSize: 9, padding: "1px 6px", borderRadius: 3, background: "var(--surface0)", color: "var(--subtext0)" }}>
                          {new Date(o.start).getTime() <= Date.now() ? "Active" : "Upcoming"}
                        </span>
                        <button className="btn btn-ghost-danger btn-sm" onClick={() => handleDelete(o)} title="Delete override">✕</button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {showWizard && (
        <CoverageWizard
          app={app}
          shifts={myShifts}
          onClose={() => setShowWizard(false)}
          onDone={() => setShowWizard(false)}
        />
      )}
    </>
  );
}
```

- [ ] **Step 2: Delete old OverridesTab.tsx**

```bash
rm mcp-apps/oncall-manager/src/components/OverridesTab.tsx
```

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-manager/src/components/OverridesModal.tsx
git rm mcp-apps/oncall-manager/src/components/OverridesTab.tsx
git commit -m "feat: add OverridesModal with real override list, delete, coverage wizard"
```

---

## Task 10: SchedulesModal

**Files:**
- Create: `mcp-apps/oncall-manager/src/components/SchedulesModal.tsx`

- [ ] **Step 1: Create SchedulesModal.tsx**

```tsx
import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { fetchScheduleDetail, fetchSchedules, fetchUsers, saveScheduleDetail } from "../api";
import type { Schedule, ScheduleDetail, ScheduleUser } from "../api";
import { USER_COLOR_FG, userColor } from "../utils/userColor";

interface Props {
  app: App;
  onClose: () => void;
}

function fmtRotation(seconds: number): string {
  const days = Math.round(seconds / 86400);
  return days === 7 ? "Weekly" : days === 1 ? "Daily" : `${days} days`;
}

export function SchedulesModal({ app, onClose }: Props) {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [filtered, setFiltered] = useState<Schedule[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ScheduleDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [editDetail, setEditDetail] = useState<ScheduleDetail | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // User search for adding to layers
  const [userSearchQuery, setUserSearchQuery] = useState("");
  const [userSearchResults, setUserSearchResults] = useState<ScheduleUser[]>([]);
  const [addingToLayer, setAddingToLayer] = useState<string | null>(null); // layer id

  useEffect(() => {
    fetchSchedules(app).then((s) => { setSchedules(s); setFiltered(s); }).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!query) { setFiltered(schedules); return; }
    const q = query.toLowerCase();
    setFiltered(schedules.filter((s) => s.name.toLowerCase().includes(q)));
  }, [query, schedules]);

  useEffect(() => {
    if (!selectedId) return;
    setDetailLoading(true);
    setDetail(null);
    setEditDetail(null);
    fetchScheduleDetail(app, selectedId)
      .then((d) => { setDetail(d); setEditDetail(d ? JSON.parse(JSON.stringify(d)) : null); })
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  useEffect(() => {
    if (!userSearchQuery || !addingToLayer) { setUserSearchResults([]); return; }
    const t = setTimeout(() => {
      fetchUsers(app, userSearchQuery).then(setUserSearchResults).catch(() => setUserSearchResults([]));
    }, 300);
    return () => clearTimeout(t);
  }, [userSearchQuery, addingToLayer]);

  function moveUser(layerId: string, fromIdx: number, toIdx: number) {
    if (!editDetail) return;
    const newDetail = JSON.parse(JSON.stringify(editDetail)) as ScheduleDetail;
    const layer = newDetail.layers.find((l) => l.id === layerId);
    if (!layer) return;
    const [user] = layer.users.splice(fromIdx, 1);
    layer.users.splice(toIdx, 0, user);
    setEditDetail(newDetail);
  }

  function removeUserFromLayer(layerId: string, userId: string) {
    if (!editDetail) return;
    const newDetail = JSON.parse(JSON.stringify(editDetail)) as ScheduleDetail;
    const layer = newDetail.layers.find((l) => l.id === layerId);
    if (!layer) return;
    layer.users = layer.users.filter((u) => u.id !== userId);
    setEditDetail(newDetail);
  }

  function addUserToLayer(layerId: string, user: ScheduleUser) {
    if (!editDetail) return;
    const newDetail = JSON.parse(JSON.stringify(editDetail)) as ScheduleDetail;
    const layer = newDetail.layers.find((l) => l.id === layerId);
    if (!layer || layer.users.find((u) => u.id === user.id)) return;
    layer.users.push(user);
    setEditDetail(newDetail);
    setAddingToLayer(null);
    setUserSearchQuery("");
    setUserSearchResults([]);
  }

  async function handleSave() {
    if (!editDetail) return;
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    try {
      const ok = await saveScheduleDetail(app, editDetail);
      if (ok) { setSaveSuccess(true); setDetail(JSON.parse(JSON.stringify(editDetail))); }
      else { setSaveError("Failed to save schedule."); }
    } catch (e: any) {
      setSaveError(e?.message ?? "Unexpected error");
    } finally {
      setSaving(false);
    }
  }

  const hasChanges = detail && editDetail && JSON.stringify(detail.layers.map((l) => l.users)) !== JSON.stringify(editDetail.layers.map((l) => l.users));

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          {selectedId && (
            <button className="detail-back" style={{ marginBottom: 0, marginRight: 4 }} onClick={() => { setSelectedId(null); setDetail(null); setEditDetail(null); }}>
              ← Back
            </button>
          )}
          <h2>📋 Schedules</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {!selectedId ? (
            <>
              <input className="search-input" placeholder="Search schedules…" value={query} onChange={(e) => setQuery((e.target as HTMLInputElement).value)} />
              {loading ? (
                <div className="loading-row"><span className="spinner" />Loading schedules…</div>
              ) : filtered.length === 0 ? (
                <p className="empty-state">No schedules found.</p>
              ) : (
                filtered.map((s) => (
                  <div key={s.id} className="list-row" onClick={() => setSelectedId(s.id)}>
                    <div className="list-row-title">{s.name}</div>
                    <div className="list-row-meta">{s.timeZone}</div>
                    <span className="list-row-chevron">›</span>
                  </div>
                ))
              )}
            </>
          ) : detailLoading ? (
            <div className="loading-row"><span className="spinner" />Loading schedule…</div>
          ) : editDetail ? (
            <>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 16, fontWeight: 700 }}>{editDetail.name}</div>
                {editDetail.description && <div style={{ fontSize: 11, color: "var(--overlay0)", marginTop: 2 }}>{editDetail.description}</div>}
                <div style={{ fontSize: 10, color: "var(--overlay0)", marginTop: 2 }}>Timezone: {editDetail.timeZone}</div>
              </div>

              {saveError && <p className="error-banner">{saveError}</p>}
              {saveSuccess && <p style={{ color: "var(--green)", fontSize: 11, marginBottom: 10 }}>✓ Schedule saved successfully</p>}

              <p className="section-heading">Schedule Layers</p>
              {editDetail.layers.map((layer) => (
                <div key={layer.id} className="layer-card">
                  <div className="layer-header">
                    <span className="layer-title">{layer.name}</span>
                    <span className="layer-meta">{fmtRotation(layer.rotationSeconds)} rotation · {layer.users.length} users</span>
                  </div>
                  <div className="layer-users">
                    {layer.users.map((u, idx) => {
                      const color = userColor(u.id);
                      return (
                        <div key={u.id} className="layer-user-row">
                          <span className="layer-user-order">#{idx + 1}</span>
                          <div className="layer-user-dot" style={{ background: color, color: USER_COLOR_FG }}>{u.name[0]}</div>
                          <span className="layer-user-name">{u.name}</span>
                          <div style={{ display: "flex", gap: 2 }}>
                            {idx > 0 && (
                              <button className="btn btn-ghost btn-sm" onClick={() => moveUser(layer.id, idx, idx - 1)} title="Move up">↑</button>
                            )}
                            {idx < layer.users.length - 1 && (
                              <button className="btn btn-ghost btn-sm" onClick={() => moveUser(layer.id, idx, idx + 1)} title="Move down">↓</button>
                            )}
                            <button className="btn btn-ghost-danger btn-sm" onClick={() => removeUserFromLayer(layer.id, u.id)} title="Remove">✕</button>
                          </div>
                        </div>
                      );
                    })}
                    {/* Add user to layer */}
                    {addingToLayer === layer.id ? (
                      <div style={{ marginTop: 6 }}>
                        <input
                          className="user-search"
                          placeholder="Search users to add…"
                          value={userSearchQuery}
                          onChange={(e) => setUserSearchQuery((e.target as HTMLInputElement).value)}
                          autoFocus
                        />
                        {userSearchResults.length > 0 && (
                          <div className="user-list" style={{ maxHeight: 160 }}>
                            {userSearchResults.map((u) => (
                              <div key={u.id} className="user-option" onClick={() => addUserToLayer(layer.id, u)}>
                                <div className="user-option-dot" style={{ background: userColor(u.id), color: USER_COLOR_FG }}>{u.name[0]}</div>
                                <div className="user-option-info">
                                  <div className="user-name">{u.name}</div>
                                  <div className="user-email">{u.email}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                        <button className="btn btn-secondary btn-sm" style={{ marginTop: 4 }} onClick={() => { setAddingToLayer(null); setUserSearchQuery(""); }}>Cancel</button>
                      </div>
                    ) : (
                      <button className="btn btn-ghost btn-sm" style={{ marginTop: 4, alignSelf: "flex-start" }} onClick={() => setAddingToLayer(layer.id)}>
                        + Add user
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {hasChanges && (
                <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                  <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                    {saving ? "Saving…" : "Save Changes"}
                  </button>
                  <button className="btn btn-secondary" onClick={() => setEditDetail(JSON.parse(JSON.stringify(detail!)))}>
                    Discard
                  </button>
                </div>
              )}
            </>
          ) : (
            <p className="empty-state">Failed to load schedule.</p>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/components/SchedulesModal.tsx
git commit -m "feat: add SchedulesModal with schedule detail, layer user reorder/add/remove"
```

---

## Task 11: EscalationPoliciesModal

**Files:**
- Create: `mcp-apps/oncall-manager/src/components/EscalationPoliciesModal.tsx`

- [ ] **Step 1: Create EscalationPoliciesModal.tsx**

```tsx
import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import {
  createEscalationPolicy,
  deleteEscalationPolicy,
  fetchEscalationPolicies,
  fetchEscalationPolicy,
  fetchSchedules,
  fetchUsers,
  updateEscalationPolicy,
} from "../api";
import type { EscalationPolicy, EscalationRule, EscalationTarget, Schedule, ScheduleUser } from "../api";

interface Props {
  app: App;
  onClose: () => void;
}

function newRule(): EscalationRule {
  return { escalation_delay_in_minutes: 30, targets: [] };
}

function newPolicy(): Pick<EscalationPolicy, "name" | "description" | "num_loops" | "escalation_rules"> {
  return { name: "", description: null, num_loops: 0, escalation_rules: [newRule()] };
}

export function EscalationPoliciesModal({ app, onClose }: Props) {
  const [policies, setPolicies] = useState<EscalationPolicy[]>([]);
  const [filtered, setFiltered] = useState<EscalationPolicy[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editPolicy, setEditPolicy] = useState<EscalationPolicy | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createDraft, setCreateDraft] = useState(newPolicy());

  // Target search
  const [targetSearch, setTargetSearch] = useState("");
  const [targetSearchResults, setTargetSearchResults] = useState<Array<{ id: string; name: string; type: "user_reference" | "schedule_reference" }>>([]);
  const [addingTargetToRule, setAddingTargetToRule] = useState<number | null>(null); // rule index

  const [cachedSchedules, setCachedSchedules] = useState<Schedule[]>([]);
  const [cachedUsers, setCachedUsers] = useState<ScheduleUser[]>([]);

  useEffect(() => {
    fetchEscalationPolicies(app).then((p) => { setPolicies(p); setFiltered(p); }).finally(() => setLoading(false));
    fetchSchedules(app).then(setCachedSchedules).catch(() => {});
    fetchUsers(app).then(setCachedUsers).catch(() => {});
  }, []);

  useEffect(() => {
    if (!query) { setFiltered(policies); return; }
    const q = query.toLowerCase();
    setFiltered(policies.filter((p) => p.name.toLowerCase().includes(q)));
  }, [query, policies]);

  useEffect(() => {
    if (!selectedId) return;
    setDetailLoading(true);
    setEditPolicy(null);
    fetchEscalationPolicy(app, selectedId)
      .then((p) => setEditPolicy(p ? JSON.parse(JSON.stringify(p)) : null))
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  useEffect(() => {
    if (!targetSearch || addingTargetToRule === null) { setTargetSearchResults([]); return; }
    const q = targetSearch.toLowerCase();
    const users = cachedUsers.filter((u) => u.name.toLowerCase().includes(q)).map((u) => ({ id: u.id, name: u.name, type: "user_reference" as const }));
    const scheds = cachedSchedules.filter((s) => s.name.toLowerCase().includes(q)).map((s) => ({ id: s.id, name: s.name, type: "schedule_reference" as const }));
    setTargetSearchResults([...users, ...scheds].slice(0, 10));
  }, [targetSearch, addingTargetToRule, cachedUsers, cachedSchedules]);

  function updateRule(idx: number, patch: Partial<EscalationRule>) {
    if (!editPolicy) return;
    const rules = [...editPolicy.escalation_rules];
    rules[idx] = { ...rules[idx], ...patch };
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
  }

  function addRule() {
    if (!editPolicy) return;
    setEditPolicy({ ...editPolicy, escalation_rules: [...editPolicy.escalation_rules, newRule()] });
  }

  function removeRule(idx: number) {
    if (!editPolicy) return;
    const rules = editPolicy.escalation_rules.filter((_, i) => i !== idx);
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
  }

  function moveRule(from: number, to: number) {
    if (!editPolicy) return;
    const rules = [...editPolicy.escalation_rules];
    const [r] = rules.splice(from, 1);
    rules.splice(to, 0, r);
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
  }

  function addTarget(ruleIdx: number, t: { id: string; name: string; type: "user_reference" | "schedule_reference" }) {
    if (!editPolicy) return;
    const rules = [...editPolicy.escalation_rules];
    const rule = rules[ruleIdx];
    if (rule.targets.find((x) => x.id === t.id)) return;
    rules[ruleIdx] = { ...rule, targets: [...rule.targets, { id: t.id, type: t.type, summary: t.name }] };
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
    setAddingTargetToRule(null);
    setTargetSearch("");
  }

  function removeTarget(ruleIdx: number, targetId: string) {
    if (!editPolicy) return;
    const rules = [...editPolicy.escalation_rules];
    rules[ruleIdx] = { ...rules[ruleIdx], targets: rules[ruleIdx].targets.filter((t) => t.id !== targetId) };
    setEditPolicy({ ...editPolicy, escalation_rules: rules });
  }

  async function handleSave() {
    if (!editPolicy) return;
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    try {
      const ok = await updateEscalationPolicy(app, editPolicy.id, editPolicy);
      if (ok) { setSaveSuccess(true); setPolicies((prev) => prev.map((p) => (p.id === editPolicy.id ? editPolicy : p))); }
      else { setSaveError("Failed to save."); }
    } catch (e: any) {
      setSaveError(e?.message ?? "Unexpected error");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!editPolicy) return;
    if (!confirm(`Delete "${editPolicy.name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      const ok = await deleteEscalationPolicy(app, editPolicy.id);
      if (ok) {
        setPolicies((prev) => prev.filter((p) => p.id !== editPolicy.id));
        setSelectedId(null);
        setEditPolicy(null);
      }
    } finally {
      setDeleting(false);
    }
  }

  async function handleCreate() {
    setSaving(true);
    setSaveError(null);
    try {
      const created = await createEscalationPolicy(app, createDraft);
      if (created) {
        setPolicies((prev) => [...prev, created]);
        setShowCreateForm(false);
        setCreateDraft(newPolicy());
        setSelectedId(created.id);
      } else {
        setSaveError("Failed to create policy.");
      }
    } catch (e: any) {
      setSaveError(e?.message ?? "Unexpected error");
    } finally {
      setSaving(false);
    }
  }

  function renderRules(
    rules: EscalationRule[],
    onUpdateRule: (idx: number, patch: Partial<EscalationRule>) => void,
    onAddRule: () => void,
    onRemoveRule: (idx: number) => void,
    onMoveRule: (from: number, to: number) => void,
    onAddTarget: (ruleIdx: number, t: { id: string; name: string; type: "user_reference" | "schedule_reference" }) => void,
    onRemoveTarget: (ruleIdx: number, targetId: string) => void,
  ) {
    return (
      <>
        {rules.map((rule, ruleIdx) => (
          <div key={ruleIdx} className="ep-rule-card">
            <div className="ep-rule-header">
              <span className="ep-rule-num">{ruleIdx + 1}</span>
              <span className="ep-rule-delay">
                Escalate after{" "}
                <input
                  type="number"
                  min={1}
                  max={999}
                  value={rule.escalation_delay_in_minutes}
                  onChange={(e) => onUpdateRule(ruleIdx, { escalation_delay_in_minutes: parseInt((e.target as HTMLInputElement).value) || 30 })}
                  style={{ width: 48, background: "var(--surface1)", border: "none", borderRadius: 3, color: "var(--text)", padding: "1px 4px", fontSize: 11, textAlign: "center" }}
                />{" "}
                minutes
              </span>
              <div style={{ display: "flex", gap: 2 }}>
                {ruleIdx > 0 && <button className="btn btn-ghost btn-sm" onClick={() => onMoveRule(ruleIdx, ruleIdx - 1)}>↑</button>}
                {ruleIdx < rules.length - 1 && <button className="btn btn-ghost btn-sm" onClick={() => onMoveRule(ruleIdx, ruleIdx + 1)}>↓</button>}
                <button className="btn btn-ghost-danger btn-sm" onClick={() => onRemoveRule(ruleIdx)}>✕</button>
              </div>
            </div>
            <div className="ep-rule-body">
              {rule.targets.map((t) => (
                <div key={t.id} className="ep-target-row">
                  <span className="ep-target-icon">{t.type === "user_reference" ? "👤" : "📅"}</span>
                  <span className="ep-target-name">{t.summary}</span>
                  <span className="ep-target-type">{t.type === "user_reference" ? "User" : "Schedule"}</span>
                  <button className="btn btn-ghost-danger btn-sm" onClick={() => onRemoveTarget(ruleIdx, t.id)}>✕</button>
                </div>
              ))}
              {rule.targets.length === 0 && <p style={{ fontSize: 10, color: "var(--overlay0)", padding: "4px 0" }}>No targets — add a user or schedule below</p>}

              {addingTargetToRule === ruleIdx ? (
                <div style={{ marginTop: 6 }}>
                  <input
                    className="user-search"
                    placeholder="Search users or schedules…"
                    value={targetSearch}
                    onChange={(e) => setTargetSearch((e.target as HTMLInputElement).value)}
                    autoFocus
                  />
                  {targetSearchResults.length > 0 && (
                    <div className="user-list" style={{ maxHeight: 140 }}>
                      {targetSearchResults.map((t) => (
                        <div key={t.id} className="user-option" onClick={() => onAddTarget(ruleIdx, t)}>
                          <span style={{ fontSize: 14 }}>{t.type === "user_reference" ? "👤" : "📅"}</span>
                          <div className="user-option-info"><div className="user-name">{t.name}</div></div>
                        </div>
                      ))}
                    </div>
                  )}
                  <button className="btn btn-secondary btn-sm" style={{ marginTop: 4 }} onClick={() => { setAddingTargetToRule(null); setTargetSearch(""); }}>Cancel</button>
                </div>
              ) : (
                <button className="btn btn-ghost btn-sm" style={{ marginTop: 4, alignSelf: "flex-start" }} onClick={() => setAddingTargetToRule(ruleIdx)}>
                  + Add target
                </button>
              )}
            </div>
          </div>
        ))}
        <button className="btn btn-secondary btn-sm" onClick={onAddRule}>+ Add escalation rule</button>
      </>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          {selectedId && (
            <button className="detail-back" style={{ marginBottom: 0, marginRight: 4 }} onClick={() => { setSelectedId(null); setEditPolicy(null); setSaveSuccess(false); }}>
              ← Back
            </button>
          )}
          <h2>📊 Escalation Policies</h2>
          {!selectedId && (
            <button className="btn btn-primary btn-sm" style={{ marginLeft: "auto", marginRight: 8 }} onClick={() => setShowCreateForm((v) => !v)}>
              {showCreateForm ? "Cancel" : "+ New Policy"}
            </button>
          )}
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {!selectedId ? (
            <>
              {showCreateForm && (
                <div className="create-form" style={{ marginBottom: 16 }}>
                  <p className="section-heading">New Escalation Policy</p>
                  {saveError && <p className="error-banner">{saveError}</p>}
                  <div className="form-row">
                    <div className="form-field">
                      <label>Name *</label>
                      <input type="text" value={createDraft.name} onChange={(e) => setCreateDraft({ ...createDraft, name: (e.target as HTMLInputElement).value })} placeholder="Policy name" />
                    </div>
                    <div className="form-field" style={{ maxWidth: 100 }}>
                      <label>Loops</label>
                      <input type="number" min={0} max={9} value={createDraft.num_loops} onChange={(e) => setCreateDraft({ ...createDraft, num_loops: parseInt((e.target as HTMLInputElement).value) || 0 })} />
                    </div>
                  </div>
                  <div className="form-field">
                    <label>Description</label>
                    <textarea value={createDraft.description ?? ""} onChange={(e) => setCreateDraft({ ...createDraft, description: (e.target as HTMLTextAreaElement).value || null })} rows={2} />
                  </div>
                  {renderRules(
                    createDraft.escalation_rules,
                    (i, p) => { const r = [...createDraft.escalation_rules]; r[i] = { ...r[i], ...p }; setCreateDraft({ ...createDraft, escalation_rules: r }); },
                    () => setCreateDraft({ ...createDraft, escalation_rules: [...createDraft.escalation_rules, newRule()] }),
                    (i) => setCreateDraft({ ...createDraft, escalation_rules: createDraft.escalation_rules.filter((_, idx) => idx !== i) }),
                    (from, to) => { const r = [...createDraft.escalation_rules]; const [x] = r.splice(from, 1); r.splice(to, 0, x); setCreateDraft({ ...createDraft, escalation_rules: r }); },
                    (ruleIdx, t) => { const r = [...createDraft.escalation_rules]; r[ruleIdx] = { ...r[ruleIdx], targets: [...r[ruleIdx].targets, { id: t.id, type: t.type, summary: t.name }] }; setCreateDraft({ ...createDraft, escalation_rules: r }); setAddingTargetToRule(null); setTargetSearch(""); },
                    (ruleIdx, tid) => { const r = [...createDraft.escalation_rules]; r[ruleIdx] = { ...r[ruleIdx], targets: r[ruleIdx].targets.filter((t) => t.id !== tid) }; setCreateDraft({ ...createDraft, escalation_rules: r }); },
                  )}
                  <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
                    <button className="btn btn-primary" onClick={handleCreate} disabled={saving || !createDraft.name}>
                      {saving ? "Creating…" : "Create Policy"}
                    </button>
                  </div>
                </div>
              )}

              <input className="search-input" placeholder="Search escalation policies…" value={query} onChange={(e) => setQuery((e.target as HTMLInputElement).value)} />
              {loading ? (
                <div className="loading-row"><span className="spinner" />Loading policies…</div>
              ) : filtered.length === 0 ? (
                <p className="empty-state">No escalation policies found.</p>
              ) : (
                filtered.map((p) => (
                  <div key={p.id} className="list-row" onClick={() => setSelectedId(p.id)}>
                    <div className="list-row-title">{p.name}</div>
                    <div className="list-row-meta">{p.escalation_rules.length} rule{p.escalation_rules.length !== 1 ? "s" : ""}{p.services.length > 0 ? ` · ${p.services.length} service${p.services.length !== 1 ? "s" : ""}` : ""}</div>
                    <span className="list-row-chevron">›</span>
                  </div>
                ))
              )}
            </>
          ) : detailLoading ? (
            <div className="loading-row"><span className="spinner" />Loading policy…</div>
          ) : editPolicy ? (
            <>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 16, fontWeight: 700 }}>{editPolicy.name}</div>
                {editPolicy.description && <div style={{ fontSize: 11, color: "var(--overlay0)", marginTop: 2 }}>{editPolicy.description}</div>}
                <div style={{ fontSize: 10, color: "var(--overlay0)", marginTop: 2 }}>
                  Loops: {editPolicy.num_loops} · {editPolicy.services.length} service{editPolicy.services.length !== 1 ? "s" : ""}
                  {editPolicy.teams.length > 0 ? ` · ${editPolicy.teams.map((t) => t.summary).join(", ")}` : ""}
                </div>
              </div>

              {saveError && <p className="error-banner">{saveError}</p>}
              {saveSuccess && <p style={{ color: "var(--green)", fontSize: 11, marginBottom: 10 }}>✓ Policy saved successfully</p>}

              <p className="section-heading">Escalation Rules</p>
              {renderRules(
                editPolicy.escalation_rules,
                updateRule,
                addRule,
                removeRule,
                moveRule,
                addTarget,
                removeTarget,
              )}

              <hr className="divider" />
              <div style={{ display: "flex", gap: 8, justifyContent: "space-between" }}>
                <button className="btn btn-danger btn-sm" onClick={handleDelete} disabled={deleting}>
                  {deleting ? "Deleting…" : "Delete Policy"}
                </button>
                <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                  {saving ? "Saving…" : "Save Changes"}
                </button>
              </div>
            </>
          ) : (
            <p className="empty-state">Failed to load policy.</p>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/components/EscalationPoliciesModal.tsx
git commit -m "feat: add EscalationPoliciesModal with full CRUD (rules, targets, create, delete)"
```

---

## Task 12: Home screen — rewrite mcp-app.tsx

**Files:**
- Replace: `mcp-apps/oncall-manager/src/mcp-app.tsx`

- [ ] **Step 1: Replace mcp-app.tsx**

```tsx
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { useEffect, useState } from "react";
import { fetchAllOnCalls, fetchCurrentUser, fetchSchedules, fetchUserShifts } from "./api";
import type { CurrentUser, OnCallShift, Schedule } from "./api";
import { EscalationPoliciesModal } from "./components/EscalationPoliciesModal";
import { MyOnCalls } from "./components/MyOnCalls";
import { OverridesModal } from "./components/OverridesModal";
import { SchedulesModal } from "./components/SchedulesModal";
import "./styles.css";

const MOCK_MODE = import.meta.env.VITE_MOCK === "true";
type Modal = "myoncalls" | "overrides" | "schedules" | "escalations" | null;

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "On-Call Manager", version: "2.0.0" },
    capabilities: {},
  });

  const [modal, setModal] = useState<Modal>(null);
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [myShifts, setMyShifts] = useState<OnCallShift[]>([]);
  const [allShifts, setAllShifts] = useState<OnCallShift[]>([]);

  async function loadData() {
    setLoading(true);
    try {
      const since = new Date().toISOString();
      const until = new Date(Date.now() + 7 * 86_400_000).toISOString();
      const user = await fetchCurrentUser(app ?? ({} as any));
      setCurrentUser(user);
      const [scheds, myS, allS] = await Promise.all([
        fetchSchedules(app ?? ({} as any)),
        user ? fetchUserShifts(app ?? ({} as any), user.id, since, until) : Promise.resolve([]),
        fetchAllOnCalls(app ?? ({} as any), since, until),
      ]);
      setSchedules(scheds);
      setMyShifts(myS);
      setAllShifts(allS);
    } catch {
      // silently fail — cards show counts as 0
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!app && !MOCK_MODE) return;
    loadData();
  }, [app]);

  if (!app && !MOCK_MODE) {
    return (
      <div className="app">
        <div className="app-header">
          <span className="dot">●</span>
          <h1>On-Call Manager</h1>
        </div>
        <div className="empty-state" style={{ marginTop: 80 }}>
          {connectionError ? `Connection error: ${connectionError.message}` : "Waiting for MCP connection…"}
        </div>
      </div>
    );
  }

  const activeNow = myShifts.filter((s) => {
    const now = Date.now();
    return new Date(s.start).getTime() <= now && new Date(s.end).getTime() > now;
  });
  const nextShift = myShifts
    .filter((s) => new Date(s.start).getTime() > Date.now())
    .sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())[0];

  function myOnCallsBadge() {
    if (loading) return null;
    if (activeNow.length > 0) return <span className="home-card-badge active">● On-call now</span>;
    if (nextShift) {
      const ms = new Date(nextShift.start).getTime() - Date.now();
      const h = Math.floor(ms / 3_600_000);
      const d = Math.floor(ms / 86_400_000);
      return <span className="home-card-badge info">Next in {d > 0 ? `${d}d` : `${h}h`}</span>;
    }
    return <span className="home-card-badge" style={{ color: "var(--overlay0)" }}>No shifts</span>;
  }

  return (
    <div className="app">
      <div className="app-header">
        <span className="dot">●</span>
        <h1>On-Call Manager</h1>
        {currentUser && <span className="user-chip">{currentUser.name}</span>}
      </div>

      <div className="home-grid">
        <div className="home-card" onClick={() => setModal("myoncalls")}>
          <div className="home-card-icon">📅</div>
          <div className="home-card-title">My On-Calls</div>
          <div className="home-card-desc">View your upcoming shifts and find coverage for any shift.</div>
          {myOnCallsBadge()}
        </div>

        <div className="home-card" onClick={() => setModal("overrides")}>
          <div className="home-card-icon">🔄</div>
          <div className="home-card-title">Overrides</div>
          <div className="home-card-desc">Create, view, and delete schedule overrides across all schedules.</div>
          {!loading && <span className="home-card-badge info">{schedules.length} schedule{schedules.length !== 1 ? "s" : ""}</span>}
        </div>

        <div className="home-card" onClick={() => setModal("schedules")}>
          <div className="home-card-icon">📋</div>
          <div className="home-card-title">Schedules</div>
          <div className="home-card-desc">Browse schedules, view rotation layers, and manage who's on each rotation.</div>
          {!loading && <span className="home-card-badge info">{schedules.length} schedules</span>}
        </div>

        <div className="home-card" onClick={() => setModal("escalations")}>
          <div className="home-card-icon">📊</div>
          <div className="home-card-title">Escalation Policies</div>
          <div className="home-card-desc">View and edit escalation rules — add targets, adjust delays, create new policies.</div>
        </div>
      </div>

      {modal === "myoncalls" && (
        <MyOnCalls
          app={app ?? ({} as any)}
          currentUser={currentUser ?? { id: "", name: "Unknown", email: "" }}
          myShifts={myShifts}
          allShifts={allShifts}
          schedules={schedules}
          onOverrideCreated={loadData}
          onClose={() => setModal(null)}
        />
      )}
      {modal === "overrides" && (
        <OverridesModal
          app={app ?? ({} as any)}
          schedules={schedules}
          myShifts={myShifts}
          onClose={() => setModal(null)}
        />
      )}
      {modal === "schedules" && (
        <SchedulesModal
          app={app ?? ({} as any)}
          onClose={() => setModal(null)}
        />
      )}
      {modal === "escalations" && (
        <EscalationPoliciesModal
          app={app ?? ({} as any)}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  );
}

export default function McpApp() {
  return <App />;
}

const rootEl = document.getElementById("root");
if (rootEl) {
  import("react-dom/client").then(({ createRoot }) => {
    createRoot(rootEl).render(<McpApp />);
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/mcp-app.tsx
git commit -m "feat: rewrite mcp-app.tsx as 4-card home screen with modal routing"
```

---

## Task 13: Typecheck + build + deploy

**Files:**
- Modify: `pagerduty_mcp/oncall_manager_view.html` (rebuilt artifact)

- [ ] **Step 1: Run typecheck**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/oncall-manager
source ~/.nvm/nvm.sh && nvm use
npm run typecheck
```

Expected: exit 0. Fix any errors before proceeding.

Common fixes needed:
- `OverridesTab` import in mcp-app.tsx removed (replaced by `OverridesModal`) — already handled
- `OnCallShift` type now has `userId` and `userName` fields — verify CoverageWizard and MyOnCalls use the new fields, not old ones
- `app` type: `app ?? ({} as any)` pattern is intentional

- [ ] **Step 2: Build**

```bash
npm run build
```

Expected: `dist/mcp-app.html` produced (single-file bundle).

- [ ] **Step 3: Deploy**

```bash
cp dist/mcp-app.html ../../pagerduty_mcp/oncall_manager_view.html
```

- [ ] **Step 4: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add pagerduty_mcp/oncall_manager_view.html mcp-apps/oncall-manager/dist/mcp-app.html
git commit -m "feat: deploy oncall-manager v2 bundle (home cards, full CRUD)"
```

---

## Self-Review

**Spec coverage:**
- ✅ 4-card home screen (My On-Calls, Overrides, Schedules, Escalation Policies)
- ✅ "No users found" fix — fallback to `list_oncalls` when `list_schedule_users` returns empty
- ✅ Colored user bars in grid — `userColor(userId)` via hash, first name shown
- ✅ Empty schedule rows filtered out from grid
- ✅ Availability badges in wizard step 2 (✓ Free / ⚠ On-call)
- ✅ Override list via `list_schedule_overrides` — real data per schedule
- ✅ Delete override via `delete_schedule_override`
- ✅ Schedule detail: layer users, reorder, add user, remove user, save
- ✅ Escalation policy: view rules, edit delay, add/remove targets, add/remove rules, reorder rules, save, delete, create new
- ✅ New Python tools registered (list_schedule_overrides, delete_schedule_override, create/update/delete_escalation_policy)
- ✅ `mime_type="text/html;profile=mcp-app"` unchanged (not touched in this PR)

**Type consistency:**
- `OnCallShift` now includes `userId` and `userName` — Tasks 7 and 8 use these fields
- `OverrideDetail` has `scheduleId` and `scheduleName` set by the caller
- `ScheduleDetail.layers[].users` are `ScheduleUser[]` — consistent throughout Tasks 9 and 10
- `EscalationRule.targets` are `EscalationTarget[]` with `id`, `type`, `summary` — consistent in Tasks 11 and 4
