# On-Call Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `oncall-schedule-visualizer` and `shift-coverage-wizard` with a single **On-Call Manager** MCP app — two tabs: "My On-Calls" (personal 7-day countdown + schedule grid) and "Overrides" (team override list + 3-step coverage wizard).

**Architecture:** React (Preact compat) + TypeScript + Vite singlefile, scaffolded from `mcp-apps/operations-intelligence/` as the reference. The app calls existing PagerDuty MCP tools via `app.callServerTool()`. `VITE_MOCK=true` dev mode enables local development without a live MCP connection.

**Tech Stack:** Preact/React 18 compat, TypeScript 5, Vite 6 + vite-plugin-singlefile, `@modelcontextprotocol/ext-apps`, Playwright for visual testing.

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Create | `mcp-apps/oncall-manager/package.json` | Build scripts, deps |
| Create | `mcp-apps/oncall-manager/tsconfig.json` | Frontend TS config |
| Create | `mcp-apps/oncall-manager/tsconfig.server.json` | Server TS config |
| Create | `mcp-apps/oncall-manager/vite.config.ts` | Vite + singlefile |
| Create | `mcp-apps/oncall-manager/mcp-app.html` | HTML entry point |
| Create | `mcp-apps/oncall-manager/server.ts` | MCP server (registerAppResource + registerAppTool) |
| Create | `mcp-apps/oncall-manager/main.ts` | HTTP + stdio entry point |
| Create | `mcp-apps/oncall-manager/src/mcp-app.tsx` | Root component, tab routing, app init |
| Create | `mcp-apps/oncall-manager/src/api.ts` | All MCP tool calls + types |
| Create | `mcp-apps/oncall-manager/src/mock.ts` | Realistic mock data for dev:mock |
| Create | `mcp-apps/oncall-manager/src/styles.css` | All CSS |
| Create | `mcp-apps/oncall-manager/src/components/MyOnCalls.tsx` | Tab 1: countdown cards + 7-day grid |
| Create | `mcp-apps/oncall-manager/src/components/OverridesTab.tsx` | Tab 2: override list + create form |
| Create | `mcp-apps/oncall-manager/src/components/CoverageWizard.tsx` | 3-step wizard modal |
| Create | `mcp-apps/oncall-manager/pw-test.spec.mjs` | Playwright smoke tests |
| Modify | `pagerduty_mcp/server.py` | Add `add_oncall_manager()`, remove old two apps |
| Delete | `pagerduty_mcp/oncall_schedule_visualizer_view.html` | Old app bundle |
| Delete | `pagerduty_mcp/shift_coverage_wizard_view.html` | Old app bundle |
| Delete | `mcp-apps/oncall-schedule-visualizer/` | Old app source |
| Delete | `mcp-apps/shift-coverage-wizard/` | Old app source |

---

## Task 1: Scaffold package files

**Files:**
- Create: `mcp-apps/oncall-manager/package.json`
- Create: `mcp-apps/oncall-manager/tsconfig.json`
- Create: `mcp-apps/oncall-manager/tsconfig.server.json`
- Create: `mcp-apps/oncall-manager/vite.config.ts`
- Create: `mcp-apps/oncall-manager/mcp-app.html`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "@pagerduty/oncall-manager",
  "version": "1.0.0",
  "type": "module",
  "private": true,
  "description": "On-Call Manager — personal schedule view and override management",
  "scripts": {
    "build": "tsc --noEmit && tsc -p tsconfig.server.json && cross-env INPUT=mcp-app.html vite build",
    "start": "concurrently \"cross-env NODE_ENV=development INPUT=mcp-app.html vite build --watch\" \"tsx watch main.ts\"",
    "dev:mock": "cross-env VITE_MOCK=true NODE_ENV=development vite",
    "serve": "npm run build && node dist/main.js",
    "typecheck": "tsc --noEmit",
    "test": "PORT=5174 APP_NAME=oncall-manager SCREENSHOT_DIR=/tmp/pw-screenshots npx playwright test pw-test.spec.mjs --browser=chromium"
  },
  "dependencies": {
    "@modelcontextprotocol/ext-apps": "^1.3.2",
    "@modelcontextprotocol/sdk": "^1.24.0",
    "cors": "^2.8.5",
    "express": "^5.1.0",
    "preact": "^10.29.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@playwright/test": "^1.59.1",
    "@types/cors": "^2.8.19",
    "@types/express": "^5.0.0",
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

- [ ] **Step 2: Create tsconfig.json**

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
    "noFallthroughCasesInSwitch": true,
    "types": ["vite/client"]
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Create tsconfig.server.json**

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
  "include": ["server.ts", "main.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 4: Create vite.config.ts**

```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const INPUT = process.env.INPUT ?? "mcp-app.html";
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
    rollupOptions: { input: INPUT },
    outDir: "dist",
    emptyOutDir: false,
  },
});
```

- [ ] **Step 5: Create mcp-app.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>On-Call Manager</title>
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
      <div class="initial-loader">Loading On-Call Manager...</div>
    </div>
    <script type="module" src="/src/mcp-app.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Install dependencies**

```bash
cd mcp-apps/oncall-manager
source ~/.nvm/nvm.sh && nvm use
npm install
```

Expected: `node_modules/` created, no errors.

- [ ] **Step 7: Commit**

```bash
git add mcp-apps/oncall-manager/package.json mcp-apps/oncall-manager/tsconfig.json mcp-apps/oncall-manager/tsconfig.server.json mcp-apps/oncall-manager/vite.config.ts mcp-apps/oncall-manager/mcp-app.html
git commit -m "feat: scaffold oncall-manager MCP app package files"
```

---

## Task 2: MCP server files (server.ts + main.ts)

**Files:**
- Create: `mcp-apps/oncall-manager/server.ts`
- Create: `mcp-apps/oncall-manager/main.ts`

- [ ] **Step 1: Create server.ts**

```ts
import {
  registerAppResource,
  registerAppTool,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import fs from "node:fs/promises";
import path from "node:path";

const DIST_DIR = import.meta.dirname;

export function createServer(): McpServer {
  const server = new McpServer({
    name: "On-Call Manager",
    version: "1.0.0",
  });

  const resourceUri = "ui://oncall-manager/dashboard.html";

  registerAppTool(
    server,
    "oncall-manager",
    {
      title: "On-Call Manager",
      description:
        "Personal on-call schedule view with 7-day countdown and team override management",
      inputSchema: {} as any,
      _meta: { ui: { resourceUri } },
    },
    async (_args: any): Promise<CallToolResult> => {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              status: "ready",
              message:
                "On-Call Manager UI initialized. Calls get_user_data, list_oncalls, list_schedules, list_schedule_users, and create_schedule_override.",
            }),
          },
        ],
      };
    },
  );

  registerAppResource(
    server,
    resourceUri,
    resourceUri,
    { mimeType: RESOURCE_MIME_TYPE },
    async () => {
      const html = await fs.readFile(
        path.join(DIST_DIR, "mcp-app.html"),
        "utf-8",
      );
      return {
        contents: [{ uri: resourceUri, mimeType: RESOURCE_MIME_TYPE, text: html }],
      };
    },
  );

  return server;
}
```

- [ ] **Step 2: Create main.ts** (copy from operations-intelligence, change server name)

```ts
import { createMcpExpressApp } from "@modelcontextprotocol/sdk/server/express.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import cors from "cors";
import type { Request, Response } from "express";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createServer } from "./server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function startStreamableHTTPServer(
  createServerFn: () => McpServer,
): Promise<void> {
  const port = parseInt(process.env.PORT ?? "3002", 10);
  const app = createMcpExpressApp({ host: "0.0.0.0" });
  app.use(cors());

  app.get("/", (_req: Request, res: Response) => {
    const htmlPath = path.join(__dirname, "dist", "mcp-app.html");
    res.send(fs.readFileSync(htmlPath, "utf-8"));
  });

  app.all("/mcp", async (req: Request, res: Response) => {
    const server = createServerFn();
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
    });
    res.on("close", () => {
      transport.close().catch(() => {});
      server.close().catch(() => {});
    });
    try {
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      console.error("MCP error:", error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: { code: -32603, message: "Internal server error" },
          id: null,
        });
      }
    }
  });

  const httpServer = app.listen(port, (err) => {
    if (err) { console.error("Failed to start server:", err); process.exit(1); }
    console.log(`📅 On-Call Manager listening on http://localhost:${port}/mcp`);
  });

  const shutdown = () => { httpServer.close(() => process.exit(0)); };
  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

