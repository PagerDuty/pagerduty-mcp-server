# Onboarding Wizard MCP App — Design Spec

**Date:** 2026-05-08  
**Branch:** `feature/onboarding-wizard` (from `feature/new-mcp-apps`)  
**Status:** Approved

---

## Goal

Build a 7-phase structured wizard MCP App in `pagerduty-mcp-server` that replicates the full PagerDuty onboarding journey from the production assistant (`csg-innv-onb-asst-client-ecs`). Users trigger it via a Claude tool call; the wizard runs in a sandboxed iframe and calls existing PagerDuty MCP tools directly — no LLM backend required.

**Reference production app:** https://onboarding-assistant.innovation.csg.pagerduty.com/assistant

---

## Scope

### In scope
- 7-phase linear wizard with skip support: Teams → Users → Schedules → Escalation Policies → Services → AIOps → Incident Workflows
- New `create_user` tool added to `pagerduty_mcp/tools/users.py` (POST /users, no invite email)
- CSV bulk upload for Users phase: drag-drop, browser-side parse, batch `create_user` calls with per-row status
- Review summary screen after all phases
- Mock mode (`npm run dev:mock`) for development without MCP connection
- Playwright test suite
- Dark mode support

### Out of scope
- User invitation emails
- Conversational / LLM-driven interaction
- CSV template download (sandbox restriction — schema shown inline instead)
- Persistent state across sessions (wizard state lives in React only)

---

## Architecture

```
pagerduty-mcp-server/
├── mcp-apps/onboarding-wizard/
│   ├── src/
│   │   ├── mcp-app.tsx                  # Wizard shell + stepper
│   │   ├── api.ts                       # callServerTool wrappers + MOCK_MODE guard
│   │   ├── mock.ts                      # Seed data for all 7 phases
│   │   ├── styles.css                   # CSS variables, stepper, form, CSV table
│   │   └── components/
│   │       ├── Stepper.tsx              # Phase progress header (7 steps)
│   │       ├── PhaseTeams.tsx           # create_team / select existing
│   │       ├── PhaseUsers.tsx           # create_user (single) + CsvUpload
│   │       ├── PhaseSchedules.tsx       # create_schedule + assign users
│   │       ├── PhaseEscalationPolicies.tsx
│   │       ├── PhaseServices.tsx
│   │       ├── PhaseAIOps.tsx
│   │       ├── PhaseIncidentWorkflows.tsx
│   │       ├── CsvUpload.tsx            # Drag-drop, parse, batch, progress
│   │       └── ReviewSummary.tsx        # Final confirmation screen
│   ├── server.ts
│   ├── main.ts
│   ├── mcp-app.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.server.json
│   ├── vite.config.ts
│   └── pw-test.spec.mjs
│
├── pagerduty_mcp/
│   ├── tools/users.py                   # + create_user (new write tool)
│   ├── onboarding_wizard_view.html      # Built bundle (cp dist/mcp-app.html)
│   └── server.py                        # + add_onboarding_wizard()
```

---

## Phase Breakdown

| # | Phase | Read tools | Write tools | Notes |
|---|-------|-----------|-------------|-------|
| 1 | Teams | `list_teams` | `create_team` | Can select existing or create new |
| 2 | Users | `list_users` | `create_user` (new) | Single form + CSV bulk upload |
| 3 | Schedules | `list_schedules`, `list_users` | `create_schedule` | Assign users from phase 2 |
| 4 | Escalation Policies | `list_escalation_policies`, `list_schedules` | `create_escalation_policy` | References schedule from phase 3 |
| 5 | Services | `list_services`, `list_escalation_policies` | `create_service` | References EP from phase 4 |
| 6 | AIOps | `list_event_orchestrations` | `append_event_orchestration_router_rule` | Optional — skip encouraged if no orchestrations exist |
| 7 | Incident Workflows | `list_incident_workflows` | `start_incident_workflow` | Optional — list existing, trigger one |

---

## Wizard State

Held in React (`useState`), not persisted across sessions:

