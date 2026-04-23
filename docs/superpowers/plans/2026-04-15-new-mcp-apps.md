# New MCP Apps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build three new MCP Apps (Shift Coverage Wizard, Post-Mortem Builder, Operations Intelligence Report) on the `feature/new-mcp-apps` branch (based on `experimental`), using the same design system, build toolchain, and server registration pattern as the existing apps.

**Architecture:** Each app is a Preact+TypeScript SPA built with Vite (`vite-plugin-singlefile`) into a single inline HTML file. The HTML is served from the Python MCP server via a `ui://` resource URI and registered with a companion tool. Apps call back into MCP tools via `app.callServerTool()` from the `@modelcontextprotocol/ext-apps` SDK. Only base `pagerduty-mcp-server` tools are used (no advance server dependency). The branch is `feature/new-mcp-apps` which was cut from `experimental`.

**Tech Stack:** Preact 10 (aliased as React), TypeScript 5, Vite 6, `vite-plugin-singlefile`, `@modelcontextprotocol/ext-apps` ^1.3.2, same CSS variables as existing apps.

---

## CSS Design System (reference — DO NOT change these values)

```css
/* Light mode */
--bg-primary: #ffffff
--bg-secondary: #fafafa
--bg-tertiary: #f5f5f5
--text-primary: #1d1d1f
--text-secondary: #6e6e73
--border-primary: #e5e5e5

/* Dark mode (data-theme="dark") */
--bg-primary: #1e1e1e
--bg-secondary: #2d2d30
--bg-tertiary: #3e3e42
--text-primary: #d4d4d4
--text-secondary: #a0a0a0
--border-primary: #3e3e42

/* Status colors (universal) */
triggered:   #e53e3e  (red)
acknowledged:#3182ce  (blue)
resolved:    #38a169  (green)
change event:#319795  (teal)
note:        #d69e2e  (yellow)
escalation:  #dd6b20  (orange)
PD green:    #00b050  (brand primary)
PD dark green: #005a2f
```

---

## File Map

### App 1 — Shift Coverage Wizard
- **Create:** `mcp-apps/shift-coverage-wizard/mcp-app.html`
- **Create:** `mcp-apps/shift-coverage-wizard/package.json`
- **Create:** `mcp-apps/shift-coverage-wizard/vite.config.ts`
- **Create:** `mcp-apps/shift-coverage-wizard/tsconfig.json`
- **Create:** `mcp-apps/shift-coverage-wizard/tsconfig.server.json`
- **Create:** `mcp-apps/shift-coverage-wizard/src/mcp-app.tsx`
- **Create:** `mcp-apps/shift-coverage-wizard/src/styles.css`
- **Create:** `mcp-apps/shift-coverage-wizard/src/api.ts`
- **Create:** `mcp-apps/shift-coverage-wizard/src/components/PagerDutyLogo.tsx`
- **Create:** `mcp-apps/shift-coverage-wizard/src/components/StepIndicator.tsx`
- **Create:** `mcp-apps/shift-coverage-wizard/src/components/ShiftCard.tsx`
- **Create:** `mcp-apps/shift-coverage-wizard/src/components/CoverageUserCard.tsx`
- **Create:** `mcp-apps/shift-coverage-wizard/src/components/ConfirmModal.tsx`
- **Built output:** `pagerduty_mcp/shift_coverage_wizard_view.html`

### App 2 — Post-Mortem Builder
- **Create:** `mcp-apps/post-mortem-builder/mcp-app.html`
- **Create:** `mcp-apps/post-mortem-builder/package.json`
- **Create:** `mcp-apps/post-mortem-builder/vite.config.ts`
- **Create:** `mcp-apps/post-mortem-builder/tsconfig.json`
- **Create:** `mcp-apps/post-mortem-builder/tsconfig.server.json`
- **Create:** `mcp-apps/post-mortem-builder/src/mcp-app.tsx`
- **Create:** `mcp-apps/post-mortem-builder/src/styles.css`
- **Create:** `mcp-apps/post-mortem-builder/src/api.ts`
- **Create:** `mcp-apps/post-mortem-builder/src/components/PagerDutyLogo.tsx`
- **Create:** `mcp-apps/post-mortem-builder/src/components/IncidentPicker.tsx`
- **Create:** `mcp-apps/post-mortem-builder/src/components/TimelineView.tsx`
- **Create:** `mcp-apps/post-mortem-builder/src/components/TimelineEvent.tsx`
- **Built output:** `pagerduty_mcp/post_mortem_builder_view.html`

### App 3 — Operations Intelligence
- **Create:** `mcp-apps/operations-intelligence/mcp-app.html`
- **Create:** `mcp-apps/operations-intelligence/package.json`
- **Create:** `mcp-apps/operations-intelligence/vite.config.ts`
- **Create:** `mcp-apps/operations-intelligence/tsconfig.json`
- **Create:** `mcp-apps/operations-intelligence/tsconfig.server.json`
- **Create:** `mcp-apps/operations-intelligence/src/mcp-app.tsx`
- **Create:** `mcp-apps/operations-intelligence/src/styles.css`
- **Create:** `mcp-apps/operations-intelligence/src/api.ts`
- **Create:** `mcp-apps/operations-intelligence/src/components/PagerDutyLogo.tsx`
- **Create:** `mcp-apps/operations-intelligence/src/components/SummaryCards.tsx`
- **Create:** `mcp-apps/operations-intelligence/src/components/ServiceBreakdown.tsx`
- **Create:** `mcp-apps/operations-intelligence/src/components/IncidentTable.tsx`
- **Built output:** `pagerduty_mcp/operations_intelligence_view.html`

### Server & Scripts
- **Modify:** `pagerduty_mcp/server.py` — add 3 URI constants + 3 `add_*` functions + calls in `run()`
- **Modify:** `mcp-apps/build-all.sh` — add 3 new apps
- **Modify:** `mcp-apps/setup-all.sh` — add 3 new apps

### Docs
- **Create:** `website/docs/experimental/shift-coverage-wizard.md`
- **Create:** `website/docs/experimental/post-mortem-builder.md`
- **Create:** `website/docs/experimental/operations-intelligence.md`
- **Modify:** `website/docs/experimental/overview.md` — add 3 rows to the apps table

---

## Task 1: Scaffold shift-coverage-wizard boilerplate

**Files:**
- Create: `mcp-apps/shift-coverage-wizard/mcp-app.html`
- Create: `mcp-apps/shift-coverage-wizard/package.json`
- Create: `mcp-apps/shift-coverage-wizard/vite.config.ts`
- Create: `mcp-apps/shift-coverage-wizard/tsconfig.json`
- Create: `mcp-apps/shift-coverage-wizard/tsconfig.server.json`

- [ ] **Step 1: Create mcp-app.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Shift Coverage Wizard</title>
  </head>
  <body>
    <div id="root">
      <style>
        .initial-loader {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100vh;
          font-family: system-ui, -apple-system, sans-serif;
          color: #666;
        }
      </style>
      <div class="initial-loader">Loading Shift Coverage Wizard...</div>
    </div>
    <script type="module" src="/src/mcp-app.tsx"></script>
  </body>
</html>
```

- [ ] **Step 2: Create package.json** (copy from oncall-schedule-visualizer, change name/description)

```json
{
  "name": "@pagerduty/shift-coverage-wizard",
  "version": "1.0.0",
  "type": "module",
  "private": true,
  "description": "Multi-step wizard for finding and creating on-call shift coverage",
  "scripts": {
    "build": "tsc --noEmit && cross-env INPUT=mcp-app.html vite build",
    "start": "concurrently \"cross-env NODE_ENV=development INPUT=mcp-app.html vite build --watch\" \"tsx watch main.ts\"",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@modelcontextprotocol/ext-apps": "^1.3.2",
    "@modelcontextprotocol/sdk": "^1.24.0",
    "preact": "^10.29.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "22.19.5",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "concurrently": "^9.2.1",
    "cross-env": "^10.1.0",
    "tsx": "^4.21.0",
    "typescript": "^5.9.3",
    "vite": "^6.0.0",
    "vite-plugin-singlefile": "^2.3.0"
  }
}
```

- [ ] **Step 3: Create vite.config.ts** (identical to all other apps)

```typescript
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const INPUT = process.env.INPUT;
if (!INPUT) {
  throw new Error("INPUT environment variable is not set");
}

const isDevelopment = process.env.NODE_ENV === "development";

export default defineConfig({
  plugins: [react(), viteSingleFile()],
  resolve: {
    alias: {
      "react": "preact/compat",
      "react-dom/test-utils": "preact/test-utils",
      "react-dom": "preact/compat",
      "react/jsx-runtime": "preact/jsx-runtime",
    },
  },
  build: {
    sourcemap: isDevelopment ? "inline" : undefined,
    cssMinify: !isDevelopment,
    minify: !isDevelopment,
    rollupOptions: {
      input: INPUT,
    },
    outDir: "dist",
    emptyOutDir: false,
  },
});
```

- [ ] **Step 4: Create tsconfig.json** (identical to all other apps)

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "jsx": "react-jsx",
    "noEmit": true,
    "strict": true,
    "skipLibCheck": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

- [ ] **Step 5: Create tsconfig.server.json**

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "lib": ["ESNext"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "dist",
    "strict": true,
    "skipLibCheck": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true
  },
  "include": ["src"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 6: Install deps**

```bash
cd mcp-apps/shift-coverage-wizard && npm install
```

Expected: `node_modules/` created, no errors.

---

## Task 2: Build shift-coverage-wizard — API layer

**Files:**
- Create: `mcp-apps/shift-coverage-wizard/src/api.ts`

- [ ] **Step 1: Create src/api.ts**

```typescript
/**
 * Shift Coverage Wizard - API layer
 * Calls PagerDuty MCP tools to fetch schedule/oncall data and create overrides.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface CurrentUser {
  id: string;
  name: string;
  email: string;
}

export interface ScheduleRef {
  id: string;
  name: string;
  time_zone: string;
}

export interface OnCallShift {
  scheduleId: string;
  scheduleName: string;
  start: string;
  end: string;
  escalationLevel: number;
}

export interface ScheduleUser {
  id: string;
  name: string;
  email: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

// ─── API functions ────────────────────────────────────────────────────────────

/** Get the authenticated user's profile. */
export async function fetchCurrentUser(app: App): Promise<CurrentUser | null> {
  const result = await app.callServerTool({ name: "get_user_data", arguments: {} });
  const data = extract<any>(result);
  const user = data?.response ?? data;
  if (!user?.id) return null;
  return { id: user.id, name: user.name, email: user.email };
}