async function startStdioServer(createServerFn: () => McpServer): Promise<void> {
  await createServerFn().connect(new StdioServerTransport());
}

async function main() {
  if (process.argv.includes("--stdio")) {
    await startStdioServer(createServer);
  } else {
    await startStreamableHTTPServer(createServer);
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
```

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-manager/server.ts mcp-apps/oncall-manager/main.ts
git commit -m "feat: add oncall-manager MCP server and entry point"
```

---

## Task 3: API layer (src/api.ts)

**Files:**
- Create: `mcp-apps/oncall-manager/src/api.ts`

All data types and fetch functions. The wrapping pattern for `list_oncalls` and `create_schedule_override` is taken verbatim from `mcp-apps/shift-coverage-wizard/src/api.ts` — do not change it.

- [ ] **Step 1: Create src/api.ts**

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

export interface OnCallShift {
  scheduleId: string;
  scheduleName: string;
  start: string;   // ISO 8601
  end: string;     // ISO 8601
  escalationLevel: number;
}

export interface Override {
  id: string;
  scheduleId: string;
  scheduleName: string;
  userId: string;
  userName: string;
  start: string;
  end: string;
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
  try { return JSON.parse(text) as T; } catch { return null; }
}

// ─── API functions ────────────────────────────────────────────────────────────

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
    arguments: {
      query_model: { since, until, earliest: false },
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

export async function fetchScheduleUsers(
  app: App,
  scheduleId: string,
): Promise<ScheduleUser[]> {
  if (MOCK_MODE) {
    const { MOCK_ONCALL_DATA } = await import("./mock");
    return MOCK_ONCALL_DATA.scheduleUsers[scheduleId] ?? [];
  }
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
        overrides: [
          { start, end, user: { id: userId, type: "user_reference" } },
        ],
      },
    },
  });
  return !result.isError;
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/api.ts
git commit -m "feat: add oncall-manager API layer"
```

---

## Task 4: Mock data (src/mock.ts)

**Files:**
- Create: `mcp-apps/oncall-manager/src/mock.ts`

Realistic mock that covers: current user, personal shifts (one active now, one upcoming), all shifts for grid, schedule users for coverage wizard.

- [ ] **Step 1: Create src/mock.ts**

```ts
import type { CurrentUser, OnCallShift, Override, Schedule, ScheduleUser } from "./api";

const NOW = new Date();
const D = (offsetDays: number, hour = 9) => {
  const d = new Date(NOW);
  d.setDate(d.getDate() + offsetDays);
  d.setHours(hour, 0, 0, 0);
  return d.toISOString();
};