```ts
interface WizardState {
  currentPhase: number;                  // 0-6
  completedPhases: Set<number>;
  selectedTeam: Team | null;             // Phase 1 output
  createdUsers: User[];                  // Phase 2 output
  createdSchedule: Schedule | null;      // Phase 3 output
  createdEscalationPolicy: EscalationPolicy | null; // Phase 4 output
  createdService: Service | null;        // Phase 5 output
}
```

Phase outputs feed as defaults into subsequent phases (e.g. Phase 3 pre-selects users created in Phase 2).

---

## New Tool: `create_user`

Added to `pagerduty_mcp/tools/users.py` as a write tool.

```python
class CreateUserRequest(BaseModel):
    name: str
    email: str
    role: str = "user"          # user | admin | read_only_user | etc.
    time_zone: str = "UTC"

def create_user(request: CreateUserRequest) -> User:
    """Create a new PagerDuty user. No invitation email is sent."""
    # POST /users via existing pd_client
```

Registered in `tools/__init__.py` write_tools list. Uses existing `PDClient` pattern.

---

## CSV Upload (Phase 2)

**Schema** (matching production exactly):
```
Team Name, User Name, Email, Voice, SMS, Team Role, User Role
```

**Flow:**
1. Drag-drop or click-to-browse (`<input type="file" accept=".csv">`)
2. Browser-side parse (PapaParse or manual split) — validates all 7 columns present
3. Preview table: show first 5 rows + total count
4. "Import N users" button → batch `create_user` calls
5. Per-row status column: ⏳ pending → ✓ created / ✗ error (with message)
6. Summary: X created, Y failed — option to retry failed rows

**Sandbox note:** `allow-downloads` not available — CSV template not downloadable. Schema shown as inline code block above the upload zone.

---

## Python Server Registration

```python
# pagerduty_mcp/server.py

ONBOARDING_WIZARD_URI = "ui://onboarding-wizard/mcp-app.html"

def add_onboarding_wizard(mcp_instance: FastMCP) -> None:
    @mcp_instance.tool(
        meta={"ui": {"resourceUri": ONBOARDING_WIZARD_URI},
              "ui/resourceUri": ONBOARDING_WIZARD_URI}
    )
    def onboarding_wizard() -> list[TextContent]:
        """Guided 7-phase wizard to set up PagerDuty: teams, users, schedules,
        escalation policies, services, AIOps, and incident workflows. UI calls
        existing MCP tools."""
        return [TextContent(type="text", text="Onboarding Wizard initialized.")]

    @mcp_instance.resource(
        ONBOARDING_WIZARD_URI,
        mime_type="text/html;profile=mcp-app",
        description="PagerDuty onboarding wizard — 7-phase structured setup",
    )
    def onboarding_wizard_view() -> str:
        html_path = pathlib.Path(__file__).parent / "onboarding_wizard_view.html"
        return html_path.read_text(encoding="utf-8")
```

---

## Error Handling

- Each `callServerTool` call wrapped in try/catch; errors shown inline per phase, non-blocking
- Phase list-load failure → inline retry button, does not block wizard progression
- CSV: column validation before any API calls; invalid schema shows required columns
- Wizard state preserved across phase errors — user can retry without starting over

---

## Testing

**Mock mode:** `npm run dev:mock` with seed data for all 7 phases (2 teams, 5 users, 2 schedules, 1 EP, 1 service, 1 orchestration, 1 workflow).

**Playwright tests (`pw-test.spec.mjs`):**
- Wizard renders with 7-step stepper
- Each phase: form fields present, "Next" advances stepper, "Skip" also advances
- CSV upload: valid file → preview table → import button appears
- Dark mode: `?theme=dark` — text contrast check
- Review summary renders after phase 7

---

## Build & Deploy

```bash
cd mcp-apps/onboarding-wizard
npm run build
cp dist/mcp-app.html ../../pagerduty_mcp/onboarding_wizard_view.html
```

`emptyOutDir: false` preserves `dist/server.js` + `dist/main.js`.
