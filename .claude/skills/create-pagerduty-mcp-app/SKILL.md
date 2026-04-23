---
name: create-pagerduty-mcp-app
description: Use when creating a new MCP app in pagerduty-mcp-server, modifying an existing app's build or Python registration, writing mock data for dev:mock, or visually testing an MCP app before deploying its HTML bundle.
---

# Create PagerDuty MCP App

## Overview

Each MCP app is a React + TypeScript single-file bundle served by the Python FastMCP server as a resource. The Python side registers a trigger tool + HTML resource. The TypeScript side calls existing MCP tools via `app.callServerTool()`.

Reference implementations:
- `mcp-apps/post-mortem-builder/` — list → detail navigation pattern
- `mcp-apps/operations-intelligence/` — multi-tab dashboard with analytics

For MCP Apps SDK fundamentals (host APIs, streaming, fullscreen, CSP) see `mcp-apps:create-mcp-app`.

---

## 1. Scaffold

Copy from the closest reference app, then rename:

```
mcp-apps/<app-name>/
├── package.json            # scripts: build, start, serve, dev:mock, typecheck, test
├── tsconfig.json           # src/ only, noEmit: true
├── tsconfig.server.json    # server.ts + main.ts → dist/
├── vite.config.ts          # viteSingleFile, preact aliases, INPUT ?? "mcp-app.html"
├── mcp-app.html            # Vite entry point
├── server.ts               # registerAppTool + registerAppResource
├── main.ts                 # HTTP (port 3001) + --stdio mode
└── src/
    ├── mcp-app.tsx         # useApp() + mockMode guard
    ├── api.ts              # MOCK_MODE check + app.callServerTool() calls
    ├── mock.ts             # MOCK_<APP>_DATA + any canned responses
    ├── styles.css          # CSS variables (light + dark), component styles
    └── components/         # React components
```

---

## 2. Python server registration

Add to `pagerduty_mcp/server.py`:

```python
APP_URI = "ui://<app-name>/<filename>.html"  # MUST match registerAppResource URI in server.ts

def add_<app_name>(mcp_instance: FastMCP) -> None:
    @mcp_instance.tool(meta={"ui": {"resourceUri": APP_URI}, "ui/resourceUri": APP_URI})
    def <app_name>() -> list[TextContent]:
        """<Description>. UI calls existing MCP tools."""
        return [TextContent(type="text", text="<App> UI initialized.")]

    @mcp_instance.resource(
        APP_URI,
        mime_type="text/html;profile=mcp-app",   # NOT plain "text/html"
        description="<Description>",
    )
    def <app_name>_view() -> str:
        html_path = pathlib.Path(__file__).parent / "<app_name>_view.html"
        return html_path.read_text(encoding="utf-8")
```

Then call `add_<app_name>(mcp)` inside the `run()` function at the bottom of `server.py`.

---

## 3. Build and deploy

```bash
# In mcp-apps/<app-name>/
npm run build
# → tsc --noEmit && tsc -p tsconfig.server.json && INPUT=mcp-app.html vite build
# → produces dist/mcp-app.html (single-file bundle)

cp dist/mcp-app.html ../../pagerduty_mcp/<app_snake>_view.html
```

`emptyOutDir: false` in `vite.config.ts` preserves `dist/server.js` + `dist/main.js` from `tsc`.

---

## 4. Mock data (`dev:mock`)

Run the app in a browser without any MCP connection:

```bash
npm run dev:mock   # VITE_MOCK=true vite → http://localhost:517x/mcp-app.html
```

**`src/mock.ts`** — export data typed to your interfaces:
```ts
import type { MyData } from "./api";
export const MOCK_MY_DATA: MyData = { /* realistic values */ };
```

**`src/api.ts`** — early-return mock branch in each exported function:
```ts
const MOCK_MODE = import.meta.env.VITE_MOCK === "true";

export async function fetchData(app: App, ...): Promise<MyData> {
  if (MOCK_MODE) {
    const { MOCK_MY_DATA } = await import("./mock");
    return MOCK_MY_DATA;
  }
  // real callServerTool calls below
}
```

**`src/mcp-app.tsx`** — bypass `app` null guard in mock mode:
```ts
const mockMode = import.meta.env.VITE_MOCK === "true";
// change:  if (!app) return;
// to:      if (!app && !mockMode) return;
// and pass: app ?? ({} as App)   to all API calls
```

---

## 5. Testing with Playwright

Copy `.claude/skills/create-pagerduty-mcp-app/pw-test.template.mjs` to `mcp-apps/<app-name>/pw-test.spec.mjs` and fill in the selectors and interaction test.

```bash
# Terminal 1 — start mock server
npm run dev:mock

# Terminal 2 — run tests (uses PORT env var)
npm run test
```

**Visual checklist before deploying the bundle:**
- [ ] Initial view renders — no blank screen, no JS error overlay
- [ ] Mock data visible — tables/cards populated, not showing "no data"
- [ ] Last row in any CSS grid not collapsed (check visually — narrow text = bad)
- [ ] Multi-step flow works — click a row/button, verify next view loads correctly
- [ ] Dark mode — request URL `?theme=dark` and check text contrast

---

## 6. Gotchas checklist

1. **FastMCP arg wrapping** — always wrap under the Python parameter name.
   Look up the function signature: `def get_data(request: GetDataRequest)` → call with `{ request: { filters: {...} } }`.
   Wrong: `{ filters: {...} }` — silently returns empty data.

2. **CSS grid text collapse** — every direct grid child that contains text needs:
   ```css
   min-width: 0;
   width: 100%;
   ```
   Without it, text stacks vertically at near-zero width (especially the last item).

3. **`display: none` shifts grid columns** — removing an element from layout moves subsequent children.
   Use `visibility: hidden` to hide without disturbing column positions.

4. **`mime_type` must be `"text/html;profile=mcp-app"`** — plain `"text/html"` prevents VS Code from rendering the resource as an MCP App panel.

5. **URI must match exactly** — `resourceUri` in `server.ts` `_meta`, the URI in `registerAppResource`, and the URI in `@mcp_instance.resource()` must be byte-for-byte identical.

6. **`import.meta.dirname` in compiled ESM resolves to `dist/`** — `const DIST_DIR = import.meta.dirname` is correct in `server.ts`; do not add an extra `dist/` segment when reading `mcp-app.html`.

7. **Mock key matching** — use `.toLowerCase().includes(keyword)`, not `.slice(0, N)`. Short slices produce false negatives (e.g. `"MTTA & M"` never matches query text).