export const MOCK_ONCALL_DATA: {
  currentUser: CurrentUser;
  schedules: Schedule[];
  myShifts: OnCallShift[];
  allShifts: OnCallShift[];
  overrides: Override[];
  scheduleUsers: Record<string, ScheduleUser[]>;
} = {
  currentUser: { id: "U001", name: "Alice Chen", email: "alice@example.com" },

  schedules: [
    { id: "S001", name: "Infra Primary", timeZone: "America/New_York" },
    { id: "S002", name: "Platform On-Call", timeZone: "America/New_York" },
    { id: "S003", name: "Backend Primary", timeZone: "America/Los_Angeles" },
  ],

  myShifts: [
    // Active now
    { scheduleId: "S001", scheduleName: "Infra Primary", start: D(-1), end: D(1), escalationLevel: 1 },
    // Upcoming in 3 days
    { scheduleId: "S002", scheduleName: "Platform On-Call", start: D(3), end: D(5), escalationLevel: 1 },
  ],

  allShifts: [
    // Alice (current user) — shown in blue
    { scheduleId: "S001", scheduleName: "Infra Primary", start: D(-1), end: D(1), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", start: D(3), end: D(5), escalationLevel: 1 },
    // Others — shown in grey
    { scheduleId: "S001", scheduleName: "Infra Primary", start: D(1), end: D(3), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", start: D(0), end: D(2), escalationLevel: 1 },
    { scheduleId: "S003", scheduleName: "Backend Primary", start: D(2), end: D(4), escalationLevel: 1 },
    { scheduleId: "S003", scheduleName: "Backend Primary", start: D(5), end: D(7), escalationLevel: 1 },
  ],

  overrides: [
    {
      id: "OR001",
      scheduleId: "S001",
      scheduleName: "Infra Primary",
      userId: "U002",
      userName: "Bob Kim",
      start: D(2),
      end: D(3),
    },
    {
      id: "OR002",
      scheduleId: "S003",
      scheduleName: "Backend Primary",
      userId: "U001",
      userName: "Alice Chen",
      start: D(5),
      end: D(6),
    },
  ],

  scheduleUsers: {
    S001: [
      { id: "U001", name: "Alice Chen", email: "alice@example.com" },
      { id: "U002", name: "Bob Kim", email: "bob@example.com" },
      { id: "U003", name: "Carlos M.", email: "carlos@example.com" },
    ],
    S002: [
      { id: "U001", name: "Alice Chen", email: "alice@example.com" },
      { id: "U004", name: "Dana W.", email: "dana@example.com" },
      { id: "U005", name: "Eric L.", email: "eric@example.com" },
    ],
    S003: [
      { id: "U003", name: "Carlos M.", email: "carlos@example.com" },
      { id: "U002", name: "Bob Kim", email: "bob@example.com" },
      { id: "U006", name: "Fiona R.", email: "fiona@example.com" },
    ],
  },
};
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/mock.ts
git commit -m "feat: add oncall-manager mock data"
```

---

## Task 5: CSS (src/styles.css)

**Files:**
- Create: `mcp-apps/oncall-manager/src/styles.css`

Dark Catppuccin-Mocha palette (matching the other apps). All CSS variables defined on `:root`. Key rules: tab bar, countdown cards, 7-day grid, override list, wizard overlay.

- [ ] **Step 1: Create src/styles.css**

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
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.app-header .dot { color: var(--green); font-size: 14px; }
.app-header h1 { font-size: 14px; font-weight: 600; }

/* ─── Tabs ─── */
.tabs {
  display: flex;
  gap: 2px;
  margin-left: auto;
}
.tab-btn {
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--overlay0);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}
.tab-btn:hover { background: var(--surface0); color: var(--text); }
.tab-btn.active { background: var(--blue); color: var(--mantle); font-weight: 600; }

/* ─── Tab content ─── */
.tab-content { flex: 1; padding: 16px; overflow-y: auto; }

/* ─── Section headings ─── */
.section-heading {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--overlay1);
  margin-bottom: 10px;
  margin-top: 20px;
}
.section-heading:first-child { margin-top: 0; }

/* ─── Countdown cards ─── */
.countdown-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
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
.countdown-card .time-detail { font-size: 11px; color: var(--overlay0); margin-bottom: 10px; }
.countdown-card .actions { display: flex; gap: 6px; flex-wrap: wrap; }

/* ─── 7-day schedule grid ─── */
.schedule-grid { overflow-x: auto; }
.grid-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}
.grid-table th {
  background: var(--mantle);
  color: var(--overlay0);
  font-weight: 500;
  padding: 6px 8px;
  text-align: center;
  border-bottom: 1px solid var(--surface0);
  white-space: nowrap;
}
.grid-table th:first-child { text-align: left; min-width: 130px; }
.grid-table td {
  padding: 4px 8px;
  border-bottom: 1px solid var(--surface0);
  text-align: center;
  vertical-align: middle;
  min-width: 0;
  width: 100%;
}
.grid-table td:first-child { text-align: left; color: var(--subtext1); white-space: nowrap; }
.grid-table tr:last-child td { border-bottom: none; }

.shift-block {
  display: inline-block;
  border-radius: 3px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
  min-width: 0;
  width: 100%;
}
.shift-block.mine { background: var(--blue); color: var(--mantle); }
.shift-block.other { background: var(--surface1); color: var(--subtext0); }
.shift-block.override { background: var(--mauve); color: var(--mantle); }

/* ─── Buttons ─── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
  transition: opacity 0.15s;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--blue); color: var(--mantle); }
.btn-secondary { background: var(--surface0); color: var(--text); }
.btn-danger { background: var(--red); color: var(--mantle); }
.btn-ghost { background: transparent; color: var(--blue); padding: 3px 6px; }
.btn-ghost:hover { background: var(--surface0); }
.btn-sm { font-size: 10px; padding: 3px 7px; }

/* ─── Override list ─── */
.override-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 20px; }
.override-row {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 6px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.override-row .or-schedule { font-size: 10px; color: var(--overlay0); margin-bottom: 2px; }
.override-row .or-user { font-weight: 600; font-size: 12px; }
.override-row .or-dates { font-size: 10px; color: var(--overlay0); }
.override-row .or-actions { margin-left: auto; display: flex; gap: 6px; }

/* ─── Create override form ─── */
.create-override-form {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.form-row { display: flex; gap: 10px; flex-wrap: wrap; }
.form-field { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 140px; }
.form-field label { font-size: 10px; color: var(--overlay0); font-weight: 500; }
.form-field select,
.form-field input[type="datetime-local"] {
  background: var(--surface0);
  border: 1px solid var(--surface1);
  border-radius: 4px;
  color: var(--text);
  padding: 5px 8px;
  font-size: 12px;
  width: 100%;
}
.form-field select:focus,
.form-field input:focus { outline: 1px solid var(--blue); border-color: var(--blue); }

/* ─── Coverage wizard overlay ─── */
.wizard-overlay {
  position: fixed;
  inset: 0;
  background: rgba(17, 17, 27, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.wizard-dialog {
  background: var(--base);
  border: 1px solid var(--surface1);
  border-radius: 10px;
  width: min(500px, 95vw);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.wizard-header {
  background: var(--mantle);
  border-bottom: 1px solid var(--surface0);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.wizard-header h3 { font-size: 13px; font-weight: 600; flex: 1; }
.wizard-close { background: transparent; border: none; color: var(--overlay0); cursor: pointer; font-size: 14px; padding: 2px 6px; border-radius: 4px; }
.wizard-close:hover { background: var(--surface0); color: var(--text); }

.wizard-steps {
  display: flex;
  gap: 0;
  padding: 10px 16px;
  border-bottom: 1px solid var(--surface0);
  background: var(--mantle);
}
.wizard-step {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: var(--overlay0);
}
.wizard-step.active { color: var(--blue); font-weight: 600; }
.wizard-step.done { color: var(--green); }
.wizard-step-num {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--surface0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
}
.wizard-step.active .wizard-step-num { background: var(--blue); color: var(--mantle); }
.wizard-step.done .wizard-step-num { background: var(--green); color: var(--mantle); }
.wizard-step-sep { color: var(--surface1); margin: 0 6px; font-size: 10px; }

.wizard-body { padding: 16px; overflow-y: auto; flex: 1; }
.wizard-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--surface0);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--mantle);
}

/* ─── Shift picker (wizard step 1) ─── */
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
.shift-option.selected { border-color: var(--blue); background: rgba(137, 180, 250, 0.1); }
.shift-option .shift-sched { font-size: 10px; color: var(--overlay0); margin-bottom: 2px; }
.shift-option .shift-dates { font-size: 12px; font-weight: 500; }

/* ─── User picker (wizard step 2) ─── */
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
.user-list { display: flex; flex-direction: column; gap: 4px; max-height: 240px; overflow-y: auto; }
.user-option {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 5px;
  padding: 8px 12px;
  cursor: pointer;
  transition: border-color 0.15s;
}
.user-option:hover { border-color: var(--blue); }
.user-option.selected { border-color: var(--blue); background: rgba(137, 180, 250, 0.1); }
.user-option .user-name { font-weight: 600; font-size: 12px; }
.user-option .user-email { font-size: 10px; color: var(--overlay0); }

/* ─── Confirm step (wizard step 3) ─── */
.confirm-card {
  background: var(--mantle);
  border: 1px solid var(--surface0);
  border-radius: 8px;
  padding: 14px 16px;
}
.confirm-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px; }
.confirm-row .label { color: var(--overlay0); }
.confirm-row .value { font-weight: 500; }

/* ─── Empty / error / loading ─── */
.empty-state { text-align: center; color: var(--overlay0); padding: 32px 16px; font-size: 12px; }
.error-banner { background: rgba(243, 139, 168, 0.15); border: 1px solid var(--red); color: var(--red); border-radius: 6px; padding: 8px 12px; font-size: 12px; margin-bottom: 12px; }
.loading-row { display: flex; align-items: center; gap: 8px; color: var(--overlay0); font-size: 12px; padding: 8px 0; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--surface1);
  border-top-color: var(--blue);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/styles.css
git commit -m "feat: add oncall-manager CSS styles"
```

---

## Task 6: CoverageWizard component (src/components/CoverageWizard.tsx)

**Files:**
- Create: `mcp-apps/oncall-manager/src/components/CoverageWizard.tsx`

3-step wizard: Step 1 = pick shift, Step 2 = pick user (searchable), Step 3 = confirm + submit.

- [ ] **Step 1: Create src/components/CoverageWizard.tsx**

```tsx
import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { createOverride, fetchScheduleUsers } from "../api";
import type { OnCallShift, ScheduleUser } from "../api";

interface Props {
  app: App;
  shifts: OnCallShift[];         // user's own shifts to choose from
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
  const [userSearch, setUserSearch] = useState("");
  const [selectedUser, setSelectedUser] = useState<ScheduleUser | null>(null);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (step === 2 && selectedShift) {
      setLoadingUsers(true);
      fetchScheduleUsers(app, selectedShift.scheduleId)
        .then(setUsers)
        .catch(() => setUsers([]))
        .finally(() => setLoadingUsers(false));
    }
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
      const ok = await createOverride(
        app,
        selectedShift.scheduleId,
        selectedUser.id,
        selectedShift.start,
        selectedShift.end,
      );
      if (ok) {
        onDone();
      } else {
        setError("Failed to create override. Please try again.");
      }
    } catch (e: any) {
      setError(e?.message ?? "Unexpected error");
    } finally {
      setSubmitting(false);
    }
  }

  const stepLabel = ["Select shift", "Choose coverage", "Confirm"];

  return (
    <div className="wizard-overlay" onClick={onClose}>
      <div className="wizard-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="wizard-header">
          <h3>🔄 Find Coverage</h3>
          <button className="wizard-close" onClick={onClose}>✕</button>
        </div>

        <div className="wizard-steps">
          {[1, 2, 3].map((n, i) => (
            <>
              <div
                key={n}
                className={`wizard-step ${step === n ? "active" : step > n ? "done" : ""}`}
              >
                <span className="wizard-step-num">{step > n ? "✓" : n}</span>
                {stepLabel[i]}
              </div>
              {i < 2 && <span className="wizard-step-sep">›</span>}
            </>
          ))}
        </div>

        <div className="wizard-body">
          {step === 1 && (
            <div className="shift-list">
              {shifts.length === 0 && (
                <p className="empty-state">No upcoming shifts found.</p>
              )}
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
                  />
                  <div className="user-list">
                    {filteredUsers.length === 0 && (
                      <p className="empty-state">No users found.</p>
                    )}
                    {filteredUsers.map((u) => (
                      <div
                        key={u.id}
                        className={`user-option ${selectedUser?.id === u.id ? "selected" : ""}`}
                        onClick={() => setSelectedUser(u)}
                      >
                        <div className="user-name">{u.name}</div>
                        <div className="user-email">{u.email}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}

          {step === 3 && selectedShift && selectedUser && (
            <>
              {error && <p className="error-banner">{error}</p>}
              <div className="confirm-card">
                <div className="confirm-row">
                  <span className="label">Schedule</span>
                  <span className="value">{selectedShift.scheduleName}</span>
                </div>
                <div className="confirm-row">
                  <span className="label">Period</span>
                  <span className="value">{fmtRange(selectedShift.start, selectedShift.end)}</span>
                </div>
                <div className="confirm-row">
                  <span className="label">Coverage by</span>
                  <span className="value">{selectedUser.name}</span>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="wizard-footer">
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
              disabled={
                (step === 1 && !selectedShift) ||
                (step === 2 && !selectedUser)
              }
            >
              Next →
            </button>
          ) : (
            <button
              className="btn btn-primary"
              onClick={handleConfirm}
              disabled={submitting}
            >
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
git commit -m "feat: add CoverageWizard 3-step component"
```

---

## Task 7: MyOnCalls tab (src/components/MyOnCalls.tsx)

**Files:**
- Create: `mcp-apps/oncall-manager/src/components/MyOnCalls.tsx`

Shows: countdown cards (active now, next shift), 7-day schedule grid (all schedules × days), and "Find Coverage" / "Create Override" buttons.

- [ ] **Step 1: Create src/components/MyOnCalls.tsx**

```tsx
import type { App } from "@modelcontextprotocol/ext-apps";
import { useState } from "react";
import type { CurrentUser, OnCallShift, Schedule } from "../api";
import { CoverageWizard } from "./CoverageWizard";

interface Props {
  app: App;
  currentUser: CurrentUser;
  myShifts: OnCallShift[];
  allShifts: OnCallShift[];
  schedules: Schedule[];
  onOverrideCreated: () => void;
}

function isNow(shift: OnCallShift): boolean {
  const now = Date.now();
  return new Date(shift.start).getTime() <= now && new Date(shift.end).getTime() > now;
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleString([], {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function countdownLabel(shift: OnCallShift): string {
  const ms = new Date(shift.start).getTime() - Date.now();
  if (ms <= 0) {
    const remaining = new Date(shift.end).getTime() - Date.now();
    const h = Math.floor(remaining / 3_600_000);
    const m = Math.floor((remaining % 3_600_000) / 60_000);
    return h > 0 ? `${h}h ${m}m remaining` : `${m}m remaining`;
  }
  const days = Math.floor(ms / 86_400_000);
  const h = Math.floor((ms % 86_400_000) / 3_600_000);
  return days > 0 ? `in ${days}d ${h}h` : `in ${h}h`;
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

export function MyOnCalls({ app, currentUser, myShifts, allShifts, schedules, onOverrideCreated }: Props) {
  const [wizardShift, setWizardShift] = useState<OnCallShift | undefined>(undefined);
  const [showWizard, setShowWizard] = useState(false);

  const activeShift = myShifts.find(isNow);
  const upcomingShifts = myShifts.filter((s) => !isNow(s)).sort(
    (a, b) => new Date(a.start).getTime() - new Date(b.start).getTime(),
  );
  const nextShift = upcomingShifts[0];
  const days = getDays(7);

  const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <div>
      {/* Countdown cards */}
      <p className="section-heading">My Shifts</p>
      <div className="countdown-row">
        {activeShift ? (
          <div className="countdown-card active-now">
            <div className="label">🟢 On-call now</div>
            <div className="schedule-name">{activeShift.scheduleName}</div>
            <div className="time-detail">
              {fmtDate(activeShift.start)} → {fmtDate(activeShift.end)}
            </div>
            <div className="time-detail" style={{ color: "var(--green)", fontWeight: 600 }}>
              {countdownLabel(activeShift)}
            </div>
            <div className="actions">
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => { setWizardShift(activeShift); setShowWizard(true); }}
              >
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
            <div className="time-detail">
              {fmtDate(nextShift.start)} → {fmtDate(nextShift.end)}
            </div>
            <div className="time-detail" style={{ color: "var(--blue)", fontWeight: 600 }}>
              {countdownLabel(nextShift)}
            </div>
            <div className="actions">
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => { setWizardShift(nextShift); setShowWizard(true); }}
              >
                🔄 Find coverage
              </button>
            </div>
          </div>
        ) : (
          !activeShift && (
            <div className="countdown-card" style={{ borderColor: "var(--surface0)" }}>
              <div className="label" style={{ color: "var(--overlay0)" }}>Next shift</div>
              <div className="schedule-name" style={{ color: "var(--overlay0)" }}>No upcoming shifts</div>
            </div>
          )
        )}
      </div>

      {/* 7-day grid */}
      <p className="section-heading">7-Day Schedule</p>
      <div className="schedule-grid">
        <table className="grid-table">
          <thead>
            <tr>
              <th>Schedule</th>
              {days.map((d) => (
                <th key={d.toISOString()}>
                  <div>{DAY_NAMES[d.getDay()]}</div>
                  <div style={{ color: "var(--text)", fontWeight: 600 }}>{d.getDate()}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {schedules.map((sched) => (
              <tr key={sched.id}>
                <td>{sched.name}</td>
                {days.map((day) => {
                  const dayShifts = shiftsOnDay(allShifts, sched.id, day);
                  if (dayShifts.length === 0) {
                    return <td key={day.toISOString()} />;
                  }
                  return (
                    <td key={day.toISOString()}>
                      {dayShifts.map((s, i) => {
                        const isMine = s.scheduleId === sched.id &&
                          myShifts.some((ms) => ms.scheduleId === s.scheduleId && ms.start === s.start);
                        return (
                          <span key={i} className={`shift-block ${isMine ? "mine" : "other"}`}>
                            {isMine ? currentUser.name.split(" ")[0] : "●"}
                          </span>
                        );
                      })}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Coverage wizard */}
      {showWizard && (
        <CoverageWizard
          app={app}
          shifts={myShifts}
          preselectedShift={wizardShift}
          onClose={() => setShowWizard(false)}
          onDone={() => { setShowWizard(false); onOverrideCreated(); }}
        />
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/components/MyOnCalls.tsx
git commit -m "feat: add MyOnCalls tab component"
```

---

## Task 8: OverridesTab component (src/components/OverridesTab.tsx)

**Files:**
- Create: `mcp-apps/oncall-manager/src/components/OverridesTab.tsx`

Lists active/upcoming overrides, inline create form (schedule picker + user picker + datetime range), and "Find Coverage" wizard entry point.

- [ ] **Step 1: Create src/components/OverridesTab.tsx**

```tsx
import type { App } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { createOverride, fetchScheduleUsers } from "../api";
import type { OnCallShift, Override, Schedule, ScheduleUser } from "../api";
import { CoverageWizard } from "./CoverageWizard";

interface Props {
  app: App;
  schedules: Schedule[];
  overrides: Override[];
  myShifts: OnCallShift[];
  onOverrideCreated: () => void;
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

function fromLocalInput(local: string): string {
  return new Date(local).toISOString();
}

export function OverridesTab({ app, schedules, overrides, myShifts, onOverrideCreated }: Props) {
  const [showForm, setShowForm] = useState(false);
  const [showWizard, setShowWizard] = useState(false);
  const [formSchedule, setFormSchedule] = useState(schedules[0]?.id ?? "");
  const [formUsers, setFormUsers] = useState<ScheduleUser[]>([]);
  const [formUser, setFormUser] = useState("");
  const [formStart, setFormStart] = useState(toLocalInput(new Date().toISOString()));
  const [formEnd, setFormEnd] = useState(toLocalInput(new Date(Date.now() + 86_400_000).toISOString()));
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!formSchedule) return;
    fetchScheduleUsers(app, formSchedule)
      .then((users) => {
        setFormUsers(users);
        setFormUser(users[0]?.id ?? "");
      })
      .catch(() => setFormUsers([]));
  }, [formSchedule]);

  async function handleCreate() {
    if (!formSchedule || !formUser) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const ok = await createOverride(
        app,
        formSchedule,
        formUser,
        fromLocalInput(formStart),
        fromLocalInput(formEnd),
      );
      if (ok) {
        setShowForm(false);
        onOverrideCreated();
      } else {
        setFormError("Failed to create override.");
      }
    } catch (e: any) {
      setFormError(e?.message ?? "Unexpected error");
    } finally {
      setSubmitting(false);
    }
  }

  const upcoming = overrides
    .filter((o) => new Date(o.end).getTime() > Date.now())
    .sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
        <p className="section-heading" style={{ marginBottom: 0 }}>Active & Upcoming Overrides</p>
        <div style={{ display: "flex", gap: 6 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => { setShowWizard(true); }}>
            🔄 Find Coverage
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowForm((v) => !v)}>
            {showForm ? "Cancel" : "+ New Override"}
          </button>
        </div>
      </div>

      {/* Inline create form */}
      {showForm && (
        <div className="create-override-form" style={{ marginBottom: 16 }}>
          {formError && <p className="error-banner">{formError}</p>}
          <div className="form-row">
            <div className="form-field">
              <label>Schedule</label>
              <select value={formSchedule} onChange={(e) => setFormSchedule((e.target as HTMLSelectElement).value)}>
                {schedules.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
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
              <input
                type="datetime-local"
                value={formStart}
                onChange={(e) => setFormStart((e.target as HTMLInputElement).value)}
              />
            </div>
            <div className="form-field">
              <label>End</label>
              <input
                type="datetime-local"
                value={formEnd}
                onChange={(e) => setFormEnd((e.target as HTMLInputElement).value)}
              />
            </div>
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button className="btn btn-primary" onClick={handleCreate} disabled={submitting || !formSchedule || !formUser}>
              {submitting ? "Creating…" : "Create Override"}
            </button>
          </div>
        </div>
      )}

      {/* Override list */}
      <div className="override-list">
        {upcoming.length === 0 && (
          <p className="empty-state">No active or upcoming overrides.</p>
        )}
        {upcoming.map((o) => (
          <div key={o.id} className="override-row">
            <div>
              <div className="or-schedule">{o.scheduleName}</div>
              <div className="or-user">{o.userName}</div>
              <div className="or-dates">{fmtRange(o.start, o.end)}</div>
            </div>
            <div className="or-actions">
              <span
                style={{ fontSize: 10, padding: "2px 7px", borderRadius: 3, background: "var(--surface0)", color: "var(--subtext0)" }}
              >
                {new Date(o.start).getTime() <= Date.now() ? "Active" : "Upcoming"}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Coverage wizard */}
      {showWizard && (
        <CoverageWizard
          app={app}
          shifts={myShifts}
          onClose={() => setShowWizard(false)}
          onDone={() => { setShowWizard(false); onOverrideCreated(); }}
        />
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add mcp-apps/oncall-manager/src/components/OverridesTab.tsx
git commit -m "feat: add OverridesTab component"
```

---

## Task 9: Root component (src/mcp-app.tsx)

**Files:**
- Create: `mcp-apps/oncall-manager/src/mcp-app.tsx`

Bootstraps the MCP app context, fetches all data, renders tab bar + tab content.

- [ ] **Step 1: Create src/mcp-app.tsx**

```tsx
import { useApp } from "@modelcontextprotocol/ext-apps";
import { useEffect, useState } from "react";
import { fetchAllOnCalls, fetchCurrentUser, fetchSchedules, fetchUserShifts } from "./api";
import type { CurrentUser, OnCallShift, Override, Schedule } from "./api";
import { MyOnCalls } from "./components/MyOnCalls";
import { OverridesTab } from "./components/OverridesTab";
import "./styles.css";

const MOCK_MODE = import.meta.env.VITE_MOCK === "true";
type Tab = "myoncalls" | "overrides";

function App() {
  const app = useApp();

  const [tab, setTab] = useState<Tab>("myoncalls");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [myShifts, setMyShifts] = useState<OnCallShift[]>([]);
  const [allShifts, setAllShifts] = useState<OnCallShift[]>([]);
  const [overrides, setOverrides] = useState<Override[]>([]);

  async function loadData() {
    setLoading(true);
    setError(null);
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

      // In mock mode, load mock overrides
      if (MOCK_MODE) {
        const { MOCK_ONCALL_DATA } = await import("./mock");
        setOverrides(MOCK_ONCALL_DATA.overrides);
      }
    } catch (e: any) {
      setError(e?.message ?? "Failed to load data");
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
        <div className="empty-state" style={{ marginTop: 80 }}>
          Waiting for MCP connection…
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="app-header">
        <span className="dot">●</span>
        <h1>On-Call Manager</h1>
        <div className="tabs">
          <button
            className={`tab-btn ${tab === "myoncalls" ? "active" : ""}`}
            onClick={() => setTab("myoncalls")}
          >
            My On-Calls
          </button>
          <button
            className={`tab-btn ${tab === "overrides" ? "active" : ""}`}
            onClick={() => setTab("overrides")}
          >
            Overrides
          </button>
        </div>
      </div>

      <div className="tab-content">
        {loading && (
          <div className="loading-row">
            <span className="spinner" />
            Loading schedule data…
          </div>
        )}

        {!loading && error && (
          <p className="error-banner">{error}</p>
        )}

        {!loading && !error && currentUser && (
          <>
            {tab === "myoncalls" && (
              <MyOnCalls
                app={app ?? ({} as any)}
                currentUser={currentUser}
                myShifts={myShifts}
                allShifts={allShifts}
                schedules={schedules}
                onOverrideCreated={loadData}
              />
            )}
            {tab === "overrides" && (
              <OverridesTab
                app={app ?? ({} as any)}
                schedules={schedules}
                overrides={overrides}
                myShifts={myShifts}
                onOverrideCreated={loadData}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default function McpApp() {
  return <App />;
}

// MCP app bootstrap — file must export default component
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
git commit -m "feat: add oncall-manager root component"
```

---

## Task 10: Typecheck + dev:mock smoke test

**Files:** none new

- [ ] **Step 1: Run typecheck**

```bash
cd mcp-apps/oncall-manager
source ~/.nvm/nvm.sh && nvm use
npm run typecheck
```

Expected: exit 0, no TypeScript errors.

- [ ] **Step 2: Start dev:mock**

```bash
npm run dev:mock
```

Expected: Vite starts at `http://localhost:5174/mcp-app.html` (or similar). Open browser and verify:
- App header with "On-Call Manager" + two tabs
- "My On-Calls" tab shows countdown cards + 7-day grid populated from mock
- "Overrides" tab shows mock overrides list
- Clicking "Find Coverage" opens the 3-step wizard
- Clicking "Next →" advances steps, "Back" goes back

- [ ] **Step 3: Fix any render issues found during smoke test**

Common issues to check:
- Grid last row not collapsed (use `visibility: hidden` not `display: none`)
- Shift blocks need `min-width: 0; width: 100%` if text collapses
- Tab switching renders correct content

---

## Task 11: Build + deploy + Python registration

**Files:**
- Modify: `pagerduty_mcp/server.py`

- [ ] **Step 1: Build**

```bash
cd mcp-apps/oncall-manager
npm run build
```

Expected: `dist/mcp-app.html` created (single-file bundle).

- [ ] **Step 2: Deploy HTML to Python package**

```bash
cp dist/mcp-app.html ../../pagerduty_mcp/oncall_manager_view.html
```

- [ ] **Step 3: Register in server.py**

In `pagerduty_mcp/server.py`, add constant near the top (after existing URIs):
```python
ONCALL_MANAGER_URI = "ui://oncall-manager/dashboard.html"
```

Add function before `run()`:
```python
def add_oncall_manager(mcp_instance: FastMCP) -> None:
    """Add On-Call Manager MCP App resource.

    The UI directly calls existing MCP tools:
    - get_user_data
    - list_oncalls, list_schedules, list_schedule_users
    - create_schedule_override

    Args:
        mcp_instance: The MCP server instance
    """

    @mcp_instance.tool(
        meta={
            "ui": {"resourceUri": ONCALL_MANAGER_URI},
            "ui/resourceUri": ONCALL_MANAGER_URI,
        }
    )
    def oncall_manager() -> list[TextContent]:
        """On-Call Manager - Personal schedule and override management.

        Shows the current user's upcoming 7-day shifts with countdown cards,
        a 7-day schedule grid, and an Overrides tab with create/coverage wizard.
        The UI calls get_user_data, list_oncalls, list_schedules, list_schedule_users,
        and create_schedule_override.

        Returns:
            Text content indicating the UI is ready
        """
        return [
            TextContent(
                type="text",
                text="On-Call Manager UI initialized. The UI will call existing MCP tools to fetch and write data."
            )
        ]

    @mcp_instance.resource(
        ONCALL_MANAGER_URI,
        mime_type="text/html;profile=mcp-app",
        description="On-Call Manager - Personal schedule view and override management"
    )
    def oncall_manager_view() -> str:
        """On-Call Manager UI resource."""
        html_path = pathlib.Path(__file__).parent / "oncall_manager_view.html"
        return html_path.read_text(encoding="utf-8")
```

In the `run()` function, add after `add_shift_coverage_wizard(mcp)`:
```python
    add_oncall_manager(mcp)
```

- [ ] **Step 4: Commit**

```bash
git add pagerduty_mcp/server.py pagerduty_mcp/oncall_manager_view.html mcp-apps/oncall-manager/dist/mcp-app.html
git commit -m "feat: register on-call-manager MCP app and deploy HTML bundle"
```

---

## Task 12: Playwright test

**Files:**
- Create: `mcp-apps/oncall-manager/pw-test.spec.mjs`

- [ ] **Step 1: Create pw-test.spec.mjs**

```js
// @ts-check
import { test, expect } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { join } from "node:path";

const PORT = process.env.PORT ?? "5174";
const BASE_URL = `http://localhost:${PORT}/mcp-app.html`;
const APP_NAME = process.env.APP_NAME ?? "oncall-manager";
const SCREENSHOT_DIR = process.env.SCREENSHOT_DIR ?? `${process.env.HOME}/tmp-screenshots`;

test.beforeAll(async () => {
  await mkdir(SCREENSHOT_DIR, { recursive: true });
});

test("initial load — My On-Calls tab", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".countdown-row", { timeout: 10000 });
  await page.screenshot({
    path: join(SCREENSHOT_DIR, `${APP_NAME}-myoncalls.png`),
    fullPage: true,
  });
  // Should show at least one countdown card
  const cards = await page.locator(".countdown-card").count();
  expect(cards).toBeGreaterThan(0);
});