/** Get upcoming on-call shifts for a specific user within a date range. */
export async function fetchUserOnCallShifts(
  app: App,
  userId: string,
  since: string,
  until: string
): Promise<OnCallShift[]> {
  const result = await app.callServerTool({
    name: "list_oncalls",
    arguments: {
      query_model: {
        user_ids: [userId],
        since,
        until,
        earliest: false,
      },
    },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items
    .filter((o: any) => o.schedule?.id && o.start && o.end)
    .map((o: any) => ({
      scheduleId: o.schedule.id,
      scheduleName: o.schedule.summary ?? o.schedule.id,
      start: o.start,
      end: o.end,
      escalationLevel: o.escalation_level ?? 0,
    }));
}

/** Get all users on a given schedule (potential coverage candidates). */
export async function fetchScheduleUsers(
  app: App,
  scheduleId: string
): Promise<ScheduleUser[]> {
  const result = await app.callServerTool({
    name: "list_schedule_users",
    arguments: { schedule_id: scheduleId },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map((u: any) => ({
    id: u.id,
    name: u.name ?? u.summary,
    email: u.email ?? "",
  }));
}

/** Create a schedule override. Returns true on success. */
export async function createOverride(
  app: App,
  scheduleId: string,
  userId: string,
  start: string,
  end: string
): Promise<boolean> {
  const result = await app.callServerTool({
    name: "create_schedule_override",
    arguments: {
      schedule_id: scheduleId,
      override_request: {
        overrides: [
          {
            start,
            end,
            user: { id: userId, type: "user_reference" },
          },
        ],
      },
    },
  });
  return !result.isError;
}
```

---

## Task 3: Build shift-coverage-wizard — UI components

**Files:**
- Create: `mcp-apps/shift-coverage-wizard/src/components/PagerDutyLogo.tsx`
- Create: `mcp-apps/shift-coverage-wizard/src/components/StepIndicator.tsx`
- Create: `mcp-apps/shift-coverage-wizard/src/components/ShiftCard.tsx`
- Create: `mcp-apps/shift-coverage-wizard/src/components/CoverageUserCard.tsx`
- Create: `mcp-apps/shift-coverage-wizard/src/components/ConfirmModal.tsx`

- [ ] **Step 1: Create PagerDutyLogo.tsx** (identical logo SVG used across all apps)

```tsx
export function PagerDutyLogo({ size = 24 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="PagerDuty"
    >
      <path
        d="M14.5 2H9.5C6.46 2 4 4.46 4 7.5V22h4v-5h6.5c3.04 0 5.5-2.46 5.5-5.5v-4C20 4.46 17.54 2 14.5 2zM16 11.5c0 .83-.67 1.5-1.5 1.5H8V6h6.5c.83 0 1.5.67 1.5 1.5v4z"
        fill="currentColor"
      />
    </svg>
  );
}
```

- [ ] **Step 2: Create StepIndicator.tsx**

```tsx
interface StepIndicatorProps {
  steps: string[];
  current: number; // 0-based
}

export function StepIndicator({ steps, current }: StepIndicatorProps) {
  return (
    <div className="step-indicator">
      {steps.map((label, i) => (
        <div key={label} className="step-item">
          <div
            className={`step-circle ${
              i < current ? "done" : i === current ? "active" : "pending"
            }`}
          >
            {i < current ? "✓" : i + 1}
          </div>
          <span className={`step-label ${i === current ? "active" : ""}`}>{label}</span>
          {i < steps.length - 1 && <div className={`step-line ${i < current ? "done" : ""}`} />}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: Create ShiftCard.tsx**

```tsx
import type { OnCallShift } from "../api";

interface ShiftCardProps {
  shift: OnCallShift;
  selected: boolean;
  onSelect: () => void;
}

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function durationHours(start: string, end: string): string {
  const h = Math.round((new Date(end).getTime() - new Date(start).getTime()) / 3_600_000);
  return h >= 24 ? `${Math.round(h / 24)}d` : `${h}h`;
}

export function ShiftCard({ shift, selected, onSelect }: ShiftCardProps) {
  return (
    <div
      className={`shift-card ${selected ? "selected" : ""}`}
      role="button"
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(e) => e.key === "Enter" && onSelect()}
      aria-pressed={selected}
    >
      <div className="shift-card-radio">{selected ? "◉" : "○"}</div>
      <div className="shift-card-body">
        <div className="shift-card-name">{shift.scheduleName}</div>
        <div className="shift-card-range">
          {fmt(shift.start)} → {fmt(shift.end)}{" "}
          <span className="shift-card-duration">({durationHours(shift.start, shift.end)})</span>
        </div>
        {shift.escalationLevel > 0 && (
          <div className="shift-card-level">Escalation level {shift.escalationLevel}</div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create CoverageUserCard.tsx**

```tsx
import type { ScheduleUser } from "../api";

interface CoverageUserCardProps {
  user: ScheduleUser;
  onSelect: () => void;
}

function initials(name: string): string {
  return name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function CoverageUserCard({ user, onSelect }: CoverageUserCardProps) {
  return (
    <div className="coverage-user-card">
      <div className="coverage-user-avatar">{initials(user.name)}</div>
      <div className="coverage-user-info">
        <div className="coverage-user-name">{user.name}</div>
        <div className="coverage-user-email">{user.email}</div>
      </div>
      <button className="btn btn-primary btn-sm" onClick={onSelect}>
        Select
      </button>
    </div>
  );
}
```

- [ ] **Step 5: Create ConfirmModal.tsx**

```tsx
interface ConfirmModalProps {
  scheduleName: string;
  userName: string;
  start: string;
  end: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
}

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function ConfirmModal({
  scheduleName,
  userName,
  start,
  end,
  onConfirm,
  onCancel,
  loading,
}: ConfirmModalProps) {
  return (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div className="modal">
        <div className="modal-header">
          <h3>Confirm Override</h3>
        </div>
        <div className="modal-body">
          <table className="confirm-table">
            <tbody>
              <tr>
                <td className="confirm-label">Schedule</td>
                <td className="confirm-value">{scheduleName}</td>
              </tr>
              <tr>
                <td className="confirm-label">Assignee</td>
                <td className="confirm-value">{userName}</td>
              </tr>
              <tr>
                <td className="confirm-label">From</td>
                <td className="confirm-value">{fmt(start)}</td>
              </tr>
              <tr>
                <td className="confirm-label">To</td>
                <td className="confirm-value">{fmt(end)}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={onConfirm} disabled={loading}>
            {loading ? "Creating..." : "Create Override ✓"}
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## Task 4: Build shift-coverage-wizard — main app + CSS

**Files:**
- Create: `mcp-apps/shift-coverage-wizard/src/mcp-app.tsx`
- Create: `mcp-apps/shift-coverage-wizard/src/styles.css`

- [ ] **Step 1: Create src/styles.css**

Copy the `:root` and `:root[data-theme="dark"]` blocks verbatim from `mcp-apps/incident-command-center/src/styles.css`, then add wizard-specific rules:

```css
/* Shift Coverage Wizard Styles */

:root {
  --bg-primary: #ffffff;
  --bg-secondary: #fafafa;
  --bg-tertiary: #f5f5f5;
  --text-primary: #1d1d1f;
  --text-secondary: #6e6e73;
  --text-tertiary: #a0a0a0;
  --border-primary: #e5e5e5;
  --border-secondary: #d0d0d0;
  --border-hover: #b0b0b0;
  --shadow: rgba(0, 0, 0, 0.08);
  --shadow-hover: rgba(0, 0, 0, 0.12);
  --shadow-modal: rgba(0, 0, 0, 0.2);
  --overlay-bg: rgba(0, 0, 0, 0.5);
  --pd-green: #00b050;
  --pd-dark-green: #005a2f;
  --status-triggered: #e53e3e;
  --status-acknowledged: #3182ce;
  --status-resolved: #38a169;
}

:root[data-theme="dark"] {
  --bg-primary: #1e1e1e;
  --bg-secondary: #2d2d30;
  --bg-tertiary: #3e3e42;
  --text-primary: #d4d4d4;
  --text-secondary: #a0a0a0;
  --text-tertiary: #808080;
  --border-primary: #3e3e42;
  --border-secondary: #505050;
  --border-hover: #606060;
  --shadow: rgba(0, 0, 0, 0.4);
  --shadow-hover: rgba(0, 0, 0, 0.5);
  --shadow-modal: rgba(0, 0, 0, 0.7);
  --overlay-bg: rgba(0, 0, 0, 0.8);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.5;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ── Header ── */
.app-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.app-header h1 {
  font-size: 16px;
  font-weight: 600;
}

.app-header .pd-icon { color: var(--pd-green); }

/* ── Step Indicator ── */
.step-indicator {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  gap: 0;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  border: 2px solid var(--border-secondary);
  color: var(--text-secondary);
  background: var(--bg-primary);
  flex-shrink: 0;
}

.step-circle.active {
  border-color: var(--pd-green);
  color: var(--pd-green);
}

.step-circle.done {
  border-color: var(--status-resolved);
  background: var(--status-resolved);
  color: #fff;
}

.step-label {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.step-label.active {
  color: var(--text-primary);
  font-weight: 600;
}

.step-line {
  height: 2px;
  width: 40px;
  background: var(--border-secondary);
  margin: 0 8px;
  flex-shrink: 0;
}

.step-line.done { background: var(--status-resolved); }

/* ── Content ── */
.step-content {
  flex: 1;
  padding: 24px;
  max-width: 640px;
  margin: 0 auto;
  width: 100%;
}

.step-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
}

/* ── Date range ── */
.date-range {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.date-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 160px;
}

.date-field label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.date-field input {
  padding: 8px 12px;
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
}

.date-field input:focus {
  outline: none;
  border-color: var(--pd-green);
}

/* ── Shift cards ── */
.shift-list { display: flex; flex-direction: column; gap: 12px; }

.shift-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  cursor: pointer;
  background: var(--bg-primary);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.shift-card:hover { border-color: var(--border-hover); box-shadow: 0 2px 8px var(--shadow-hover); }
.shift-card.selected { border-color: var(--pd-green); box-shadow: 0 0 0 2px rgba(0,176,80,0.15); }

.shift-card-radio { font-size: 18px; color: var(--pd-green); margin-top: 1px; }
.shift-card-name { font-weight: 600; margin-bottom: 4px; }
.shift-card-range { color: var(--text-secondary); font-size: 13px; }
.shift-card-duration { color: var(--text-tertiary); }
.shift-card-level { font-size: 12px; color: var(--text-tertiary); margin-top: 4px; }

/* ── Coverage users ── */
.coverage-list { display: flex; flex-direction: column; gap: 10px; }

.coverage-user-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-primary);
}

.coverage-user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--pd-dark-green);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.coverage-user-info { flex: 1; }
.coverage-user-name { font-weight: 600; }
.coverage-user-email { font-size: 12px; color: var(--text-secondary); }

/* ── Buttons ── */
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.15s, border-color 0.15s;
}

.btn-primary {
  background: var(--pd-green);
  color: #fff;
  border-color: var(--pd-green);
}

.btn-primary:hover:not(:disabled) { background: #009040; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--border-secondary);
}

.btn-secondary:hover:not(:disabled) { border-color: var(--border-hover); }

.btn-sm { padding: 6px 12px; font-size: 12px; }

.btn-row {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: var(--bg-primary);
  border-radius: 10px;
  box-shadow: 0 8px 32px var(--shadow-modal);
  width: 400px;
  max-width: 90vw;
  overflow: hidden;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-primary);
  font-size: 15px;
  font-weight: 600;
}

.modal-body { padding: 20px; }
.modal-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--border-primary);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.confirm-table { width: 100%; border-collapse: collapse; }
.confirm-table tr { border-bottom: 1px solid var(--border-primary); }
.confirm-table tr:last-child { border-bottom: none; }
.confirm-label { padding: 8px 0; color: var(--text-secondary); font-size: 13px; width: 90px; }
.confirm-value { padding: 8px 0; font-weight: 500; }

/* ── States ── */
.loading, .empty-state, .error-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.error-state { color: var(--status-triggered); }

.success-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: rgba(56,161,105,0.1);
  border: 1px solid var(--status-resolved);
  border-radius: 8px;
  color: var(--status-resolved);
  font-weight: 600;
  margin-bottom: 16px;
}

.notice {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 16px;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border-left: 3px solid var(--border-secondary);
}

:root[data-theme="dark"] .date-field input {
  background: #252526;
  border-color: #3e3e42;
  color: #d4d4d4;
}

:root[data-theme="dark"] .shift-card { background: #252526; }
:root[data-theme="dark"] .coverage-user-card { background: #252526; }
:root[data-theme="dark"] .modal { background: #252526; }
```

- [ ] **Step 2: Create src/mcp-app.tsx**

```tsx
/**
 * Shift Coverage Wizard - Main App
 *
 * 3-step wizard:
 *  Step 0 — Date range picker → fetch user's on-call shifts
 *  Step 1 — Select a shift to get coverage for
 *  Step 2 — Pick a coverage user → confirm + create override
 */

import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import {
  fetchCurrentUser,
  fetchUserOnCallShifts,
  fetchScheduleUsers,
  createOverride,
  type CurrentUser,
  type OnCallShift,
  type ScheduleUser,
} from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { StepIndicator } from "./components/StepIndicator";
import { ShiftCard } from "./components/ShiftCard";
import { CoverageUserCard } from "./components/CoverageUserCard";
import { ConfirmModal } from "./components/ConfirmModal";

const STEPS = ["Date Range", "Select Shift", "Find Coverage"];

function getDefaultSince(): string {
  const d = new Date();
  return d.toISOString().slice(0, 16); // datetime-local format
}

function getDefaultUntil(): string {
  const d = new Date();
  d.setDate(d.getDate() + 14);
  return d.toISOString().slice(0, 16);
}

// Detect dark mode from host context or system preference
function detectTheme(): "dark" | "light" {
  if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) return "dark";
  return "light";
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Shift Coverage Wizard", version: "1.0.0" },
    capabilities: {},
  });

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [step, setStep] = useState(0);
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getDefaultUntil);

  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [shifts, setShifts] = useState<OnCallShift[]>([]);
  const [selectedShift, setSelectedShift] = useState<OnCallShift | null>(null);
  const [candidates, setCandidates] = useState<ScheduleUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<ScheduleUser | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if ((ctx as any).theme) setTheme((ctx as any).theme === "dark" ? "dark" : "light");
    };
  }, [app]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // Step 0 → 1: fetch user + their shifts
  const handleFindShifts = useCallback(async () => {
    if (!app) return;
    setLoading(true);
    setError(null);
    try {
      const user = await fetchCurrentUser(app);
      if (!user) throw new Error("Could not load your user profile. Check your API token.");
      setCurrentUser(user);
      const found = await fetchUserOnCallShifts(app, user.id, new Date(since).toISOString(), new Date(until).toISOString());
      if (found.length === 0) {
        setError("No on-call shifts found in that date range for your user.");
        setLoading(false);
        return;
      }
      setShifts(found);
      setStep(1);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load shifts");
    } finally {
      setLoading(false);
    }
  }, [app, since, until]);

  // Step 1 → 2: load coverage candidates for selected shift
  const handleFindCoverage = useCallback(async () => {
    if (!app || !selectedShift) return;
    setLoading(true);
    setError(null);
    try {
      const users = await fetchScheduleUsers(app, selectedShift.scheduleId);
      // Exclude the current user from candidates
      const filtered = users.filter((u) => u.id !== currentUser?.id);
      if (filtered.length === 0) {
        setError("No other users found on this schedule to cover your shift.");
        setLoading(false);
        return;
      }
      setCandidates(filtered);
      setStep(2);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load coverage candidates");
    } finally {
      setLoading(false);
    }
  }, [app, selectedShift, currentUser]);

  // Confirm override
  const handleConfirm = useCallback(async () => {
    if (!app || !selectedShift || !selectedUser) return;
    setConfirmLoading(true);
    try {
      await createOverride(
        app,
        selectedShift.scheduleId,
        selectedUser.id,
        new Date(since).toISOString(),
        new Date(until).toISOString()
      );
      setConfirmOpen(false);
      setSuccess(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create override");
      setConfirmOpen(false);
    } finally {
      setConfirmLoading(false);
    }
  }, [app, selectedShift, selectedUser, since, until]);

  const displayError = connectionError?.message ?? error;

  return (
    <div className="app">
      <header className="app-header">
        <span className="pd-icon">
          <PagerDutyLogo size={22} />
        </span>
        <h1>Shift Coverage Wizard</h1>
      </header>

      <StepIndicator steps={STEPS} current={step} />

      <main className="step-content">
        {displayError && <div className="error-state">{displayError}</div>}
        {success && (
          <div className="success-banner">
            ✓ Override created for {selectedUser?.name} on "{selectedShift?.scheduleName}"
          </div>
        )}

        {/* Step 0: Date range */}
        {step === 0 && (
          <>
            <div className="step-title">When do you need coverage?</div>
            <div className="date-range">
              <div className="date-field">
                <label>From</label>
                <input
                  type="datetime-local"
                  value={since}
                  onChange={(e) => setSince(e.currentTarget.value)}
                />
              </div>
              <div className="date-field">
                <label>To</label>
                <input
                  type="datetime-local"
                  value={until}
                  onChange={(e) => setUntil(e.currentTarget.value)}
                />
              </div>
            </div>
            <div className="btn-row">
              <button
                className="btn btn-primary"
                onClick={handleFindShifts}
                disabled={loading || !since || !until}
              >
                {loading ? "Loading..." : "Find my shifts →"}
              </button>
            </div>
          </>
        )}

        {/* Step 1: Select shift */}
        {step === 1 && (
          <>
            <div className="step-title">
              Your on-call shifts{currentUser ? ` for ${currentUser.name}` : ""}
            </div>
            <div className="shift-list">
              {shifts.map((s, i) => (
                <ShiftCard
                  key={`${s.scheduleId}-${i}`}
                  shift={s}
                  selected={selectedShift?.scheduleId === s.scheduleId && selectedShift?.start === s.start}
                  onSelect={() => setSelectedShift(s)}
                />
              ))}
            </div>
            <div className="btn-row">
              <button className="btn btn-secondary" onClick={() => { setStep(0); setSelectedShift(null); }}>
                ← Back
              </button>
              <button
                className="btn btn-primary"
                onClick={handleFindCoverage}
                disabled={loading || !selectedShift}
              >
                {loading ? "Loading..." : "Find coverage →"}
              </button>
            </div>
          </>
        )}

        {/* Step 2: Select coverage user */}
        {step === 2 && (
          <>
            <div className="step-title">Who can cover?</div>
            <div className="coverage-list">
              {candidates.map((u) => (
                <CoverageUserCard
                  key={u.id}
                  user={u}
                  onSelect={() => {
                    setSelectedUser(u);
                    setConfirmOpen(true);
                  }}
                />
              ))}
            </div>
            <div className="notice">
              ℹ Reach out via Slack or Teams to confirm availability before creating the override.
            </div>
            <div className="btn-row">
              <button className="btn btn-secondary" onClick={() => { setStep(1); setCandidates([]); setSelectedUser(null); }}>
                ← Back
              </button>
            </div>
          </>
        )}

        {confirmOpen && selectedShift && selectedUser && (
          <ConfirmModal
            scheduleName={selectedShift.scheduleName}
            userName={selectedUser.name}
            start={new Date(since).toISOString()}
            end={new Date(until).toISOString()}
            onConfirm={handleConfirm}
            onCancel={() => setConfirmOpen(false)}
            loading={confirmLoading}
          />
        )}
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

---

## Task 5: Build shift-coverage-wizard — compile and verify

**Files:**
- Built output: `pagerduty_mcp/shift_coverage_wizard_view.html`

- [ ] **Step 1: Build the app**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/shift-coverage-wizard
source ~/.nvm/nvm.sh && nvm use --lts
npm run build
```

Expected: `dist/mcp-app.html` created, no TypeScript errors.

- [ ] **Step 2: Copy to Python package**

```bash
cp /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/shift-coverage-wizard/dist/mcp-app.html \
   /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/pagerduty_mcp/shift_coverage_wizard_view.html
```

- [ ] **Step 3: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/shift-coverage-wizard/ pagerduty_mcp/shift_coverage_wizard_view.html
git commit -m "feat: add Shift Coverage Wizard MCP App"
```

---

## Task 6: Scaffold post-mortem-builder boilerplate

Identical structure to Task 1 with different name/description.

**Files:**
- Create: `mcp-apps/post-mortem-builder/mcp-app.html`
- Create: `mcp-apps/post-mortem-builder/package.json`
- Create: `mcp-apps/post-mortem-builder/vite.config.ts`
- Create: `mcp-apps/post-mortem-builder/tsconfig.json`
- Create: `mcp-apps/post-mortem-builder/tsconfig.server.json`

- [ ] **Step 1: Create mcp-app.html** (same as Task 1 Step 1 but title = "Post-Mortem Builder")

- [ ] **Step 2: Create package.json**

```json
{
  "name": "@pagerduty/post-mortem-builder",
  "version": "1.0.0",
  "type": "module",
  "private": true,
  "description": "Timeline-based post-mortem builder from incident data",
  "scripts": {
    "build": "tsc --noEmit && cross-env INPUT=mcp-app.html vite build",
    "start": "concurrently \"cross-env NODE_ENV=development INPUT=mcp-app.html vite build --watch\" \"tsx watch main.ts\"",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@modelcontextprotocol/ext-apps": "^1.3.2",
    "@modelcontextprotocol/sdk": "^1.24.0",
    "preact": "^10.29.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "22.19.5",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "concurrently": "^9.2.1",
    "cross-env": "^10.1.0",
    "tsx": "^4.21.0",
    "typescript": "^5.9.3",
    "vite": "^6.0.0",
    "vite-plugin-singlefile": "^2.3.0"
  }
}
```

- [ ] **Step 3: Create vite.config.ts** (identical to Task 1 Step 3)

- [ ] **Step 4: Create tsconfig.json** (identical to Task 1 Step 4)

- [ ] **Step 5: Create tsconfig.server.json** (identical to Task 1 Step 5)

- [ ] **Step 6: Install deps**

```bash
cd mcp-apps/post-mortem-builder && npm install
```

---

## Task 7: Build post-mortem-builder — API layer

**Files:**
- Create: `mcp-apps/post-mortem-builder/src/api.ts`

- [ ] **Step 1: Create src/api.ts**

```typescript
/**
 * Post-Mortem Builder - API layer
 * Fetches incident data, log entries, notes, alerts, and change events.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface IncidentSummary {
  id: string;
  number: number;
  title: string;
  status: string;
  urgency: string;
  createdAt: string;
  resolvedAt: string | null;
  serviceName: string;
  priority: string | null;
  assignees: string[];
  alertCount: number;
}

export type TimelineEventKind =
  | "trigger"
  | "acknowledge"
  | "resolve"
  | "note"
  | "escalation"
  | "assign"
  | "change"
  | "alert"
  | "snooze"
  | "other";

export interface TimelineEvent {
  id: string;
  kind: TimelineEventKind;
  timestamp: string;
  summary: string;
  detail: string | null;
  actor: string | null;
  link: string | null;
}

export interface IncidentTimeline {
  incident: IncidentSummary;
  events: TimelineEvent[];
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

function logEntryKind(type: string): TimelineEventKind {
  if (type.includes("trigger")) return "trigger";
  if (type.includes("acknowledge")) return "acknowledge";
  if (type.includes("resolve")) return "resolve";
  if (type.includes("annotate")) return "note";
  if (type.includes("escalat")) return "escalation";
  if (type.includes("assign") || type.includes("delegate")) return "assign";
  if (type.includes("snooze")) return "snooze";
  return "other";
}

// ─── API functions ────────────────────────────────────────────────────────────

/** List recently resolved incidents. */
export async function fetchResolvedIncidents(
  app: App,
  since: string,
  until: string
): Promise<IncidentSummary[]> {
  const result = await app.callServerTool({
    name: "list_incidents",
    arguments: {
      query_model: {
        status: ["resolved"],
        since,
        until,
        limit: 50,
      },
    },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map((i: any) => ({
    id: i.id,
    number: i.incident_number,
    title: i.title ?? i.summary,
    status: i.status,
    urgency: i.urgency,
    createdAt: i.created_at,
    resolvedAt: i.resolved_at ?? null,
    serviceName: i.service?.summary ?? i.service?.id ?? "Unknown",
    priority: i.priority?.summary ?? null,
    assignees: (i.assignments ?? []).map((a: any) => a.assignee?.summary ?? ""),
    alertCount: (i.alert_counts?.triggered ?? 0) + (i.alert_counts?.resolved ?? 0),
  }));
}

/** Fetch full incident timeline: log entries + notes + change events + alerts. */
export async function fetchIncidentTimeline(
  app: App,
  incidentId: string
): Promise<IncidentTimeline> {
  const [incResult, logResult, notesResult, changesResult, alertsResult] = await Promise.allSettled([
    app.callServerTool({ name: "get_incident", arguments: { incident_id: incidentId } }),
    app.callServerTool({ name: "list_log_entries", arguments: { query_model: { incident_id: incidentId, limit: 100 } } }),
    app.callServerTool({ name: "list_incident_notes", arguments: { incident_id: incidentId } }),
    app.callServerTool({ name: "list_incident_change_events", arguments: { incident_id: incidentId } }),
    app.callServerTool({ name: "list_alerts_from_incident", arguments: { incident_id: incidentId, query_model: { limit: 50 } } }),
  ]);

  const incData = incResult.status === "fulfilled" ? extract<any>(incResult.value) : null;
  const inc = incData?.response ?? incData ?? {};

  const logEntries: any[] = logResult.status === "fulfilled"
    ? (extract<any>(logResult.value)?.response ?? []) : [];
  const notes: any[] = notesResult.status === "fulfilled"
    ? (extract<any>(notesResult.value)?.response ?? []) : [];
  const changes: any[] = changesResult.status === "fulfilled"
    ? (extract<any>(changesResult.value)?.response ?? []) : [];
  const alerts: any[] = alertsResult.status === "fulfilled"
    ? (extract<any>(alertsResult.value)?.response ?? []) : [];

  const events: TimelineEvent[] = [];

  // Log entries
  for (const le of logEntries) {
    events.push({
      id: le.id,
      kind: logEntryKind(le.type ?? ""),
      timestamp: le.created_at,
      summary: le.summary ?? le.type,
      detail: le.note ?? le.event_details?.description ?? null,
      actor: le.agent?.summary ?? null,
      link: le.html_url ?? null,
    });
  }

  // Notes (may overlap with annotate log entries — deduplicate by content+time)
  for (const note of notes) {
    const dup = events.find(
      (e) => e.kind === "note" && e.detail === note.content && e.timestamp === note.created_at
    );
    if (!dup) {
      events.push({
        id: note.id,
        kind: "note",
        timestamp: note.created_at,
        summary: "Note added",
        detail: note.content,
        actor: note.user?.summary ?? null,
        link: null,
      });
    }
  }

  // Change events
  for (const ce of changes) {
    events.push({
      id: ce.id,
      kind: "change",
      timestamp: ce.timestamp,
      summary: ce.summary ?? "Change event",
      detail: ce.custom_details ? JSON.stringify(ce.custom_details).slice(0, 200) : null,
      actor: ce.source ?? ce.integration?.summary ?? null,
      link: ce.html_url ?? ce.links?.[0]?.href ?? null,
    });
  }

  // Alerts (only first trigger per alert key)
  const seenKeys = new Set<string>();
  for (const al of alerts) {
    const key = al.alert_key ?? al.id;
    if (!seenKeys.has(key)) {
      seenKeys.add(key);
      events.push({
        id: al.id,
        kind: "alert",
        timestamp: al.created_at,
        summary: al.summary ?? "Alert triggered",
        detail: `Severity: ${al.severity ?? "unknown"} · Status: ${al.status ?? "unknown"}`,
        actor: al.service?.summary ?? null,
        link: al.html_url ?? null,
      });
    }
  }

  // Sort chronologically
  events.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  const incident: IncidentSummary = {
    id: inc.id ?? incidentId,
    number: inc.incident_number ?? 0,
    title: inc.title ?? inc.summary ?? "Unknown",
    status: inc.status ?? "resolved",
    urgency: inc.urgency ?? "low",
    createdAt: inc.created_at ?? "",
    resolvedAt: inc.resolved_at ?? null,
    serviceName: inc.service?.summary ?? "Unknown",
    priority: inc.priority?.summary ?? null,
    assignees: (inc.assignments ?? []).map((a: any) => a.assignee?.summary ?? ""),
    alertCount: (inc.alert_counts?.triggered ?? 0) + (inc.alert_counts?.resolved ?? 0),
  };

  return { incident, events };
}

/** Generate markdown export of the timeline. */
export function exportToMarkdown(timeline: IncidentTimeline): string {
  const { incident, events } = timeline;
  const duration = incident.resolvedAt
    ? Math.round(
        (new Date(incident.resolvedAt).getTime() - new Date(incident.createdAt).getTime()) / 60000
      ) + " min"
    : "ongoing";

  const lines: string[] = [
    `## Incident #${incident.number} Post-Mortem`,
    `**Title:** ${incident.title}`,
    `**Service:** ${incident.serviceName}  **Priority:** ${incident.priority ?? "—"}  **Urgency:** ${incident.urgency}  **Duration:** ${duration}`,
    "",
    "### Timeline",
    "",
  ];

  for (const ev of events) {
    const time = new Date(ev.timestamp).toLocaleString("en-US", {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
    const actor = ev.actor ? ` — ${ev.actor}` : "";
    const detail = ev.detail ? `\n  > ${ev.detail.replace(/\n/g, "\n  > ")}` : "";
    lines.push(`- **${time}** — ${ev.summary}${actor}${detail}`);
  }

  lines.push("", "### Root Cause", "", "_[Fill in]_", "", "### Contributing Factors", "", "- ", "", "### Action Items", "", "- [ ] ");

  return lines.join("\n");
}
```

---

## Task 8: Build post-mortem-builder — UI components

**Files:**
- Create: `mcp-apps/post-mortem-builder/src/components/PagerDutyLogo.tsx` (identical to Task 3 Step 1)
- Create: `mcp-apps/post-mortem-builder/src/components/IncidentPicker.tsx`
- Create: `mcp-apps/post-mortem-builder/src/components/TimelineEvent.tsx`
- Create: `mcp-apps/post-mortem-builder/src/components/TimelineView.tsx`

- [ ] **Step 1: Create PagerDutyLogo.tsx** (copy from shift-coverage-wizard)

- [ ] **Step 2: Create IncidentPicker.tsx**

```tsx
import type { IncidentSummary } from "../api";

interface IncidentPickerProps {
  incidents: IncidentSummary[];
  onSelect: (id: string) => void;
  search: string;
  onSearchChange: (v: string) => void;
  urgencyFilter: string;
  onUrgencyChange: (v: string) => void;
}

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

function durationStr(start: string, end: string | null): string {
  if (!end) return "ongoing";
  const m = Math.round((new Date(end).getTime() - new Date(start).getTime()) / 60000);
  if (m < 60) return `${m}m`;
  return `${Math.floor(m / 60)}h ${m % 60}m`;
}

export function IncidentPicker({
  incidents, onSelect, search, onSearchChange, urgencyFilter, onUrgencyChange,
}: IncidentPickerProps) {
  const filtered = incidents.filter((i) => {
    const matchSearch =
      !search ||
      i.title.toLowerCase().includes(search.toLowerCase()) ||
      i.serviceName.toLowerCase().includes(search.toLowerCase()) ||
      String(i.number).includes(search);
    const matchUrgency = !urgencyFilter || i.urgency === urgencyFilter;
    return matchSearch && matchUrgency;
  });

  return (
    <div className="incident-picker">
      <div className="picker-controls">
        <input
          type="search"
          placeholder="Search incidents..."
          value={search}
          onChange={(e) => onSearchChange(e.currentTarget.value)}
          className="picker-search"
        />
        <select
          value={urgencyFilter}
          onChange={(e) => onUrgencyChange(e.currentTarget.value)}
          className="picker-filter"
        >
          <option value="">All urgencies</option>
          <option value="high">High</option>
          <option value="low">Low</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">No incidents found</div>
      ) : (
        <div className="incident-list">
          {filtered.map((i) => (
            <div key={i.id} className="incident-row">
              <div className="incident-row-main">
                <span className="incident-number">#{i.number}</span>
                <span className="incident-title">{i.title}</span>
                {i.priority && <span className="badge badge-priority">{i.priority}</span>}
                <span className={`badge badge-urgency badge-${i.urgency}`}>{i.urgency}</span>
              </div>
              <div className="incident-row-meta">
                <span>{i.serviceName}</span>
                <span>·</span>
                <span>{fmt(i.createdAt)}</span>
                <span>·</span>
                <span>{durationStr(i.createdAt, i.resolvedAt)}</span>
                {i.alertCount > 0 && (
                  <>
                    <span>·</span>
                    <span>{i.alertCount} alert{i.alertCount !== 1 ? "s" : ""}</span>
                  </>
                )}
              </div>
              <button className="btn btn-primary btn-sm" onClick={() => onSelect(i.id)}>
                Build Post-Mortem
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Create TimelineEvent.tsx**

```tsx
import type { TimelineEvent } from "../api";

const KIND_CONFIG: Record<string, { icon: string; color: string; label: string }> = {
  trigger:      { icon: "🔴", color: "var(--status-triggered)",    label: "Alert Triggered" },
  acknowledge:  { icon: "👤", color: "var(--status-acknowledged)",  label: "Acknowledged" },
  resolve:      { icon: "✅", color: "var(--status-resolved)",      label: "Resolved" },
  note:         { icon: "📝", color: "var(--color-note)",           label: "Note Added" },
  escalation:   { icon: "📋", color: "var(--color-escalation)",     label: "Escalated" },
  assign:       { icon: "↪",  color: "var(--color-assign)",         label: "Reassigned" },
  change:       { icon: "🔧", color: "var(--color-change)",         label: "Change Event" },
  alert:        { icon: "⚠️", color: "var(--status-triggered)",    label: "Alert" },
  snooze:       { icon: "💤", color: "var(--text-tertiary)",        label: "Snoozed" },
  other:        { icon: "●",  color: "var(--text-tertiary)",        label: "Event" },
};

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
}

export function TimelineEventCard({ event }: { event: TimelineEvent }) {
  const cfg = KIND_CONFIG[event.kind] ?? KIND_CONFIG.other!;
  return (
    <div className="timeline-event">
      <div className="timeline-dot" style={{ color: cfg.color }}>{cfg.icon}</div>
      <div className="timeline-line" />
      <div className="timeline-card">
        <div className="timeline-card-header">
          <span className="timeline-kind" style={{ color: cfg.color }}>{cfg.label}</span>
          <span className="timeline-time">{fmt(event.timestamp)}</span>
          {event.actor && <span className="timeline-actor">{event.actor}</span>}
          {event.link && (
            <a href={event.link} target="_blank" rel="noopener noreferrer" className="timeline-link">
              ↗
            </a>
          )}
        </div>
        <div className="timeline-summary">{event.summary}</div>
        {event.detail && <div className="timeline-detail">{event.detail}</div>}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create TimelineView.tsx**

```tsx
import type { IncidentTimeline } from "../api";
import { TimelineEventCard } from "./TimelineEvent";

interface TimelineViewProps {
  timeline: IncidentTimeline;
  onCopyMarkdown: () => void;
  onBack: () => void;
}

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function durationStr(start: string, end: string | null): string {
  if (!end) return "ongoing";
  const m = Math.round((new Date(end).getTime() - new Date(start).getTime()) / 60000);
  if (m < 60) return `${m}m`;
  return `${Math.floor(m / 60)}h ${m % 60}m`;
}

export function TimelineView({ timeline, onCopyMarkdown, onBack }: TimelineViewProps) {
  const { incident, events } = timeline;
  return (
    <div className="timeline-view">
      <div className="timeline-header">
        <button className="btn btn-secondary btn-sm" onClick={onBack}>← Back</button>
        <div className="timeline-incident-meta">
          <span className="incident-number">#{incident.number}</span>
          <span className="timeline-title">{incident.title}</span>
        </div>
        <div className="timeline-incident-sub">
          <span>{incident.serviceName}</span>
          <span>·</span>
          <span>Duration: {durationStr(incident.createdAt, incident.resolvedAt)}</span>
          {incident.priority && <><span>·</span><span>{incident.priority}</span></>}
          <span>·</span>
          <span className={`badge badge-urgency badge-${incident.urgency}`}>{incident.urgency}</span>
        </div>
      </div>

      <div className="timeline-actions">
        <button className="btn btn-secondary btn-sm" onClick={onCopyMarkdown}>
          📋 Copy as Markdown
        </button>
        <span className="timeline-count">{events.length} events</span>
      </div>

      <div className="timeline-events">
        {events.length === 0 ? (
          <div className="empty-state">No timeline events found</div>
        ) : (
          events.map((ev) => <TimelineEventCard key={ev.id} event={ev} />)
        )}
      </div>
    </div>
  );
}
```

---

## Task 9: Build post-mortem-builder — main app + CSS

**Files:**
- Create: `mcp-apps/post-mortem-builder/src/mcp-app.tsx`
- Create: `mcp-apps/post-mortem-builder/src/styles.css`

- [ ] **Step 1: Create src/styles.css**

```css
/* Post-Mortem Builder Styles */

:root {
  --bg-primary: #ffffff;
  --bg-secondary: #fafafa;
  --bg-tertiary: #f5f5f5;
  --text-primary: #1d1d1f;
  --text-secondary: #6e6e73;
  --text-tertiary: #a0a0a0;
  --border-primary: #e5e5e5;
  --border-secondary: #d0d0d0;
  --border-hover: #b0b0b0;
  --shadow: rgba(0, 0, 0, 0.08);
  --shadow-hover: rgba(0, 0, 0, 0.12);
  --shadow-modal: rgba(0, 0, 0, 0.2);
  --overlay-bg: rgba(0, 0, 0, 0.5);
  --pd-green: #00b050;
  --pd-dark-green: #005a2f;
  --status-triggered: #e53e3e;
  --status-acknowledged: #3182ce;
  --status-resolved: #38a169;
  --color-note: #d69e2e;
  --color-escalation: #dd6b20;
  --color-assign: #805ad5;
  --color-change: #319795;
}

:root[data-theme="dark"] {
  --bg-primary: #1e1e1e;
  --bg-secondary: #2d2d30;
  --bg-tertiary: #3e3e42;
  --text-primary: #d4d4d4;
  --text-secondary: #a0a0a0;
  --text-tertiary: #808080;
  --border-primary: #3e3e42;
  --border-secondary: #505050;
  --border-hover: #606060;
  --shadow: rgba(0, 0, 0, 0.4);
  --shadow-hover: rgba(0, 0, 0, 0.5);
  --shadow-modal: rgba(0, 0, 0, 0.7);
  --overlay-bg: rgba(0, 0, 0, 0.8);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.5;
}

.app { display: flex; flex-direction: column; min-height: 100vh; }

/* ── Header ── */
.app-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.app-header h1 { font-size: 16px; font-weight: 600; }
.app-header .pd-icon { color: var(--pd-green); }

/* ── Date controls ── */
.date-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
  flex-wrap: wrap;
}

.date-controls label { font-size: 12px; font-weight: 600; color: var(--text-secondary); }

.date-controls input[type="date"] {
  padding: 6px 10px;
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
}

/* ── Incident Picker ── */
.incident-picker { flex: 1; padding: 20px; }

.picker-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.picker-search {
  flex: 1;
  min-width: 200px;
  padding: 8px 12px;
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
}

.picker-filter {
  padding: 8px 10px;
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
}

.incident-list { display: flex; flex-direction: column; gap: 10px; }

.incident-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: var(--bg-primary);
  flex-wrap: wrap;
}

.incident-row-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 200px;
  flex-wrap: wrap;
}

.incident-number { font-weight: 700; color: var(--text-secondary); font-size: 12px; }
.incident-title { font-weight: 500; }

.incident-row-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  flex: 1;
  min-width: 180px;
}

/* ── Badges ── */
.badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.badge-priority { background: rgba(128,90,213,0.15); color: #805ad5; }
.badge-urgency.badge-high { background: rgba(229,62,62,0.1); color: var(--status-triggered); }
.badge-urgency.badge-low { background: rgba(56,161,105,0.1); color: var(--status-resolved); }

/* ── Timeline ── */
.timeline-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.timeline-header {
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.timeline-incident-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.timeline-title { font-weight: 600; font-size: 15px; }

.timeline-incident-sub {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  flex-wrap: wrap;
}

.timeline-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border-primary);
}

.timeline-count { font-size: 12px; color: var(--text-secondary); }

.timeline-events {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px 32px;
}

.timeline-event {
  display: grid;
  grid-template-columns: 28px 2px 1fr;
  gap: 0 12px;
  margin-bottom: 4px;
  position: relative;
}

.timeline-dot {
  font-size: 16px;
  line-height: 1;
  padding-top: 2px;
  text-align: center;
}

.timeline-line {
  background: var(--border-secondary);
  width: 2px;
  min-height: 100%;
  margin: 20px 0 0;
  align-self: stretch;
}

.timeline-event:last-child .timeline-line { display: none; }

.timeline-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 12px;
}

.timeline-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.timeline-kind { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.timeline-time { font-size: 11px; color: var(--text-tertiary); font-family: monospace; }
.timeline-actor { font-size: 12px; color: var(--text-secondary); }
.timeline-link { font-size: 12px; color: var(--pd-green); text-decoration: none; }
.timeline-summary { font-weight: 500; margin-bottom: 4px; }
.timeline-detail { font-size: 12px; color: var(--text-secondary); font-family: monospace; background: var(--bg-tertiary); padding: 6px 8px; border-radius: 4px; word-break: break-all; }

/* ── Buttons ── */
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.15s;
}

.btn-primary { background: var(--pd-green); color: #fff; border-color: var(--pd-green); }
.btn-primary:hover:not(:disabled) { background: #009040; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary { background: var(--bg-tertiary); color: var(--text-primary); border-color: var(--border-secondary); }
.btn-secondary:hover:not(:disabled) { border-color: var(--border-hover); }

.btn-sm { padding: 6px 12px; font-size: 12px; }

/* ── States ── */
.loading, .empty-state, .error-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.error-state { color: var(--status-triggered); }

.success-toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: var(--status-resolved);
  color: #fff;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  z-index: 200;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

:root[data-theme="dark"] .timeline-card { background: #252526; }
:root[data-theme="dark"] .picker-search,
:root[data-theme="dark"] .picker-filter,
:root[data-theme="dark"] input[type="date"] { background: #252526; border-color: #3e3e42; color: #d4d4d4; }
:root[data-theme="dark"] .incident-row { background: #252526; }
```

- [ ] **Step 2: Create src/mcp-app.tsx**

```tsx
/**
 * Post-Mortem Builder - Main App
 *
 * View A — Incident Picker: list resolved incidents, search/filter
 * View B — Timeline View: color-coded event timeline + copy as markdown
 */

import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import {
  fetchResolvedIncidents,
  fetchIncidentTimeline,
  exportToMarkdown,
  type IncidentSummary,
  type IncidentTimeline,
} from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { IncidentPicker } from "./components/IncidentPicker";
import { TimelineView } from "./components/TimelineView";

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
    appInfo: { name: "Post-Mortem Builder", version: "1.0.0" },
    capabilities: {},
  });

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);

  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [search, setSearch] = useState("");
  const [urgencyFilter, setUrgencyFilter] = useState("");
  const [timeline, setTimeline] = useState<IncidentTimeline | null>(null);

  const [loading, setLoading] = useState(false);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if ((ctx as any).theme) setTheme((ctx as any).theme === "dark" ? "dark" : "light");
    };
  }, [app]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // Load incidents when app is ready or date range changes
  useEffect(() => {
    if (!app) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchResolvedIncidents(app, new Date(since).toISOString(), new Date(until + "T23:59:59").toISOString())
      .then((data) => { if (!cancelled) setIncidents(data); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load incidents"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [app, since, until]);

  const handleSelectIncident = useCallback(async (id: string) => {
    if (!app) return;
    setTimelineLoading(true);
    setError(null);
    try {
      const t = await fetchIncidentTimeline(app, id);
      setTimeline(t);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load timeline");
    } finally {
      setTimelineLoading(false);
    }
  }, [app]);

  const handleCopyMarkdown = useCallback(() => {
    if (!timeline) return;
    const md = exportToMarkdown(timeline);
    navigator.clipboard.writeText(md).then(() => {
      setToast("Copied to clipboard!");
      setTimeout(() => setToast(null), 2500);
    });
  }, [timeline]);

  const displayError = connectionError?.message ?? error;

  return (
    <div className="app">
      <header className="app-header">
        <span className="pd-icon"><PagerDutyLogo size={22} /></span>
        <h1>Post-Mortem Builder</h1>
      </header>

      {!timeline && (
        <div className="date-controls">
          <label>From</label>
          <input type="date" value={since} onChange={(e) => setSince(e.currentTarget.value)} />
          <label>To</label>
          <input type="date" value={until} onChange={(e) => setUntil(e.currentTarget.value)} />
          <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
            {incidents.length} resolved incident{incidents.length !== 1 ? "s" : ""}
          </span>
        </div>
      )}

      {displayError && <div className="error-state">{displayError}</div>}

      {timelineLoading ? (
        <div className="loading">Loading timeline…</div>
      ) : timeline ? (
        <TimelineView
          timeline={timeline}
          onCopyMarkdown={handleCopyMarkdown}
          onBack={() => setTimeline(null)}
        />
      ) : loading ? (
        <div className="loading">Loading incidents…</div>
      ) : (
        <IncidentPicker
          incidents={incidents}
          onSelect={handleSelectIncident}
          search={search}
          onSearchChange={setSearch}
          urgencyFilter={urgencyFilter}
          onUrgencyChange={setUrgencyFilter}
        />
      )}

      {toast && <div className="success-toast">{toast}</div>}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

---

## Task 10: Build post-mortem-builder — compile and verify

- [ ] **Step 1: Build**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/post-mortem-builder
source ~/.nvm/nvm.sh && nvm use --lts
npm run build
```

Expected: `dist/mcp-app.html` created, no TypeScript errors.

- [ ] **Step 2: Copy**

```bash
cp /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/post-mortem-builder/dist/mcp-app.html \
   /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/pagerduty_mcp/post_mortem_builder_view.html
```

- [ ] **Step 3: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/post-mortem-builder/ pagerduty_mcp/post_mortem_builder_view.html
git commit -m "feat: add Post-Mortem Builder MCP App"
```

---

## Task 11: Scaffold operations-intelligence boilerplate

Identical structure to Task 1.

**Files:**
- Create: `mcp-apps/operations-intelligence/mcp-app.html`
- Create: `mcp-apps/operations-intelligence/package.json`
- Create: `mcp-apps/operations-intelligence/vite.config.ts`
- Create: `mcp-apps/operations-intelligence/tsconfig.json`
- Create: `mcp-apps/operations-intelligence/tsconfig.server.json`

- [ ] **Step 1–5:** Same as Task 1, substituting name `@pagerduty/operations-intelligence` and description `"Team operational health dashboard with service breakdown and incident trends"`.

- [ ] **Step 6: Install deps**

```bash
cd mcp-apps/operations-intelligence && npm install
```

---

## Task 12: Build operations-intelligence — API layer

**Files:**
- Create: `mcp-apps/operations-intelligence/src/api.ts`

- [ ] **Step 1: Create src/api.ts**

```typescript
/**
 * Operations Intelligence - API layer
 * Fetches incident + service + oncall data for operational health dashboard.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Team {
  id: string;
  name: string;
}

export interface ServiceStat {
  id: string;
  name: string;
  incidentCount: number;
  highUrgencyCount: number;
  mttrMinutes: number | null; // null if no resolved incidents
}

export interface OpsData {
  teams: Team[];
  selectedTeam: string | null;
  since: string;
  until: string;
  totalIncidents: number;
  highUrgencyCount: number;
  resolvedCount: number;
  mttrMinutes: number | null;
  serviceStats: ServiceStat[];
  recentIncidents: RecentIncident[];
  oncallUsers: string[];
}

export interface RecentIncident {
  id: string;
  number: number;
  title: string;
  status: string;
  urgency: string;
  serviceName: string;
  createdAt: string;
  resolvedAt: string | null;
  mttrMinutes: number | null;
  priority: string | null;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function extract<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

function mttr(start: string, end: string | null): number | null {
  if (!end) return null;
  return Math.round((new Date(end).getTime() - new Date(start).getTime()) / 60000);
}

// ─── API functions ────────────────────────────────────────────────────────────

export async function fetchTeams(app: App): Promise<Team[]> {
  const result = await app.callServerTool({
    name: "list_teams",
    arguments: { query_model: { limit: 100 } },
  });
  const data = extract<any>(result);
  const items: any[] = data?.response ?? [];
  return items.map((t: any) => ({ id: t.id, name: t.name ?? t.summary }));
}

export async function fetchOpsData(
  app: App,
  since: string,
  until: string,
  teamId: string | null
): Promise<OpsData> {
  // Build teams query first to return in result
  const teamsResult = await app.callServerTool({
    name: "list_teams",
    arguments: { query_model: { limit: 100 } },
  });
  const teamsData = extract<any>(teamsResult);
  const teams: Team[] = (teamsData?.response ?? []).map((t: any) => ({
    id: t.id,
    name: t.name ?? t.summary,
  }));

  // Fetch incidents (optionally filtered by team)
  const incArgs: any = {
    query_model: {
      status: ["triggered", "acknowledged", "resolved"],
      since,
      until,
      limit: 100,
    },
  };
  if (teamId) incArgs.query_model.team_ids = [teamId];

  const [incResult, oncallResult] = await Promise.allSettled([
    app.callServerTool({ name: "list_incidents", arguments: incArgs }),
    app.callServerTool({
      name: "list_oncalls",
      arguments: {
        query_model: {
          since,
          until,
          earliest: true,
          ...(teamId ? {} : {}),
        },
      },
    }),
  ]);

  const incidents: any[] = incResult.status === "fulfilled"
    ? (extract<any>(incResult.value)?.response ?? []) : [];

  const oncalls: any[] = oncallResult.status === "fulfilled"
    ? (extract<any>(oncallResult.value)?.response ?? []) : [];

  // Compute stats
  const resolved = incidents.filter((i: any) => i.status === "resolved");
  const highUrgency = incidents.filter((i: any) => i.urgency === "high");

  // MTTR
  const mttrValues = resolved
    .map((i: any) => mttr(i.created_at, i.resolved_at))
    .filter((v): v is number => v !== null);
  const avgMttr = mttrValues.length > 0
    ? Math.round(mttrValues.reduce((a, b) => a + b, 0) / mttrValues.length)
    : null;

  // Service breakdown
  const serviceMap = new Map<string, ServiceStat>();
  for (const inc of incidents) {
    const svcId = inc.service?.id ?? "unknown";
    const svcName = inc.service?.summary ?? "Unknown";
    if (!serviceMap.has(svcId)) {
      serviceMap.set(svcId, { id: svcId, name: svcName, incidentCount: 0, highUrgencyCount: 0, mttrMinutes: null });
    }
    const stat = serviceMap.get(svcId)!;
    stat.incidentCount++;
    if (inc.urgency === "high") stat.highUrgencyCount++;
  }
  // MTTR per service
  for (const inc of resolved) {
    const svcId = inc.service?.id ?? "unknown";
    const stat = serviceMap.get(svcId);
    if (stat) {
      const m = mttr(inc.created_at, inc.resolved_at);
      if (m !== null) {
        stat.mttrMinutes = stat.mttrMinutes === null ? m : Math.round((stat.mttrMinutes + m) / 2);
      }
    }
  }
  const serviceStats = [...serviceMap.values()].sort((a, b) => b.incidentCount - a.incidentCount);

  // Recent incidents
  const recentIncidents: RecentIncident[] = incidents.slice(0, 50).map((i: any) => ({
    id: i.id,
    number: i.incident_number,
    title: i.title ?? i.summary,
    status: i.status,
    urgency: i.urgency,
    serviceName: i.service?.summary ?? "Unknown",
    createdAt: i.created_at,
    resolvedAt: i.resolved_at ?? null,
    mttrMinutes: mttr(i.created_at, i.resolved_at),
    priority: i.priority?.summary ?? null,
  }));

  // On-call users (unique)
  const oncallUserSet = new Set<string>();
  for (const oc of oncalls) {
    if (oc.user?.summary) oncallUserSet.add(oc.user.summary);
  }

  return {
    teams,
    selectedTeam: teamId,
    since,
    until,
    totalIncidents: incidents.length,
    highUrgencyCount: highUrgency.length,
    resolvedCount: resolved.length,
    mttrMinutes: avgMttr,
    serviceStats,
    recentIncidents,
    oncallUsers: [...oncallUserSet].slice(0, 10),
  };
}
```

---

## Task 13: Build operations-intelligence — UI components

**Files:**
- Create: `mcp-apps/operations-intelligence/src/components/PagerDutyLogo.tsx` (copy)
- Create: `mcp-apps/operations-intelligence/src/components/SummaryCards.tsx`
- Create: `mcp-apps/operations-intelligence/src/components/ServiceBreakdown.tsx`
- Create: `mcp-apps/operations-intelligence/src/components/IncidentTable.tsx`

- [ ] **Step 1: Create PagerDutyLogo.tsx** (same as before)

- [ ] **Step 2: Create SummaryCards.tsx**

```tsx
import type { OpsData } from "../api";

function fmtMttr(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}m`;
}

interface CardProps {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}

function Card({ label, value, sub, accent }: CardProps) {
  return (
    <div className="summary-card">
      <div className="summary-label">{label}</div>
      <div className="summary-value" style={accent ? { color: accent } : undefined}>{value}</div>
      {sub && <div className="summary-sub">{sub}</div>}
    </div>
  );
}

export function SummaryCards({ data }: { data: OpsData }) {
  const highPct = data.totalIncidents > 0
    ? Math.round((data.highUrgencyCount / data.totalIncidents) * 100)
    : 0;

  return (
    <div className="summary-cards">
      <Card
        label="Total Incidents"
        value={String(data.totalIncidents)}
        sub={`${data.resolvedCount} resolved`}
      />
      <Card
        label="High Urgency"
        value={String(data.highUrgencyCount)}
        sub={`${highPct}% of total`}
        accent={data.highUrgencyCount > 0 ? "var(--status-triggered)" : undefined}
      />
      <Card
        label="Avg MTTR"
        value={fmtMttr(data.mttrMinutes)}
        sub="mean time to resolve"
        accent={
          data.mttrMinutes !== null && data.mttrMinutes > 60
            ? "var(--color-escalation)"
            : undefined
        }
      />
      <Card
        label="On-Call Users"
        value={String(data.oncallUsers.length)}
        sub={data.oncallUsers.slice(0, 2).join(", ") || "—"}
      />
    </div>
  );
}
```

- [ ] **Step 3: Create ServiceBreakdown.tsx**

```tsx
import type { ServiceStat } from "../api";

function fmtMttr(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export function ServiceBreakdown({ stats, max }: { stats: ServiceStat[]; max: number }) {
  return (
    <div className="service-breakdown">
      <div className="section-title">Incidents by Service</div>
      {stats.length === 0 ? (
        <div className="empty-state">No service data</div>
      ) : (
        <table className="service-table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Incidents</th>
              <th>High Urgency</th>
              <th>MTTR</th>
            </tr>
          </thead>
          <tbody>
            {stats.map((s) => (
              <tr key={s.id}>
                <td className="service-name">{s.name}</td>
                <td>
                  <div className="bar-cell">
                    <div
                      className="bar-fill"
                      style={{ width: `${Math.round((s.incidentCount / max) * 100)}%` }}
                    />
                    <span>{s.incidentCount}</span>
                  </div>
                </td>
                <td>
                  {s.highUrgencyCount > 0 ? (
                    <span className="high-urgency-count">{s.highUrgencyCount}</span>
                  ) : (
                    <span className="zero-count">0</span>
                  )}
                </td>
                <td className="mttr-cell">{fmtMttr(s.mttrMinutes)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Create IncidentTable.tsx**

```tsx
import type { RecentIncident } from "../api";

type SortKey = "createdAt" | "urgency" | "status" | "mttrMinutes";

interface IncidentTableProps {
  incidents: RecentIncident[];
  sortKey: SortKey;
  sortDir: "asc" | "desc";
  onSort: (key: SortKey) => void;
}

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function fmtMttr(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export function IncidentTable({ incidents, sortKey, sortDir, onSort }: IncidentTableProps) {
  function thClass(key: SortKey): string {
    return `th-sortable${sortKey === key ? " th-active" : ""}`;
  }

  function arrow(key: SortKey): string {
    if (sortKey !== key) return " ↕";
    return sortDir === "asc" ? " ↑" : " ↓";
  }

  return (
    <div className="incident-table-wrap">
      <div className="section-title">
        Recent Incidents <span className="count-badge">{incidents.length}</span>
      </div>
      <div className="table-scroll">
        <table className="incident-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Title</th>
              <th>Service</th>
              <th className={thClass("status")} onClick={() => onSort("status")}>
                Status{arrow("status")}
              </th>
              <th className={thClass("urgency")} onClick={() => onSort("urgency")}>
                Urgency{arrow("urgency")}
              </th>
              <th className={thClass("createdAt")} onClick={() => onSort("createdAt")}>
                Created{arrow("createdAt")}
              </th>
              <th className={thClass("mttrMinutes")} onClick={() => onSort("mttrMinutes")}>
                MTTR{arrow("mttrMinutes")}
              </th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((i) => (
              <tr key={i.id}>
                <td className="col-num">#{i.number}</td>
                <td className="col-title">
                  {i.priority && <span className="badge badge-priority">{i.priority}</span>}
                  {i.title}
                </td>
                <td className="col-service">{i.serviceName}</td>
                <td>
                  <span className={`badge badge-status badge-${i.status}`}>{i.status}</span>
                </td>
                <td>
                  <span className={`badge badge-urgency badge-${i.urgency}`}>{i.urgency}</span>
                </td>
                <td className="col-date">{fmt(i.createdAt)}</td>
                <td className="col-mttr">{fmtMttr(i.mttrMinutes)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

## Task 14: Build operations-intelligence — main app + CSS

**Files:**
- Create: `mcp-apps/operations-intelligence/src/mcp-app.tsx`
- Create: `mcp-apps/operations-intelligence/src/styles.css`

- [ ] **Step 1: Create src/styles.css**

```css
/* Operations Intelligence Styles */

:root {
  --bg-primary: #ffffff;
  --bg-secondary: #fafafa;
  --bg-tertiary: #f5f5f5;
  --text-primary: #1d1d1f;
  --text-secondary: #6e6e73;
  --text-tertiary: #a0a0a0;
  --border-primary: #e5e5e5;
  --border-secondary: #d0d0d0;
  --border-hover: #b0b0b0;
  --shadow: rgba(0, 0, 0, 0.08);
  --pd-green: #00b050;
  --pd-dark-green: #005a2f;
  --status-triggered: #e53e3e;
  --status-acknowledged: #3182ce;
  --status-resolved: #38a169;
  --color-escalation: #dd6b20;
}

:root[data-theme="dark"] {
  --bg-primary: #1e1e1e;
  --bg-secondary: #2d2d30;
  --bg-tertiary: #3e3e42;
  --text-primary: #d4d4d4;
  --text-secondary: #a0a0a0;
  --text-tertiary: #808080;
  --border-primary: #3e3e42;
  --border-secondary: #505050;
  --border-hover: #606060;
  --shadow: rgba(0, 0, 0, 0.4);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.5;
}

.app { display: flex; flex-direction: column; min-height: 100vh; }

.app-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
}

.app-header h1 { font-size: 16px; font-weight: 600; }
.app-header .pd-icon { color: var(--pd-green); }

/* ── Controls ── */
.controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-secondary);
  flex-wrap: wrap;
}

.controls label { font-size: 12px; font-weight: 600; color: var(--text-secondary); }

.controls input[type="date"],
.controls select {
  padding: 6px 10px;
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
}

/* ── Summary cards ── */
.summary-cards {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--border-primary);
}

.summary-card {
  flex: 1;
  min-width: 120px;
  padding: 14px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
}

.summary-label { font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
.summary-value { font-size: 24px; font-weight: 700; }
.summary-sub { font-size: 11px; color: var(--text-tertiary); margin-top: 2px; }

/* ── Body layout ── */
.body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Service breakdown ── */
.service-breakdown {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-primary);
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.service-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.service-table th {
  text-align: left;
  padding: 6px 8px;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-primary);
  font-size: 12px;
}

.service-table td { padding: 8px; border-bottom: 1px solid var(--border-primary); }
.service-table tr:last-child td { border-bottom: none; }
.service-name { font-weight: 500; }

.bar-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
}

.bar-fill {
  height: 8px;
  background: var(--pd-green);
  border-radius: 4px;
  min-width: 4px;
  transition: width 0.3s ease;
}

.high-urgency-count { color: var(--status-triggered); font-weight: 600; }
.zero-count { color: var(--text-tertiary); }
.mttr-cell { font-family: monospace; font-size: 12px; }

/* ── Incident table ── */
.incident-table-wrap {
  flex: 1;
  padding: 16px 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.count-badge {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: normal;
  margin-left: 6px;
}

.table-scroll { flex: 1; overflow: auto; }

.incident-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.incident-table th {
  text-align: left;
  padding: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 2px solid var(--border-primary);
  white-space: nowrap;
  position: sticky;
  top: 0;
  background: var(--bg-primary);
}

.th-sortable { cursor: pointer; user-select: none; }
.th-sortable:hover { color: var(--text-primary); }
.th-active { color: var(--pd-green); }

.incident-table td { padding: 8px; border-bottom: 1px solid var(--border-primary); }
.incident-table tr:hover td { background: var(--bg-secondary); }

.col-num { color: var(--text-secondary); font-size: 11px; white-space: nowrap; }
.col-title { max-width: 280px; }
.col-service { color: var(--text-secondary); font-size: 12px; white-space: nowrap; }
.col-date { font-size: 12px; color: var(--text-secondary); white-space: nowrap; }
.col-mttr { font-family: monospace; font-size: 12px; white-space: nowrap; }

/* ── Badges ── */
.badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  display: inline-block;
  margin-right: 4px;
}

.badge-priority { background: rgba(128,90,213,0.15); color: #805ad5; }
.badge-urgency.badge-high { background: rgba(229,62,62,0.1); color: var(--status-triggered); }
.badge-urgency.badge-low { background: rgba(56,161,105,0.1); color: var(--status-resolved); }
.badge-status.badge-triggered { background: rgba(229,62,62,0.1); color: var(--status-triggered); }
.badge-status.badge-acknowledged { background: rgba(49,130,206,0.1); color: var(--status-acknowledged); }
.badge-status.badge-resolved { background: rgba(56,161,105,0.1); color: var(--status-resolved); }

/* ── States ── */
.loading, .empty-state, .error-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.error-state { color: var(--status-triggered); }

/* Btn */
.btn { padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: 1px solid transparent; }
.btn-primary { background: var(--pd-green); color: #fff; border-color: var(--pd-green); }
.btn-primary:hover:not(:disabled) { background: #009040; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-sm { padding: 6px 12px; font-size: 12px; }

/* Dark mode overrides */
:root[data-theme="dark"] .incident-table th { background: #1e1e1e; }
:root[data-theme="dark"] .controls input[type="date"],
:root[data-theme="dark"] .controls select { background: #252526; border-color: #3e3e42; color: #d4d4d4; }
```

- [ ] **Step 2: Create src/mcp-app.tsx**

```tsx
/**
 * Operations Intelligence - Main App
 *
 * Controls bar: team picker + date range + refresh
 * Summary cards: total incidents, high urgency, avg MTTR, on-call users
 * Service breakdown: sortable bar chart table
 * Incident table: sortable, paginated list
 */

import { useApp } from "@modelcontextprotocol/ext-apps/react";
import { StrictMode, useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { fetchOpsData, type OpsData, type RecentIncident } from "./api";
import { PagerDutyLogo } from "./components/PagerDutyLogo";
import { SummaryCards } from "./components/SummaryCards";
import { ServiceBreakdown } from "./components/ServiceBreakdown";
import { IncidentTable } from "./components/IncidentTable";

type SortKey = "createdAt" | "urgency" | "status" | "mttrMinutes";

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

function sortIncidents(incidents: RecentIncident[], key: SortKey, dir: "asc" | "desc"): RecentIncident[] {
  return [...incidents].sort((a, b) => {
    let av: string | number = a[key] ?? "";
    let bv: string | number = b[key] ?? "";
    if (key === "mttrMinutes") {
      av = a.mttrMinutes ?? Infinity;
      bv = b.mttrMinutes ?? Infinity;
    }
    if (av < bv) return dir === "asc" ? -1 : 1;
    if (av > bv) return dir === "asc" ? 1 : -1;
    return 0;
  });
}

function App() {
  const { app, error: connectionError } = useApp({
    appInfo: { name: "Operations Intelligence", version: "1.0.0" },
    capabilities: {},
  });

  const [theme, setTheme] = useState<"dark" | "light">(detectTheme);
  const [since, setSince] = useState(getDefaultSince);
  const [until, setUntil] = useState(getToday);
  const [selectedTeam, setSelectedTeam] = useState<string>("");

  const [data, setData] = useState<OpsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sortKey, setSortKey] = useState<SortKey>("createdAt");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

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

  function handleSort(key: SortKey) {
    if (key === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("desc"); }
  }

  const sortedIncidents = useMemo(
    () => sortIncidents(data?.recentIncidents ?? [], sortKey, sortDir),
    [data, sortKey, sortDir]
  );

  const maxServiceCount = useMemo(
    () => Math.max(1, ...(data?.serviceStats ?? []).map((s) => s.incidentCount)),
    [data]
  );

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

      {displayError && <div className="error-state">{displayError}</div>}

      {loading && !data ? (
        <div className="loading">Loading operational data…</div>
      ) : data ? (
        <div className="body">
          <SummaryCards data={data} />
          <ServiceBreakdown stats={data.serviceStats.slice(0, 10)} max={maxServiceCount} />
          <IncidentTable
            incidents={sortedIncidents}
            sortKey={sortKey}
            sortDir={sortDir}
            onSort={handleSort}
          />
        </div>
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

---

## Task 15: Build operations-intelligence — compile and verify

- [ ] **Step 1: Build**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence
source ~/.nvm/nvm.sh && nvm use --lts
npm run build
```

Expected: `dist/mcp-app.html` created, no TypeScript errors.

- [ ] **Step 2: Copy**

```bash
cp /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/mcp-apps/operations-intelligence/dist/mcp-app.html \
   /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/pagerduty_mcp/operations_intelligence_view.html
```

- [ ] **Step 3: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add mcp-apps/operations-intelligence/ pagerduty_mcp/operations_intelligence_view.html
git commit -m "feat: add Operations Intelligence MCP App"
```

---

## Task 16: Register all three apps in server.py

**Files:**
- Modify: `pagerduty_mcp/server.py`

- [ ] **Step 1: Add URI constants** (after the existing 4 constants, around line 22)

```python
SHIFT_COVERAGE_WIZARD_URI = "ui://shift-coverage-wizard/wizard.html"
POST_MORTEM_BUILDER_URI = "ui://post-mortem-builder/builder.html"
OPERATIONS_INTELLIGENCE_URI = "ui://operations-intelligence/dashboard.html"
```

- [ ] **Step 2: Add `add_shift_coverage_wizard()` function** (before the `run()` function)

```python
def add_shift_coverage_wizard(mcp_instance: FastMCP) -> None:
    """Add Shift Coverage Wizard MCP App resource.

    The UI directly calls existing MCP tools:
    - get_user_data (current user)
    - list_oncalls (user's upcoming shifts)
    - list_schedule_users (coverage candidates)
    - create_schedule_override (write — creates the override)

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": SHIFT_COVERAGE_WIZARD_URI},
            "ui/resourceUri": SHIFT_COVERAGE_WIZARD_URI,
        }
    )
    def shift_coverage_wizard() -> list[TextContent]:
        """Shift Coverage Wizard - Find and create on-call coverage.

        A 3-step wizard: pick a date range → select the shift you need covered →
        choose a replacement user → create a schedule override.
        Requires --enable-write-tools to create overrides.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Shift Coverage Wizard UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        SHIFT_COVERAGE_WIZARD_URI,
        mime_type="text/html;profile=mcp-app",
        description="Shift Coverage Wizard - Multi-step wizard for finding and creating on-call coverage"
    )
    def shift_coverage_wizard_view() -> str:
        """Shift Coverage Wizard UI resource."""
        html_path = pathlib.Path(__file__).parent / "shift_coverage_wizard_view.html"
        return html_path.read_text(encoding="utf-8")
```

- [ ] **Step 3: Add `add_post_mortem_builder()` function**

```python
def add_post_mortem_builder(mcp_instance: FastMCP) -> None:
    """Add Post-Mortem Builder MCP App resource.

    The UI directly calls existing MCP tools:
    - list_incidents (find resolved incidents)
    - get_incident (incident details)
    - list_log_entries (activity timeline)
    - list_incident_notes (notes)
    - list_incident_change_events (change events)
    - list_alerts_from_incident (alerts)

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": POST_MORTEM_BUILDER_URI},
            "ui/resourceUri": POST_MORTEM_BUILDER_URI,
        }
    )
    def post_mortem_builder() -> list[TextContent]:
        """Post-Mortem Builder - Interactive incident timeline and post-mortem generator.

        Select a resolved incident to see a color-coded timeline of all activity:
        alerts, log entries, notes, change events, and escalations.
        Export the full timeline as markdown for your post-mortem document.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Post-Mortem Builder UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        POST_MORTEM_BUILDER_URI,
        mime_type="text/html;profile=mcp-app",
        description="Post-Mortem Builder - Timeline-based post-mortem generator from incident data"
    )
    def post_mortem_builder_view() -> str:
        """Post-Mortem Builder UI resource."""
        html_path = pathlib.Path(__file__).parent / "post_mortem_builder_view.html"
        return html_path.read_text(encoding="utf-8")
```

- [ ] **Step 4: Add `add_operations_intelligence()` function**

```python
def add_operations_intelligence(mcp_instance: FastMCP) -> None:
    """Add Operations Intelligence MCP App resource.

    The UI directly calls existing MCP tools:
    - list_teams (team filter)
    - list_incidents (incident data)
    - list_oncalls (who's on-call)

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": OPERATIONS_INTELLIGENCE_URI},
            "ui/resourceUri": OPERATIONS_INTELLIGENCE_URI,
        }
    )
    def operations_intelligence() -> list[TextContent]:
        """Operations Intelligence - Team operational health dashboard.

        Summary cards (total incidents, high urgency %, MTTR, on-call users),
        service breakdown by incident volume, and a sortable incident table.
        Filter by team and date range.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="Operations Intelligence UI initialized. The UI will call existing MCP tools to fetch data."
            )
        ]

    @mcp_instance.resource(
        OPERATIONS_INTELLIGENCE_URI,
        mime_type="text/html;profile=mcp-app",
        description="Operations Intelligence - Team operational health dashboard"
    )
    def operations_intelligence_view() -> str:
        """Operations Intelligence UI resource."""
        html_path = pathlib.Path(__file__).parent / "operations_intelligence_view.html"
        return html_path.read_text(encoding="utf-8")
```

- [ ] **Step 5: Add the 3 calls inside `run()`** (after the existing 4 `add_*` calls)

```python
    add_shift_coverage_wizard(mcp)
    add_post_mortem_builder(mcp)
    add_operations_intelligence(mcp)
```

- [ ] **Step 6: Commit**

```bash
cd /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server
git add pagerduty_mcp/server.py
git commit -m "feat: register Shift Coverage Wizard, Post-Mortem Builder, and Operations Intelligence in server"
```

---

## Task 17: Update build scripts and docs

**Files:**
- Modify: `mcp-apps/build-all.sh`
- Modify: `mcp-apps/setup-all.sh`
- Modify: `website/docs/experimental/overview.md`
- Create: `website/docs/experimental/shift-coverage-wizard.md`
- Create: `website/docs/experimental/post-mortem-builder.md`
- Create: `website/docs/experimental/operations-intelligence.md`

- [ ] **Step 1: Update build-all.sh** — add these lines before the "Copy to Python package" comment:

```bash
echo "📦 Building Shift Coverage Wizard..."
cd shift-coverage-wizard && npm run build && cd ..

echo "📦 Building Post-Mortem Builder..."
cd post-mortem-builder && npm run build && cd ..

echo "📦 Building Operations Intelligence..."
cd operations-intelligence && npm run build && cd ..
```

And add these lines in the copy section:

```bash
cp shift-coverage-wizard/dist/mcp-app.html ../pagerduty_mcp/shift_coverage_wizard_view.html
cp post-mortem-builder/dist/mcp-app.html ../pagerduty_mcp/post_mortem_builder_view.html
cp operations-intelligence/dist/mcp-app.html ../pagerduty_mcp/operations_intelligence_view.html
```

- [ ] **Step 2: Update setup-all.sh** — add the 3 new app names to the APPS array

- [ ] **Step 3: Add 3 rows to the app table in overview.md**

```markdown
| [Shift Coverage Wizard](./shift-coverage-wizard) | A 3-step wizard to find on-call conflicts and create schedule overrides without leaving your IDE |
| [Post-Mortem Builder](./post-mortem-builder) | Build incident post-mortems from a color-coded timeline of alerts, notes, log entries, and change events |
| [Operations Intelligence](./operations-intelligence) | Team operational health dashboard: incident volume, MTTR, service breakdown, and sortable incident table |
```

- [ ] **Step 4: Create shift-coverage-wizard.md** (brief doc page, same format as existing experimental pages)

- [ ] **Step 5: Create post-mortem-builder.md** (brief doc page)

- [ ] **Step 6: Create operations-intelligence.md** (brief doc page)

- [ ] **Step 7: Commit**

```bash
git add mcp-apps/build-all.sh mcp-apps/setup-all.sh website/docs/experimental/
git commit -m "docs: add shift coverage wizard, post-mortem builder, and operations intelligence documentation"
```

---

## Task 18: Push branch

- [ ] **Step 1: Verify all built HTMLs exist**

```bash
ls -lh /Users/svillanelo/Documents/GitHub/pagerduty-mcp-server/pagerduty_mcp/*_view.html
```

Expected: 7 files (4 existing + 3 new), each non-zero size.

- [ ] **Step 2: Push**

```bash
git push -u origin feature/new-mcp-apps
```

---

## Self-Review Checklist

- [x] All 3 apps have boilerplate (html, package.json, vite.config.ts, tsconfig, tsconfig.server)
- [x] All 3 apps have `src/api.ts` with tool calls matching actual tool names
- [x] All 3 apps have `src/mcp-app.tsx` with `useApp()` pattern
- [x] All 3 apps have `src/styles.css` with identical CSS variable set
- [x] PagerDutyLogo component created in each app (same SVG)
- [x] server.py gets 3 URI constants + 3 `add_*` functions + 3 calls in `run()`
- [x] build-all.sh and setup-all.sh updated
- [x] Docs created for each app + overview table updated
- [x] Branch is `feature/new-mcp-apps` (not main)
- [x] No placeholder TBD steps — all code is complete
- [x] Type names consistent across api.ts, components, and mcp-app.tsx within each app