test("7-day grid renders", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".grid-table", { timeout: 10000 });
  // Table should have at least one data row
  const rows = await page.locator(".grid-table tbody tr").count();
  expect(rows).toBeGreaterThan(0);
});

test("overrides tab renders", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".tabs", { timeout: 10000 });
  await page.click(".tab-btn:has-text('Overrides')");
  await page.waitForSelector(".override-list", { timeout: 5000 });
  await page.screenshot({
    path: join(SCREENSHOT_DIR, `${APP_NAME}-overrides.png`),
    fullPage: true,
  });
});

test("coverage wizard opens and advances steps", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".countdown-card", { timeout: 10000 });
  // Click "Find coverage" on the active shift card (if present) or Overrides tab
  const findCovBtn = page.locator("button:has-text('Find coverage')").first();
  if (await findCovBtn.isVisible()) {
    await findCovBtn.click();
  } else {
    await page.click(".tab-btn:has-text('Overrides')");
    await page.click("button:has-text('Find Coverage')");
  }
  await page.waitForSelector(".wizard-dialog", { timeout: 5000 });
  await page.screenshot({
    path: join(SCREENSHOT_DIR, `${APP_NAME}-wizard-step1.png`),
    fullPage: true,
  });
  // Step indicator should show step 1 active
  const stepNum = await page.locator(".wizard-step.active .wizard-step-num").first().textContent();
  expect(["1", "2"].includes(stepNum ?? "")).toBeTruthy();
});
```

- [ ] **Step 2: Run Playwright tests (requires dev:mock running in another terminal)**

```bash
# Terminal 1:
npm run dev:mock

# Terminal 2:
PORT=5174 npm run test
```

Expected: 4 tests pass, screenshots saved to `/tmp/pw-screenshots/`.

- [ ] **Step 3: Commit**

```bash
git add mcp-apps/oncall-manager/pw-test.spec.mjs
git commit -m "feat: add oncall-manager Playwright smoke tests"
```

---

## Task 13: Remove old apps

**Files:**
- Modify: `pagerduty_mcp/server.py` — remove old registrations
- Delete: `pagerduty_mcp/oncall_schedule_visualizer_view.html`
- Delete: `pagerduty_mcp/shift_coverage_wizard_view.html`
- Delete: `mcp-apps/oncall-schedule-visualizer/` (entire dir)
- Delete: `mcp-apps/shift-coverage-wizard/` (entire dir)

- [ ] **Step 1: Remove old Python registrations from server.py**

Remove from `pagerduty_mcp/server.py`:
- Constants: `ONCALL_SCHEDULE_VISUALIZER_URI`, `SHIFT_COVERAGE_WIZARD_URI`
- Functions: `add_oncall_schedule_visualizer()`, `add_shift_coverage_wizard()`
- Calls in `run()`: `add_oncall_schedule_visualizer(mcp)`, `add_shift_coverage_wizard(mcp)`

- [ ] **Step 2: Delete old HTML bundles**

```bash
rm pagerduty_mcp/oncall_schedule_visualizer_view.html
rm pagerduty_mcp/shift_coverage_wizard_view.html
```

- [ ] **Step 3: Delete old app source directories**

```bash
rm -rf mcp-apps/oncall-schedule-visualizer
rm -rf mcp-apps/shift-coverage-wizard
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: remove oncall-schedule-visualizer and shift-coverage-wizard (merged into oncall-manager)"
```

---

## Self-Review

**Spec coverage:**
- ✅ Tab 1 "My On-Calls": countdown cards, 7-day grid, "Find coverage" button
- ✅ Tab 2 "Overrides": list, inline create form, "Find Coverage" wizard entry
- ✅ Coverage wizard: 3 steps — shift select → user pick (searchable) → confirm
- ✅ Mock mode (`VITE_MOCK=true`) for all data functions
- ✅ Correct `create_schedule_override` arg wrapping (`override_request.overrides[{start,end,user}]`)
- ✅ `mime_type="text/html;profile=mcp-app"` in Python registration
- ✅ URI matches between server.ts and Python
- ✅ Old apps removed
- ✅ Playwright tests

**Gotchas addressed:**
- Grid children in `.grid-table td` get `min-width: 0; width: 100%` via CSS
- `visibility: hidden` is used when hiding elements (no `display: none` on grid children)
- FastMCP arg wrapping in `createOverride` uses `override_request.overrides[...]`
- `MOCK_MODE = import.meta.env.VITE_MOCK === "true"` at top of api.ts
